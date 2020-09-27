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
from flask import request, send_from_directory, jsonify
from PIL import Image
import threading
from flask import current_app

from flask import Blueprint
search_blueprint = Blueprint('search_blueprint', __name__)

# flask initialisation and configuration (see config.py)

from crocodl.utils.log_utils import createLogger
from crocodl.image.web.searcher import Searcher

class SearchBlueprint(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("search")

    instance = Searcher()

    ####################################################################################################################
    # Main end points, invoked from index.html
    #

    @staticmethod
    @search_blueprint.route('/configuration.json', methods=['GET'])
    def get_configuration():
        return jsonify(SearchBlueprint.instance.get_configuration())

    @staticmethod
    @search_blueprint.route('/images_upload/<path:path>', methods=['POST'])
    def add_images(path):
        return jsonify(SearchBlueprint.instance.add_images(path,request.data))

    @staticmethod
    @search_blueprint.route('/image_upload/<path:path>', methods=['POST'])
    def upload_image(path):
        return jsonify(SearchBlueprint.instance.upload_image(path,request.data))

    @staticmethod
    @search_blueprint.route('/score_image/<path:path>', methods=['GET'])
    def send_scoreimage(path):
        (image_dir,path) = SearchBlueprint.instance.send_scoreimage(path)
        return send_from_directory(image_dir, path)

    @staticmethod
    @search_blueprint.route('/database/<path:path>', methods=['GET'])
    def send_database(path):
        (imagestore_dir, imagestore_filename) = SearchBlueprint.instance.send_database(path)
        return send_from_directory(imagestore_dir, imagestore_filename)

    @staticmethod
    @search_blueprint.route('/search_image', methods=['POST'])
    def search_image():
        return jsonify(SearchBlueprint.instance.search_image())

    @staticmethod
    @search_blueprint.route('/upload_database/<path:path>', methods=['POST'])
    def upload_database(path):
        return jsonify(SearchBlueprint.instance.upload_database(path,request.data))

    @staticmethod
    @search_blueprint.route('/create_database', methods=['POST'])
    def create_database():
        return jsonify(SearchBlueprint.instance.create_database(request.json))

    @staticmethod
    @search_blueprint.route('/status', methods=['GET'])
    def status():
        return jsonify(SearchBlueprint.instance.status())

    @staticmethod
    @search_blueprint.route('/view_code', methods=['GET'])
    def send_code():
        return SearchBlueprint.instance.send_code()


