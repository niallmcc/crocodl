# Copyright 2020 Niall McCarroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
import shutil
from flask import Flask, request, send_from_directory, jsonify
from PIL import Image
import threading

# flask initialisation and configuration (see config.py)
app = Flask(__name__)
app.config.from_object('config.Config')

from crocodl.utils.logutils import createLogger
from crocodl.image.web.data_utils import unpack_data
from crocodl.image.embedding.embedding_model import EmbeddingModel
from crocodl.image.embedding.image_store import ImageStore
from crocodl.image.utils.image_utils import ImageUtils
from crocodl.image.model_factories.factory import Factory
from crocodl.image.model_factories.capability import Capability

global embedding_model
embedding_model = None

global database_info
database_info = ""
image_path = ""
search_results= []
training = False
searching = False
train_progress = ""
search_progress = ""
search_image_url = ""
imagestore_path = ""
imagestore_url = ""

latest_train_path = ""
latest_train_image = ""

class TrainingThread(threading.Thread):

    def __init__(self,data_dir):
        super(TrainingThread,self).__init__(target=self)
        self.data_dir = data_dir

    def run(self):
        global embedding_model
        global training
        training = True
        embedding_model.train(self.data_dir, lambda s,p,i:self.progress_cb(s,p,i))
        training = False
        self.update_db_info()

    def progress_cb(self,progress,latest_path,latest_image):
        global train_progress, latest_train_path, latest_train_image, database_info
        train_progress = progress
        latest_train_path = latest_path
        latest_train_image = latest_image
        self.update_db_info()

    def update_db_info(self):
        global database_info
        database_info = "%s (%d images)" % (embedding_model.getArchitecture(), len(embedding_model))


class SearchThread(threading.Thread):

    def __init__(self, image_path):
        super(SearchThread, self).__init__(target=self)
        self.image_path = image_path

    def run(self):
        global embedding_model
        global searching
        searching = True
        global search_results
        search_results = []
        image = Image.open(self.image_path)
        matches = embedding_model.search(image, lambda s: self.progress_cb(s))
        for (path, similarity, bestimage) in matches:
            filename = os.path.split(path)[1]
            search_results.append({"filename": filename, "similarity": similarity, "image": ImageUtils.ImageToDataUri(bestimage)})
        searching = False

    def progress_cb(self, progress):
        global search_progress
        search_progress = progress

class App(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("app")

    ####################################################################################################################
    # Main end points, invoked from train.html
    #

    @staticmethod
    @app.route('/configuration.json', methods=['GET'])
    def get_configuration():
        return jsonify({"architectures": Factory.getAvailableArchitectures(Capability.feature_extraction)})

    @staticmethod
    @app.route('/images_upload/<path:path>', methods=['POST'])
    def add_images(path):
        global training
        if not training:
            global train_progress
            train_progress = "Adding images"
            upload_dir = os.path.join(app.config["WORKSPACE_DIR"], "upload")
            if os.path.isdir(upload_dir):
                shutil.rmtree(upload_dir)
            os.makedirs(upload_dir)

            global image_path
            zip_path = os.path.join(upload_dir, path)
            open(zip_path, "wb").write(request.data)

            data_dir = os.path.join(app.config["WORKSPACE_DIR"], "data")
            if os.path.isdir(data_dir):
                shutil.rmtree(data_dir)
            os.makedirs(data_dir)

            unpack_data(zip_path, data_dir)
            tt = TrainingThread(data_dir)
            tt.start()

        return jsonify({})

    @staticmethod
    @app.route('/image_upload/<path:path>', methods=['POST'])
    def upload_image(path):
        image_dir = os.path.join(app.config["WORKSPACE_DIR"], "image")
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.makedirs(image_dir)

        global image_path, search_image_url
        image_path = os.path.join(image_dir, path)
        open(image_path, "wb").write(request.data)
        search_image_url = "/score_image/"+path
        return jsonify({})

    @staticmethod
    @app.route('/score_image/<path:path>', methods=['GET'])
    def send_scoreimage(path):
        image_dir = os.path.join(app.config["WORKSPACE_DIR"], "image")
        return send_from_directory(image_dir, path)

    @staticmethod
    @app.route('/database/<path:path>', methods=['GET'])
    def send_database(path):
        imagestore_dir = os.path.split(imagestore_path)[0]
        imagestore_filename = os.path.split(imagestore_path)[1]
        return send_from_directory(imagestore_dir, imagestore_filename)

    @staticmethod
    @app.route('/search_image', methods=['POST'])
    def search_image():
        global search_progress
        search_progress = "Starting search..."
        global searching
        if not searching:
            st = SearchThread(image_path)
            st.start()
        return jsonify({})

    @staticmethod
    @app.route('/upload_database/<path:path>', methods=['POST'])
    def upload_database(path):
        parent_dir = os.path.join(app.config["WORKSPACE_DIR"], "image_store")
        if os.path.isdir(parent_dir):
            shutil.rmtree(parent_dir)
        os.makedirs(parent_dir)

        global imagestore_path
        imagestore_path = os.path.join(parent_dir, path)
        open(imagestore_path, "wb").write(request.data)

        global embedding_model
        imagestore = ImageStore(imagestore_path)
        embedding_model = EmbeddingModel(imagestore)

        global database_info
        database_info = "%s (%d images)" % (embedding_model.getArchitecture(), len(embedding_model))

        global imagestore_url
        imagestore_url = "database/"+path
        return jsonify({})

    @staticmethod
    @app.route('/create_database', methods=['POST'])
    def create_database():
        settings = request.json
        architecture = settings["architecture"]


        global embedding_model
        parent_dir = os.path.join(app.config["WORKSPACE_DIR"], "image_store")
        if os.path.isdir(parent_dir):
            shutil.rmtree(parent_dir)
        os.makedirs(parent_dir)

        global imagestore_path
        imagestore_path = os.path.join(parent_dir, "imagesearch.db")

        image_store = ImageStore(imagestore_path)
        image_store.setArchitecture(architecture)
        embedding_model = EmbeddingModel(image_store)

        global database_info
        database_info = "%s (%d images)" % (embedding_model.getArchitecture(), len(embedding_model))

        global imagestore_url
        imagestore_url = "database/imagesearch.db"
        return jsonify({})

    @staticmethod
    @app.route('/status', methods=['GET'])
    def status():
        global embedding_model, searching, training, search_progress, train_progress, search_results, image_path
        database_ready  = False
        search_ready = False
        if embedding_model != None:
            database_ready = True
            if not embedding_model.isEmpty():
                search_ready = True

        status = {
            "searching":searching,
            "training":training,
            "database_info":database_info,
            "image_uploaded": (image_path != ""),
            "database_ready": database_ready,
            "search_ready": search_ready
        }
        status["search_progress"] = search_progress
        status["train_progress"] = train_progress
        if training:
            status["train_image"] = latest_train_image
            status["train_file_name"] = latest_train_path
        if search_results:
            status["search_results"] = search_results

        global search_image_url
        if search_image_url:
            status["search_image_url"] = search_image_url

        global imagestore_url
        status["database_url"] = imagestore_url
        return jsonify(status)

    ####################################################################################################################
    # Service static files
    #

    @staticmethod
    @app.route('/', methods=['GET'])
    @app.route('/index.html', methods=['GET'])
    def fetch():
        """Serve the main page containing the form"""
        return send_from_directory('static','search.html')

    @staticmethod
    @app.route('/css/<path:path>',methods = ['GET'])
    def send_css(path):
        """serve CSS files"""
        return send_from_directory('static/css', path)

    @staticmethod
    @app.route('/js/<path:path>', methods=['GET'])
    def send_js(path):
        """serve JS files"""
        return send_from_directory('static/js', path)

    @staticmethod
    @app.route('/images/<path:path>', methods=['GET'])
    def send_images(path):
        """serve image files"""
        return send_from_directory('static/images', path)

    @staticmethod
    @app.route('/favicon.ico', methods=['GET'])
    def send_favicon():
        """serve favicon"""
        return send_from_directory('static/images', 'favicon.ico')

    @app.after_request
    def add_header(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        return r


if __name__ == '__main__':
    from crocodl.utils.web.browser import Browser

    parser = Browser.getArgParser()
    args = parser.parse_args()
    # start the service and try to open a new browser tab if required
    host = args.host
    port = Browser.getEphemeralPort() if args.port <= 0 else args.port
    if not args.noclient:
        Browser("http://%s:%d" % (host, port)).launch()

    app.run(host=host, port=port)




