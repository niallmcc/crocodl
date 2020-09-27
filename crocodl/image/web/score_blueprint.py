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
from flask import current_app

from crocodl.utils.log_utils import createLogger
from crocodl.runtime.h5_utils import read_metadata
from crocodl.image.model_registry.registry import Registry

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
        metadata = read_metadata(model_path)
        architecture = metadata["architecture"]
        factory = Registry.getModel(architecture)
        scorable = factory.getScorable()
        scorable.load(model_path)
        del metadata["metrics"]
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



