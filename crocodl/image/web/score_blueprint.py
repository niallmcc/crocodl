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
from flask import current_app

from crocodl.utils.logutils import createLogger
from crocodl.utils.h5utils import read_metadata
from crocodl.image.classifier.scorable import Scorable

from flask import Blueprint
score_blueprint = Blueprint('score_blueprint', __name__)

scorable = None
model_path = ""
image_path = ""

class ScoreBlueprint(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("app")

    ####################################################################################################################
    # Main end points, invoked from index.html
    #

    @staticmethod
    @score_blueprint.route('/score.json',methods = ['POST'])
    def score():
        global scorable, image
        result = scorable.score(image_path)
        return jsonify(result)

    @staticmethod
    @score_blueprint.route('/model_upload/<path:path>', methods=['POST'])
    def upload_model(path):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
        os.makedirs(model_dir)

        global model_path, scorable
        model_path = os.path.join(model_dir, path)
        open(model_path, "wb").write(request.data)

        scorable = Scorable()
        scorable.load(model_path)

        metadata = read_metadata(model_path)
        del metadata["epochs"]
        return jsonify(metadata)

    @staticmethod
    @score_blueprint.route('/image_upload/<path:path>', methods=['POST'])
    def upload_image(path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.makedirs(image_dir)

        global image_path
        image_path = os.path.join(image_dir, path)
        open(image_path, "wb").write(request.data)

        return jsonify("score_image/"+path)

    @staticmethod
    @score_blueprint.route('/score_image/<path:path>', methods=['GET'])
    def send_scoreimage(path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        return send_from_directory(image_dir, path)

    ####################################################################################################################
    # Service static files
    #

    # @staticmethod
    # @app.route('/', methods=['GET'])
    # @app.route('/index.html', methods=['GET'])
    # def fetch():
    #     """Serve the main page containing the form"""
    #     return send_from_directory('static','index.html')
    #
    # @staticmethod
    # @app.route('/css/<path:path>',methods = ['GET'])
    # def send_css(path):
    #     """serve CSS files"""
    #     return send_from_directory('static/css', path)
    #
    # @staticmethod
    # @app.route('/js/<path:path>', methods=['GET'])
    # def send_js(path):
    #     """serve JS files"""
    #     return send_from_directory('static/js', path)
    #
    # @staticmethod
    # @app.route('/images/<path:path>', methods=['GET'])
    # def send_images(path):
    #     """serve image files"""
    #     return send_from_directory('static/images', path)
    #
    # @staticmethod
    # @app.route('/favicon.ico', methods=['GET'])
    # def send_favicon():
    #     """serve favicon"""
    #     return send_from_directory('static/images', 'favicon.ico')
    #
    # @app.after_request
    # def add_header(r):
    #     r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    #     r.headers["Pragma"] = "no-cache"
    #     r.headers["Expires"] = "0"
    #     return r





