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

# flask initialisation and configuration (see config.py)
app = Flask(__name__)
app.config.from_object('config.Config')

from crocodl.utils.logutils import createLogger
from crocodl.utils.h5utils import read_metadata
from crocodl.image.web.style_blueprint import blueprint as style_blueprint
from crocodl.image.classifier.scorable import Scorable

scorable = None
model_path = ""
image_path = ""

app.register_blueprint(style_blueprint,url_prefix="/style_transfer")

import json

class App(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("app")


    ####################################################################################################################
    # Service static files
    #

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

    @staticmethod
    @app.route('/<path:path>', methods=['GET'])
    def fetch(path):
        """Serve the main page containing the form"""
        return send_from_directory('static/html', path)

    @staticmethod
    @app.route('/', methods=['GET'])
    def index():
        """Serve the main page containing the form"""
        return send_from_directory('static/html', 'index.html')


    @app.after_request
    def add_header(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        return r


if __name__ == '__main__':
    from crocodl.utils.web.browser import Browser

    args = Browser.getArgParser().parse_args()
    # start the service and try to open a new browser tab if required
    host = args.host
    port = Browser.getEphemeralPort() if args.port <= 0 else args.port
    if not args.noclient:
        Browser("http://%s:%d/style_transfer/index.html" % (host, port)).launch()
    app.run(host=host, port=port)




