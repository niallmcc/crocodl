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

from flask import request, send_from_directory, jsonify
from crocodl.image.web.scorer import AutoencoderScorer

from flask import Blueprint
score_autoencoder_blueprint = Blueprint('score_autoencoder_blueprint', __name__)

class ScoreAutoencoderBlueprint(object):
    """
    Define the routes and handlers for the web service
    """

    instance = AutoencoderScorer()

    ####################################################################################################################
    # Main end points, invoked from index.html
    #

    @staticmethod
    @score_autoencoder_blueprint.route('/score.json',methods = ['POST'])
    def score():
        return jsonify(ScoreAutoencoderBlueprint.instance.score())

    @staticmethod
    @score_autoencoder_blueprint.route('/model_upload/<path:path>', methods=['POST'])
    def upload_model(path):
        return jsonify(ScoreAutoencoderBlueprint.instance.upload_model(path,request.data))

    @staticmethod
    @score_autoencoder_blueprint.route('/image_upload/<path:path>', methods=['POST'])
    def upload_image(path):
        return jsonify(ScoreAutoencoderBlueprint.instance.upload_image(path,request.data))

    @staticmethod
    @score_autoencoder_blueprint.route('/score_image/<path:path>', methods=['GET'])
    def send_scoreimage(path):
        (image_dir, path) = ScoreAutoencoderBlueprint.instance.send_scoreimage(path)
        return send_from_directory(image_dir, path)

    @staticmethod
    @score_autoencoder_blueprint.route('/view_score_code', methods=['GET'])
    def send_score_code():
        return ScoreAutoencoderBlueprint.instance.send_score_code()

