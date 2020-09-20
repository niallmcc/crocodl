from .trainer import Trainer

from flask import Blueprint
from flask import request, send_from_directory, jsonify
train_classifier_blueprint = Blueprint('train_classifier_blueprint', __name__)

class ClassifierTrainer(Trainer):
    pass

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
    @train_classifier_blueprint.route('/training_chart.html', methods=['GET'])
    def get_training_chart():
        return TrainClassifierRouter.instance.get_training_chart()

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