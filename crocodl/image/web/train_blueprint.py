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
import threading
from flask import Flask, request, send_from_directory, jsonify
from flask import current_app

from flask import Blueprint
train_blueprint = Blueprint('train_blueprint', __name__)

from crocodl.utils.logutils import createLogger
from crocodl.image.model_factories.factory import Factory
from crocodl.image.model_factories.capability import Capability
from crocodl.image.web.data_utils import unpack_data, locate_testtrain_subdir, get_classes
from crocodl.utils.h5utils import read_metadata
from crocodl.image.classifier.trainable import Trainable
from crocodl.image.web.chart_utils import ChartUtils

train_classes = []
test_classes = []

trainable = None
model_path = ""
data_folder = ""

batch_size = 0

accuracy_chart_html = ""
svg = ChartUtils.createAccuracyChart([], 5)
accuracy_chart_html = str(svg, "utf-8")

training = False
progress = 0.0

current_start_epoch = 0 # start epoch of the current training
current_nr_epochs = 0   # number of epochs in current training
current_epoch = 0       # number of completed epochs in current training
current_batch = 0       # number of completed batches in current epoch

import json

class TrainingThread(threading.Thread):

    def __init__(self,foldername,trainable,updateStats,epochs=5,batchSize=16,onCompletion=None,onBatch=None):
        super(TrainingThread,self).__init__(target=self)
        self.foldername = foldername
        self.updateStats = updateStats
        self.epochs=epochs
        self.batchSize = batchSize
        self.onCompletion=onCompletion
        self.onBatch=onBatch
        self.trainable = trainable

    def run(self):
        self.trainable.train(self.foldername,lambda epoch,metrics:self.progress_cb(epoch,metrics),epochs=self.epochs,batchSize=self.batchSize,completion_callback=self.onCompletion,batch_callback=self.onBatch)
        self.trainable.saveModel()

    def progress_cb(self,epoch,metrics):
        svg = ChartUtils.createAccuracyChart(trainable.getEpochs(), current_start_epoch + current_nr_epochs)
        global accuracy_chart_html
        accuracy_chart_html= str(svg,"utf-8")
        if self.updateStats:
            self.updateStats(epoch,metrics)


class TrainBlueprint(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("train_app")

    @staticmethod
    def updateTrainingProgress(epoch,metrics):
        global progress, current_epoch, current_nr_epochs
        progress = epoch/current_nr_epochs
        current_epoch = epoch

    @staticmethod
    def updateTrainingBatch(batch, metrics):
        global current_batch
        current_batch = batch

    @staticmethod
    def setTrainingCompleted():
        global training, progress
        progress = 1.0
        training = False
        global current_start_epoch
        current_start_epoch = len(trainable.getEpochs())

    ####################################################################################################################
    # Main end points, invoked from index.html
    #

    @staticmethod
    @train_blueprint.route('/launch_training.json',methods = ['POST'])
    def submit():
        global trainable, training_thread, data_folder, training
        global current_epoch, current_nr_epochs, batch_size

        current_epoch = 0

        training_thread = TrainingThread(
            data_folder,
            trainable,
            lambda epoch,metrics: TrainBlueprint.updateTrainingProgress(epoch,metrics),
            epochs=current_nr_epochs,
            batchSize=batch_size,
            onCompletion=lambda : TrainBlueprint.setTrainingCompleted(),
            onBatch=lambda batch,metrics: TrainBlueprint.updateTrainingBatch(batch,metrics))

        training = True
        training_thread.start()
        return jsonify({"training":True,"progress":0})

    @staticmethod
    @train_blueprint.route('/training_progress.json', methods=['GET'])
    def get_progress():
        return jsonify({"progress":progress, "training":training, "epoch":current_start_epoch+current_epoch, "batch":current_batch})

    @staticmethod
    @train_blueprint.route('/training_accuracy_chart.html', methods=['GET'])
    def get_accuracy_chart():
        return accuracy_chart_html

    @staticmethod
    @train_blueprint.route('/models/<path:path>', methods=['GET'])
    def download_model(path):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        return send_from_directory(model_dir, path)

    @staticmethod
    @train_blueprint.route('/configuration.json', methods=['GET'])
    def get_configuration():
        return jsonify({"architectures":Factory.getAvailableArchitectures(Capability.classification)})

    @staticmethod
    @train_blueprint.route('/data_upload/<path:path>', methods=['POST'])
    def upload_data(path):
        upload_dir = os.path.join(current_app.config["WORKSPACE_DIR"],"upload")
        if os.path.isdir(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir)

        upload_path = os.path.join(upload_dir,path)
        data_dir = os.path.join(current_app.config["WORKSPACE_DIR"],"data")
        if os.path.isdir(data_dir):
            shutil.rmtree(data_dir)
        os.makedirs(data_dir)

        open(upload_path,"wb").write(request.data)
        unpack_data(upload_path,data_dir)

        (train_dir,test_dir,parent_dir) = locate_testtrain_subdir(data_dir)
        global data_folder
        data_folder=parent_dir
        global train_classes, test_classes
        if train_dir:
            train_classes = get_classes(train_dir)
        if test_dir:
            test_classes = get_classes(test_dir)

        print("training classes: "+json.dumps(train_classes))
        print("test classes: " + json.dumps(test_classes))

        return jsonify({"classes":train_classes})

    @staticmethod
    @train_blueprint.route('/update_training_settings.json', methods=['POST'])
    def update_training_settings():
        settings = request.json
        global current_nr_epochs, batch_size
        current_nr_epochs = settings["nr_epochs"]
        batch_size = settings["batch_size"]
        epochs = [] if not trainable else trainable.getEpochs()

        svg = ChartUtils.createAccuracyChart(epochs, current_start_epoch+current_nr_epochs)
        global accuracy_chart_html
        accuracy_chart_html = str(svg, "utf-8")
        return jsonify({})

    @staticmethod
    @train_blueprint.route('/create_model.json', methods=['POST'])
    def create_model():
        settings = request.json

        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
        os.makedirs(model_dir)

        global model_path, trainable, current_start_epoch
        model_path = os.path.join(model_dir, "model.h5")

        trainable = Trainable()
        trainable.createEmpty(model_path,train_classes,settings)
        trainable.saveModel()

        current_start_epoch = 0

        svg = ChartUtils.createAccuracyChart([], current_nr_epochs)
        global accuracy_chart_html
        accuracy_chart_html = str(svg, "utf-8")

        metadata = read_metadata(model_path)
        del metadata["epochs"]
        return jsonify({"model_details":metadata,"url":"models/model.h5","filename":"model.h5"})

    @staticmethod
    @train_blueprint.route('/model_upload/<path:path>', methods=['POST'])
    def upload_model(path):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
        os.makedirs(model_dir)

        global model_path, trainable, current_start_epoch
        model_path = os.path.join(model_dir, path)
        open(model_path, "wb").write(request.data)

        trainable = Trainable()
        trainable.open(model_path)
        current_start_epoch = len(trainable.getEpochs())

        svg = ChartUtils.createAccuracyChart(trainable.getEpochs(), current_start_epoch + current_nr_epochs)
        global accuracy_chart_html
        accuracy_chart_html = str(svg, "utf-8")

        metadata = read_metadata(model_path)
        del metadata["epochs"]
        return jsonify({"model_details":metadata,"url":"models/"+path,"filename":path})

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






