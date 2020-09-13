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
from crocodl.image.model_factories.factory import Factory

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
        factory = Factory.getFactory(architecture)
        scorable = factory.getScorable()
        scorable.load(model_path)
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



