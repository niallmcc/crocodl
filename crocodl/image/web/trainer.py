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
import threading

from flask import current_app

from crocodl.utils.log_utils import createLogger
from crocodl.image.model_registry.registry import Registry
from crocodl.image.model_registry.capability import Capability
from crocodl.image.web.data_utils import unpack_data, get_classes
from crocodl.utils.web.code_formatter import CodeFormatter
from crocodl.runtime.h5_utils import read_metadata
from crocodl.image.classifier.trainable import Trainable as TrainableClassifier
from crocodl.image.autoencoder.trainable import Trainable as TrainableAutoEncoder
from crocodl.image.web.chart_utils import ChartUtils


class TrainingThread(threading.Thread):

    def __init__(self,trainer,model_folder,training_folder,testing_folder,trainable,onEpoch,epochs=5,batchSize=16,onCompletion=None,onBatch=None):
        super(TrainingThread,self).__init__(target=self)
        self.trainer = trainer
        self.model_folder = model_folder
        self.training_folder = training_folder
        self.testing_folder = testing_folder
        self.onEpoch = onEpoch
        self.epochs=epochs
        self.batchSize = batchSize
        self.onCompletion=onCompletion
        self.onBatch=onBatch
        self.trainable = trainable

    def run(self):
        self.trainable.train(self.model_folder,self.training_folder,self.testing_folder,epoch_callback=lambda epoch,metrics:self.progress_cb(epoch,metrics),epochs=self.epochs,batch_size=self.batchSize,completion_callback=self.onCompletion,batch_callback=self.onBatch)

    def progress_cb(self,epoch,metrics):
        if self.onEpoch:
            self.onEpoch(epoch,metrics)


class Trainer(object):

    """
    Define the routes and handlers for the web service
    """

    def __init__(self):
        self.train_classes = []
        self.test_classes = []

        self.trainable = None
        self.model_path = ""
        self.model_folder = ""
        self.training_folder = ""
        self.testing_folder = ""
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
        self.metrics = []

        self.current_nr_epochs = 5  # number of epochs in current training

        self.current_batch = 0  # number of completed batches in current epoch

    logger = createLogger("train_app")

    def updateTrainingProgress(self,epoch,metrics):
        self.progress = epoch/self.current_nr_epochs
        self.metrics = metrics
        self.updateChart(metrics)

    def updateTrainingBatch(self,batch):
        self.current_batch = batch

    def setTrainingCompleted(self):
        self.progress = 1.0
        self.training = False

    def submit(self):
        if self.trainable == None:
            model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
            if os.path.isdir(model_dir):
                shutil.rmtree(model_dir)
            os.makedirs(model_dir)
            self.model_folder = model_dir

            self.model_path = os.path.join(model_dir, "model.h5")
            self.updateChart([])

            self.model_details = self.architecture
            self.model_url = "models/model.h5"
            self.model_filename = "model.h5"
            if len(self.train_classes) > 1:
                self.trainable = TrainableClassifier()
                self.trainable.createEmpty(self.model_path, self.train_classes, {TrainableClassifier.ARCHITECTURE: self.architecture})
            else:
                self.trainable = TrainableAutoEncoder()
                self.trainable.createEmpty(self.model_path, self.train_classes, {TrainableAutoEncoder.ARCHITECTURE: self.architecture})

        self.training_thread = TrainingThread(
            self,
            self.model_folder,
            self.training_folder,
            self.testing_folder,
            self.trainable,
            onEpoch=lambda epoch,metrics: self.updateTrainingProgress(epoch,metrics),
            epochs=self.current_nr_epochs,
            batchSize=self.batch_size,
            onCompletion=lambda : self.setTrainingCompleted(),
            onBatch=lambda batch,epoch: self.updateTrainingBatch(batch))

        self.training = True
        self.training_thread.start()
        return {}

    def get_status(self):
        return {
            "progress":self.progress,
            "training":self.training,
            "epoch":1+len(self.metrics),
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
        partition = os.path.split(path)[0] # training or testing
        path = os.path.split(path)[1]

        upload_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "upload", partition)
        if os.path.isdir(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir)

        upload_path = os.path.join(upload_dir,path)
        partition_dir = os.path.join(current_app.config["WORKSPACE_DIR"],"data",partition)
        if os.path.isdir(partition_dir):
            shutil.rmtree(partition_dir)
        os.makedirs(partition_dir)

        open(upload_path,"wb").write(data)
        if self.getType() == "autoencoder":
            # for autoencoder, create an extra directory level to represent a dummy class
            unpack_dir = os.path.join(partition_dir, "auto")
            unpack_data(upload_path,unpack_dir)

        if partition == "training":
            self.training_folder = partition_dir
        if partition == "testing":
            self.testing_folder = partition_dir

        # FIXME check train and test classes are identical if both non-empty

        if self.getType() == "classifier":
            if partition == "training":
                self.train_classes = get_classes(partition_dir)
            elif partition == "testing":
                self.test_classes = get_classes(partition_dir)
            self.data_info = {"classes": self.train_classes if self.train_classes else self.test_classes}
            self.architectures = Registry.getAvailableArchitectures(Capability.classification)
            self.chart_types = ["accuracy", "loss"]

        elif self.getType() == "autoencoder":
            self.data_info = {}
            self.architectures = Registry.getAvailableArchitectures(Capability.autoencoder)
            self.chart_types = ["loss"]
            self.chart_type = "loss"

        return {}

    def update_training_settings(self,settings):
        self.current_nr_epochs = settings["nr_epochs"]
        self.batch_size = settings["batch_size"]
        self.architecture = settings["architecture"]
        previous_create_or_update = self.create_or_update
        self.create_or_update = settings["create_or_update"]
        self.metrics = [] if not self.trainable else self.trainable.getMetrics()

        if previous_create_or_update != self.create_or_update:
            self.model_details = ""
            self.model_url = ""
            self.model_filename = ""
            # should maybe delete uploaded model?
        if self.create_or_update == "create":
            self.model_details = {"architecture":self.architecture}
            self.model_url = ""
            self.model_filename = ""

        self.updateChart(self.metrics)
        return {}

    def update_chart_type(self,settings):
        self.chart_type = settings["chart_type"]
        self.metrics = [] if not self.trainable else self.trainable.getMetrics()
        self.updateChart(self.metrics)
        return {}

    def upload_model(self,path,data):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
        os.makedirs(model_dir)
        self.model_folder = model_dir

        self.model_path = os.path.join(model_dir, path)
        open(self.model_path, "wb").write(data)

        if len(self.train_classes) > 1:
            self.trainable = TrainableClassifier()
        else:
            self.trainable = TrainableAutoEncoder()
        self.trainable.open(self.model_path)

        self.updateChart(self.trainable.getMetrics())

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

    def updateChart(self,metrics):
        nr_epochs = max(len(metrics),self.current_nr_epochs)
        if self.chart_type == "accuracy":
            self.chart_html = ChartUtils.createAccuracyChart(metrics,nr_epochs)
        else:
            self.chart_html = ChartUtils.createLossChart(metrics,nr_epochs)




