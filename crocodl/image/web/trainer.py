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
import json

from flask import current_app

from crocodl.utils.logutils import createLogger
from crocodl.image.model_factories.factory import Factory
from crocodl.image.model_factories.capability import Capability
from crocodl.image.web.data_utils import unpack_data, locate_testtrain_subdir, get_classes
from crocodl.utils.web.code_formatter import CodeFormatter
from crocodl.utils.h5utils import read_metadata
from crocodl.image.classifier.trainable import Trainable as TrainableClassifier
from crocodl.image.autoencoder.trainable import Trainable as TrainableAutoEncoder
from crocodl.image.web.chart_utils import ChartUtils


class TrainingThread(threading.Thread):

    def __init__(self,trainer,foldername,trainable,updateStats,epochs=5,batchSize=16,onCompletion=None,onBatch=None):
        super(TrainingThread,self).__init__(target=self)
        self.trainer = trainer
        self.foldername = foldername
        self.updateStats = updateStats
        self.epochs=epochs
        self.batchSize = batchSize
        self.onCompletion=onCompletion
        self.onBatch=onBatch
        self.trainable = trainable

    def run(self):
        training_folder = os.path.join(self.foldername, "train")
        testing_folder = os.path.join(self.foldername, "test")
        self.trainable.train(self.foldername,training_folder,testing_folder,epoch_callback=lambda epoch,metrics:self.progress_cb(epoch,metrics),epochs=self.epochs,batch_size=self.batchSize,completion_callback=self.onCompletion,batch_callback=self.onBatch)

    def progress_cb(self,epoch,metrics):
        if self.updateStats:
            self.updateStats(epoch,metrics)


class Trainer(object):

    """
    Define the routes and handlers for the web service
    """

    def __init__(self):
        self.train_classes = []
        self.test_classes = []

        self.trainable = None
        self.model_path = ""
        self.data_folder = ""
        self.data_info = None

        self.model_details = {}
        self.model_filename = ""
        self.model_url = ""

        self.architecture = ""
        self.architectures = []
        self.create_or_update = "create"
        self.batch_size = 16

        self.chart_html = ""
        self.chart_type = "loss"
        if self.chart_type == "accuracy":
            self.chart_html = ChartUtils.createAccuracyChart([], 5)
        else:
            self.chart_html = ChartUtils.createLossChart([], 5)
        self.chart_types = ["accuracy", "loss"]

        self.training = False
        self.progress = 0.0

        self.current_start_epoch = 0  # start epoch of the current training
        self.current_nr_epochs = 5  # number of epochs in current training
        self.current_epoch = 0  # number of completed epochs in current training
        self.current_batch = 0  # number of completed batches in current epoch

    logger = createLogger("train_app")

    def updateTrainingProgress(self,epoch,metrics):
        self.progress = epoch/self.current_nr_epochs
        self.current_epoch = epoch
        self.metrics = metrics
        self.updateChart(metrics,epoch)

    def updateTrainingBatch(self,batch, metrics):
        self.current_batch = batch
        self.metrics = metrics

    def setTrainingCompleted(self):
        self.progress = 1.0
        self.training = False
        self.current_start_epoch = len(self.trainable.getEpochs())

    def submit(self):
        self.current_epoch = 0

        if self.create_or_update == "create":
            model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
            if os.path.isdir(model_dir):
                shutil.rmtree(model_dir)
            os.makedirs(model_dir)

            self.model_path = os.path.join(model_dir, "model.h5")
            self.current_start_epoch = 0
            self.updateChart([], self.current_nr_epochs)

            self.model_details = self.architecture
            self.model_url = "models/model.h5"
            self.model_filename = "model.h5"
            if len(self.train_classes) > 1:
                self.trainable = TrainableClassifier()
                self.trainable.createEmpty(self.model_path, self.train_classes, {TrainableClassifier.ARCHITECTURE: self.architecture})
            else:
                self.trainable = TrainableAutoEncoder()
                self.trainable.createEmpty(self.model_path, self.train_classes, {TrainableAutoEncoder.ARCHITECTURE: self.architecture})

        else:
            if self.trainable == None:
                return {"error":"No model loaded"}

        self.training_thread = TrainingThread(
            self,
            self.data_folder,
            self.trainable,
            lambda epoch,metrics: self.updateTrainingProgress(epoch,metrics),
            epochs=self.current_nr_epochs,
            batchSize=self.batch_size,
            onCompletion=lambda : self.setTrainingCompleted(),
            onBatch=lambda batch,metrics: self.updateTrainingBatch(batch,metrics))

        self.training = True
        self.training_thread.start()
        return {}

    def get_status(self):
        return {
            "progress":self.progress,
            "training":self.training,
            "epoch":self.current_start_epoch+self.current_epoch,
            "batch":self.current_batch,
            "data_info":self.data_info,
            "model_details":self.model_details,
            "model_filename":self.model_filename,
            "model_url":self.model_url,
            "batch_size":self.batch_size,
            "nr_epochs":self.current_nr_epochs,
            "chart_type":self.chart_type,
            "chart_types":self.chart_types,
            "architectures":self.architectures,
            "create_or_update":self.create_or_update,
            "model_ready": (self.create_or_update == "create" or self.model_filename != "")
        }

    def get_training_chart(self):
        return self.chart_html

    def download_model(self,path):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        return model_dir


    def upload_data(self,path,data):
        upload_dir = os.path.join(current_app.config["WORKSPACE_DIR"],"upload")
        if os.path.isdir(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir)

        upload_path = os.path.join(upload_dir,path)
        data_dir = os.path.join(current_app.config["WORKSPACE_DIR"],"data")
        if os.path.isdir(data_dir):
            shutil.rmtree(data_dir)
        os.makedirs(data_dir)

        open(upload_path,"wb").write(data)
        unpack_data(upload_path,data_dir)

        (train_dir,test_dir,parent_dir) = locate_testtrain_subdir(data_dir)

        self.data_folder=parent_dir

        if train_dir:
            self.train_classes = get_classes(train_dir)
        if test_dir:
            self.test_classes = get_classes(test_dir)

        print("training classes: "+json.dumps(self.train_classes))
        print("test classes: " + json.dumps(self.test_classes))

        self.data_info = {"classes": self.train_classes}

        if len(self.train_classes) > 1:
            self.architectures = Factory.getAvailableArchitectures(Capability.classification)
        else:
            self.architectures = Factory.getAvailableArchitectures(Capability.autoencoder)


        if len(self.train_classes) > 1:
            self.chart_types = ["accuracy","loss"]
        else:
            self.chart_types = ["loss"]
            self.chart_type = "loss"

        return {}


    def update_training_settings(self,settings):
        self.current_nr_epochs = settings["nr_epochs"]
        self.batch_size = settings["batch_size"]
        self.architecture = settings["architecture"]
        previous_create_or_update = self.create_or_update
        self.create_or_update = settings["create_or_update"]
        self.epochs = [] if not self.trainable else self.trainable.getEpochs()

        if previous_create_or_update != self.create_or_update:
            self.model_details = ""
            self.model_url = ""
            self.model_filename = ""
            # should maybe delete uploaded model?
        if self.create_or_update == "create":
            self.model_details = {"architecture":self.architecture}
            self.model_url = ""
            self.model_filename = ""

        self.updateChart(self.epochs, self.current_start_epoch+self.current_nr_epochs)
        return {}

    def update_chart_type(self,settings):
        self.chart_type = settings["chart_type"]
        self.epochs = [] if not self.trainable else self.trainable.getEpochs()
        self.updateChart(self.epochs, self.current_start_epoch + self.current_nr_epochs)
        return {}


    def upload_model(self,path,data):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
        os.makedirs(model_dir)

        self.model_path = os.path.join(model_dir, path)
        open(self.model_path, "wb").write(data)

        if len(self.train_classes) > 1:
            self.trainable = TrainableClassifier()
        else:
            self.trainable = TrainableAutoEncoder()
        self.trainable.open(self.model_path)
        self.current_start_epoch = len(self.trainable.getEpochs())

        self.updateChart(self.trainable.getEpochs(), self.current_start_epoch + self.current_nr_epochs)

        metadata = read_metadata(self.model_path)
        del metadata["epochs"]

        self.model_details = metadata
        self.model_url = "models/"+path
        self.model_filename = path
        return {}


    def send_code(self):
        if self.architecture and self.train_classes:
            cf = CodeFormatter()
            if len(self.train_classes) != 1:
                html = cf.formatHTML(TrainableClassifier.getCode(self.architecture))
            else:
                html = cf.formatHTML(TrainableAutoEncoder.getCode(self.architecture))
            return html
        else:
            return "Select training data and model options to view training code"

    def updateChart(self,metrics,nr_epochs):
        if self.chart_type == "accuracy":
            self.chart_html = ChartUtils.createAccuracyChart(metrics, nr_epochs)
        else:
            self.chart_html = ChartUtils.createLossChart(metrics, nr_epochs)




