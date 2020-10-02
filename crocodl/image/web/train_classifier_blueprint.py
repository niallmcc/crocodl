from .trainer import Trainer

from flask import Blueprint
from flask import request, send_from_directory, jsonify
train_classifier_blueprint = Blueprint('train_classifier_blueprint', __name__)

class ClassifierTrainer(Trainer):

    def getType(self):
        return "classifier"

class TrainClassifierRouter(object):

    instance = ClassifierTrainer()

    @staticmethod
    @train_classifier_blueprint.route('/launch_training.json',methods = ['POST'])
    def submit():
        return jsonify(TrainClassifierRouter.instance.submit())

    @staticmethod
    @train_classifier_blueprint.route('/status.json', methods=['GET'])
    def get_status():
        return jsonify(TrainClassifierRouter.instance.get_status())

    @staticmethod
    @train_classifier_blueprint.route('/training_report.html', methods=['GET'])
    def get_training_report():
        return TrainClassifierRouter.instance.get_training_report()

    @staticmethod
    @train_classifier_blueprint.route('/models/<path:path>', methods=['GET'])
    def download_model(path):
        model_dir = TrainClassifierRouter.instance.download_model(path)
        return send_from_directory(model_dir, path)

    @staticmethod
    @train_classifier_blueprint.route('/data_upload/<path:path>', methods=['POST'])
    def upload_data(path):
        return jsonify(TrainClassifierRouter.instance.upload_data(path,request.data))

    @staticmethod
    @train_classifier_blueprint.route('/update_training_settings.json', methods=['POST'])
    def update_training_settings():
        return jsonify(TrainClassifierRouter.instance.update_training_settings(request.json))

    @staticmethod
    @train_classifier_blueprint.route('/update_chart_type.json', methods=['POST'])
    def update_chart_type():
        return jsonify(TrainClassifierRouter.instance.update_chart_type(request.json))

    @staticmethod
    @train_classifier_blueprint.route('/model_upload/<path:path>', methods=['POST'])
    def upload_model(path):
        return jsonify(TrainClassifierRouter.instance.upload_model(path,request.data))

    @staticmethod
    @train_classifier_blueprint.route('/view_code', methods=['GET'])
    def send_code():
        return TrainClassifierRouter.instance.send_code()

    @staticmethod
    @train_classifier_blueprint.route('/score.json', methods=['POST'])
    def score():
        return jsonify(TrainClassifierRouter.instance.score())

    @staticmethod
    @train_classifier_blueprint.route('/image_upload/<path:path>', methods=['POST'])
    def upload_image(path):
        return jsonify(TrainClassifierRouter.instance.upload_image(path, request.data))

    @staticmethod
    @train_classifier_blueprint.route('/score_image/<path:path>', methods=['GET'])
    def send_scoreimage(path):
        (image_dir, path) = TrainClassifierRouter.instance.send_scoreimage(path)
        return send_from_directory(image_dir, path)

    @staticmethod
    @train_classifier_blueprint.route('/view_score_code', methods=['GET'])
    def send_score_code():
        return TrainClassifierRouter.instance.send_score_code()

    @staticmethod
    @train_classifier_blueprint.route('/cancel', methods=['POST'])
    def cancel():
        return jsonify({"cancelled":TrainClassifierRouter.instance.cancel()})