#    Copyright (C) 2020 crocoDL developers
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os.path
import shutil
import threading
from flask import current_app

# flask initialisation and configuration (see config.py)

from crocodl.utils.log_utils import createLogger
from crocodl.image.web.data_utils import unpack_data
from crocodl.image.search.searchable import Searchable
from crocodl.runtime.image_store import ImageStore
from crocodl.utils.web.code_formatter import CodeFormatter
from crocodl.image.model_registry.registry import Registry
from crocodl.image.model_registry.capability import Capability



class LoadThread(threading.Thread):

    def __init__(self,searcher,data_dir):
        super(LoadThread,self).__init__(target=self)
        self.searcher = searcher
        self.data_dir = data_dir

    def run(self):
        self.searcher.loading = True
        self.searcher.get_searchable().load(self.data_dir, lambda s,p,i,ds:self.progress_cb(s,p,i,ds))
        self.searcher.loading = False
        self.searcher.load_complete()

    def progress_cb(self,progress,latest_path,latest_image,database_size):
        self.searcher.load_progress = progress
        self.searcher.latest_load_path = latest_path
        self.searcher.latest_load_image = latest_image
        self.searcher.set_database_size(database_size)

    def update_db_info(self):
        self.searcher.database_info = "%s (%d images)" % (self.searcher.architecture, -1)


class SearchThread(threading.Thread):

    def __init__(self, searcher,image_path):
        super(SearchThread, self).__init__(target=self)
        self.searcher = searcher
        self.image_path = image_path

    def run(self):
        self.searcher.searching = True
        self.searcher.search_results = []
        matches = self.searcher.get_searchable().search(self.image_path)
        for (path, similarity, bestimage) in matches:
            filename = os.path.split(path)[1]
            self.searcher.search_results.append({"filename": filename, "similarity": similarity, "image": bestimage})
        self.searcher.searching = False

class Searcher(object):

    def __init__(self):
        self.database_info = ""
        self.image_path = ""
        self.search_results= []
        self.loading = False
        self.searching = False
        self.load_progress = ""
        self.search_progress = ""
        self.search_image_url = ""
        self.imagestore_path = ""
        self.imagestore_url = ""
        self.searchable = None
        self.architecture = ""
        self.latest_load_path = ""
        self.latest_load_image = ""
        self.database_ready = False
        self.search_dir = ""
        self.database_size = 0


    logger = createLogger("searcher")

    ####################################################################################################################
    # Main end points, invoked from index.html
    #

    def get_searchable(self):
        if not self.searchable:

            if os.path.isdir(self.search_dir):
                shutil.rmtree(self.search_dir)
            os.makedirs(self.search_dir)
            self.search_folder = self.search_dir
            self.model_details = self.architecture
            self.searchable = Searchable(self.imagestore_path,self.architecture,self.search_folder)
        return self.searchable

    def get_configuration(self):
        self.search_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "search")
        return {"architectures": Registry.getAvailableArchitectures(Capability.feature_extraction)}

    def add_images(self,path,data):
        self.get_searchable()
        if not self.loading:
            self.load_progress = "Adding images"
            upload_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "upload")
            if os.path.isdir(upload_dir):
                shutil.rmtree(upload_dir)
            os.makedirs(upload_dir)

            zip_path = os.path.join(upload_dir, path)
            open(zip_path, "wb").write(data)

            data_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "data")
            if os.path.isdir(data_dir):
                shutil.rmtree(data_dir)
            os.makedirs(data_dir)

            unpack_data(zip_path, data_dir)
            lt = LoadThread(self,data_dir)
            lt.start()

        return {}

    def upload_image(self,path,data):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.makedirs(image_dir)

        self.image_path = os.path.join(image_dir, path)
        open(self.image_path, "wb").write(data)
        self.search_image_url = "score_image/"+path
        return {}

    def send_scoreimage(self,path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        return (image_dir,path)

    def send_database(self,path):
        imagestore_dir = os.path.split(self.imagestore_path)[0]
        imagestore_filename = os.path.split(self.imagestore_path)[1]
        return (imagestore_dir, imagestore_filename)

    def search_image(self):
        self.get_searchable()
        self.search_progress = "Starting search..."
        if not self.searching:
            st = SearchThread(self,self.image_path)
            st.start()
        return {}

    def upload_database(self,path,data):
        parent_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image_store")
        if os.path.isdir(parent_dir):
            shutil.rmtree(parent_dir)
        os.makedirs(parent_dir)

        self.imagestore_path = os.path.join(parent_dir, path)
        open(self.imagestore_path, "wb").write(data)

        imagestore = ImageStore(self.imagestore_path)
        self.architecture = imagestore.getArchitecture()
        self.database_size = len(imagestore)
        self.database_info = self.refresh_database_info()
        self.imagestore_url = "database/"+path
        self.database_ready = True
        return {}

    def load_complete(self):
        imagestore = ImageStore(self.imagestore_path)
        self.database_size = len(imagestore)
        self.database_info = self.refresh_database_info()

    def create_database(self,settings):
        self.architecture = settings["architecture"]
        parent_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image_store")
        if os.path.isdir(parent_dir):
            shutil.rmtree(parent_dir)
        os.makedirs(parent_dir)

        self.imagestore_path = os.path.join(parent_dir, "imagesearch.db")

        image_store = ImageStore(self.imagestore_path)
        image_store.setArchitecture(self.architecture)
        self.database_size = len(image_store)
        self.database_info = self.refresh_database_info()
        self.database_ready = True
        self.imagestore_url = "database/imagesearch.db"
        return {}

    def status(self):
        search_ready = self.database_ready

        status = {
            "searching":self.searching,
            "loading":self.loading,
            "database_info":self.database_info,
            "image_uploaded": (self.image_path != ""),
            "database_ready": self.database_ready,
            "search_ready": search_ready
        }
        status["search_progress"] = self.search_progress
        status["load_progress"] = self.load_progress
        if self.loading:
            status["latest_load_image"] = self.latest_load_image
            status["latest_load_path"] = self.latest_load_path
        if self.search_results:
            status["search_results"] = self.search_results

        if self.search_image_url:
            status["search_image_url"] = self.search_image_url

        status["database_url"] = self.imagestore_url
        return status

    def send_code(self):
        if self.architecture:
            cf = CodeFormatter()
            return cf.formatHTML(Searchable.getCode(self.architecture))
        else:
            return "to view code, first create or upload database"

    def set_database_size(self,database_size):
        self.database_size = database_size
        self.refresh_database_info()

    def refresh_database_info(self):
        return "%s (%d images)" % (self.architecture, self.database_size)
