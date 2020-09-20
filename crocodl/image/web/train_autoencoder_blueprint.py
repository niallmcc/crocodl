from .trainer import Trainer

from flask import Blueprint
from flask import request, send_from_directory, jsonify
train_autoencoder_blueprint = Blueprint('train_autoencoder_blueprint', __name__)

class AutoencoderTrainer(Trainer):
    pass

class TrainAutoencoderRouter(object):

    instance = AutoencoderTrainer()

    @staticmethod
    @train_autoencoder_blueprint.route('/launch_training.json',methods = ['POST'])
    def submit():
        return jsonify(TrainAutoencoderRouter.instance.submit())

    @staticmethod
    @train_autoencoder_blueprint.route('/status.json', methods=['GET'])
    def get_status():
        return jsonify(TrainAutoencoderRouter.instance.get_status())

    @staticmethod
    @train_autoencoder_blueprint.route('/training_chart.html', methods=['GET'])
    def get_training_chart():
        return TrainAutoencoderRouter.instance.get_training_chart()

    @staticmethod
    @train_autoencoder_blueprint.route('/models/<path:path>', methods=['GET'])
    def download_model(path):
        model_dir = TrainAutoencoderRouter.instance.download_model(path)
        return send_from_directory(model_dir, path)

    @staticmethod
    @train_autoencoder_blueprint.route('/data_upload/<path:path>', methods=['POST'])
    def upload_data(path):
        return jsonify(TrainAutoencoderRouter.instance.upload_data(path, request.data))

    @staticmethod
    @train_autoencoder_blueprint.route('/update_training_settings.json', methods=['POST'])
    def update_training_settings():
        return jsonify(TrainAutoencoderRouter.instance.update_training_settings(request.json))

    @staticmethod
    @train_autoencoder_blueprint.route('/update_chart_type.json', methods=['POST'])
    def update_chart_type():
        return jsonify(TrainAutoencoderRouter.instance.update_chart_type(request.json))

    @staticmethod
    @train_autoencoder_blueprint.route('/model_upload/<path:path>', methods=['POST'])
    def upload_model(path):
        return jsonify(TrainAutoencoderRouter.instance.upload_model(path, request.data))

    @staticmethod
    @train_autoencoder_blueprint.route('/view_code', methods=['GET'])
    def send_code():
        return TrainAutoencoderRouter.instance.send_code()