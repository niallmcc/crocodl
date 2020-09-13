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
from crocodl.utils.web.code_formatter import CodeFormatter
from crocodl.utils.h5utils import read_metadata
from crocodl.image.classifier.trainable import Trainable as TrainableClassifier
from crocodl.image.autoencoder.trainable import Trainable as TrainableAutoEncoder
from crocodl.image.web.chart_utils import ChartUtils

train_classes = []
test_classes = []

trainable = None
model_path = ""
data_folder = ""
data_info = None

model_details = {}
model_filename = ""
model_url = ""

architecture = ""
architectures = []
create_or_update = "create"
batch_size = 16

chart_html = ""
chart_type = "loss"
if chart_type == "accuracy":
    chart_html = ChartUtils.createAccuracyChart([], 5)
else:
    chart_html = ChartUtils.createLossChart([], 5)
chart_types = ["accuracy","loss"]

training = False
progress = 0.0

current_start_epoch = 0 # start epoch of the current training
current_nr_epochs = 5   # number of epochs in current training
current_epoch = 0       # number of completed epochs in current training
current_batch = 0       # number of completed batches in current epoch

import json

def updateChart(logs,nr_epochs):
    global chart_html
    if chart_type == "accuracy":
        chart_html = ChartUtils.createAccuracyChart(logs, nr_epochs)
    else:
        chart_html = ChartUtils.createLossChart(logs, nr_epochs)


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
        self.logs = []

    def run(self):
        training_folder = os.path.join(self.foldername, "train")
        testing_folder = os.path.join(self.foldername, "test")
        self.trainable.train(self.foldername,training_folder,testing_folder,epoch_callback=lambda epoch,metrics:self.progress_cb(epoch,metrics),epochs=self.epochs,batch_size=self.batchSize,completion_callback=self.onCompletion,batch_callback=self.onBatch)

    def progress_cb(self,epoch,metrics):
        if isinstance(metrics,list):
            self.logs = metrics
        else:
            self.logs.append(metrics)
        updateChart(self.logs, current_start_epoch + current_nr_epochs)
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

        if create_or_update == "create":
            model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
            if os.path.isdir(model_dir):
                shutil.rmtree(model_dir)
            os.makedirs(model_dir)

            global model_path, trainable, current_start_epoch
            model_path = os.path.join(model_dir, "model.h5")
            current_start_epoch = 0
            updateChart([], current_nr_epochs)

            global model_details, model_url, model_filename
            model_details = architecture
            model_url = "models/model.h5"
            model_filename = "model.h5"
            if len(train_classes) > 1:
                trainable = TrainableClassifier()
                trainable.createEmpty(model_path, train_classes, {TrainableClassifier.ARCHITECTURE: architecture})
            else:
                trainable = TrainableAutoEncoder()
                trainable.createEmpty(model_path, train_classes, {TrainableAutoEncoder.ARCHITECTURE: architecture})

        else:
            if trainable == None:
                return jsonify({"error":"No model loaded"})

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
        return jsonify({})

    @staticmethod
    @train_blueprint.route('/status.json', methods=['GET'])
    def get_status():
        return jsonify({
            "progress":progress,
            "training":training,
            "epoch":current_start_epoch+current_epoch,
            "batch":current_batch,
            "data_info":data_info,
            "model_details":model_details,
            "model_filename":model_filename,
            "model_url":model_url,
            "batch_size":batch_size,
            "nr_epochs":current_nr_epochs,
            "chart_type":chart_type,
            "chart_types":chart_types,
            "architectures":architectures,
            "create_or_update":create_or_update,
            "model_ready": (create_or_update == "create" or model_filename != "")
        })

    @staticmethod
    @train_blueprint.route('/training_chart.html', methods=['GET'])
    def get_training_chart():
        return chart_html

    @staticmethod
    @train_blueprint.route('/models/<path:path>', methods=['GET'])
    def download_model(path):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        return send_from_directory(model_dir, path)

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
        global data_info
        data_info = {"classes": train_classes}
        global architectures
        if len(train_classes) > 1:
            architectures = Factory.getAvailableArchitectures(Capability.classification)
        else:
            architectures = Factory.getAvailableArchitectures(Capability.autoencoder)

        global chart_type, chart_types
        if len(train_classes) > 1:
            chart_types = ["accuracy","loss"]
        else:
            chart_types = ["loss"]
            chart_type = "loss"

        return jsonify({})

    @staticmethod
    @train_blueprint.route('/update_training_settings.json', methods=['POST'])
    def update_training_settings():
        settings = request.json
        print(json.dumps(settings))
        global current_nr_epochs, batch_size
        current_nr_epochs = settings["nr_epochs"]
        batch_size = settings["batch_size"]
        global architecture
        architecture = settings["architecture"]
        global create_or_update
        previous_create_or_update = create_or_update
        create_or_update = settings["create_or_update"]
        epochs = [] if not trainable else trainable.getEpochs()
        global model_details, model_url, model_filename
        if previous_create_or_update != create_or_update:
            model_details = ""
            model_url = ""
            model_filename = ""
            # should maybe delete uploaded model?
        if create_or_update == "create":
            model_details = {"architecture":architecture}
            model_url = ""
            model_filename = ""

        updateChart(epochs, current_start_epoch+current_nr_epochs)
        return jsonify({})

    @staticmethod
    @train_blueprint.route('/update_chart_type.json', methods=['POST'])
    def update_chart_type():
        settings = request.json
        global chart_type
        chart_type = settings["chart_type"]
        epochs = [] if not trainable else trainable.getEpochs()
        updateChart(epochs, current_start_epoch + current_nr_epochs)
        return jsonify({})


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

        if len(train_classes) > 1:
            trainable = TrainableClassifier()
        else:
            trainable = TrainableAutoEncoder()
        trainable.open(model_path)
        current_start_epoch = len(trainable.getEpochs())

        updateChart(trainable.getEpochs(), current_start_epoch + current_nr_epochs)

        metadata = read_metadata(model_path)
        del metadata["epochs"]
        global model_details, model_url, model_filename
        model_details = metadata
        model_url = "models/"+path
        model_filename = path
        return jsonify({})

    @staticmethod
    @train_blueprint.route('/view_code', methods=['GET'])
    def send_code():
        if architecture and train_classes:
            cf = CodeFormatter()
            if len(train_classes) != 1:
                html = cf.formatHTML(TrainableClassifier.getCode(architecture))
            else:
                html = cf.formatHTML(TrainableAutoEncoder.getCode(architecture))
            return html
        else:
            return "Select training data and model options to view training code"






