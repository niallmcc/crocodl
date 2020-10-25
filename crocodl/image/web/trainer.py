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
from crocodl.image.web.scorer import ClassifierScorer, AutoencoderScorer


class TrainingThread(threading.Thread):

    def __init__(self,trainer,model_folder,training_folder,testing_folder,other_folder,trainable,onEpoch,epochs=5,batchSize=16,onCompletion=None,onEvaluationProgress=None,onBatch=None,reportPath=None):
        super(TrainingThread,self).__init__(target=self)
        self.trainer = trainer
        self.model_folder = model_folder
        self.training_folder = training_folder
        self.testing_folder = testing_folder
        self.other_folder = other_folder
        self.onEpoch = onEpoch
        self.epochs=epochs
        self.batchSize = batchSize
        self.onCompletion=onCompletion
        self.onEvaluationProgress = onEvaluationProgress
        self.onBatch=onBatch
        self.trainable = trainable
        self.report_path = reportPath

    def run(self):
        self.trainable.train(self.model_folder,self.training_folder,self.testing_folder,epoch_callback=lambda epoch,metrics:self.progress_cb(epoch,metrics),epochs=self.epochs,batch_size=self.batchSize,batch_callback=self.onBatch)
        if self.report_path:
            if self.onEvaluationProgress:
                self.onEvaluationProgress(0.0)
            self.trainable.evaluate(self.report_path,self.other_folder)
            if self.onEvaluationProgress:
                self.onEvaluationProgress(1.0)
        if self.onCompletion:
            self.onCompletion()

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
        self.other_folder = ""
        self.data_info = None
        self.report_path = ""
        self.training_status = ""
        self.completed_epoch = 0

        self.model_details = {}
        self.model_filename = ""
        self.model_url = ""

        self.architecture = ""
        self.architectures = []
        self.create_or_update = "create"
        self.batch_size = 16

        self.chart_type = "loss"
        self.chart_types = ["accuracy", "loss"]

        self.training = False
        self.progress = 0.0
        self.metrics = []

        self.current_nr_epochs = 5  # number of epochs in current training

        self.current_batch = 0  # number of completed batches in current epoch

        if self.getType() == "classifier":
            self.scorer = ClassifierScorer()
        elif self.getType() == "autoencoder":
            self.scorer = AutoencoderScorer()

    logger = createLogger("train_app")

    def updateTrainingProgress(self,epoch,metrics):
        self.progress = epoch/(2+self.current_nr_epochs)
        self.metrics = metrics
        self.completed_epoch = epoch
        self.training_status = "Completed Epoch %d/%d"%(epoch,self.current_nr_epochs)

    def updateTrainingBatch(self,batch):
        self.current_batch = batch
        self.training_status = "Running Epoch %d Batch %d"%(self.completed_epoch+1,self.current_batch)

    def updateEvaluationProgress(self,fraction_complete):
        self.progress = fraction_complete
        self.training_status = "Evaluating"

    def setCompleted(self):
        self.progress = 1.0
        self.training = False
        self.training_status = "Trained"

    def submit(self):
        if self.trainable == None:
            model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
            if os.path.isdir(model_dir):
                shutil.rmtree(model_dir)
            os.makedirs(model_dir)
            self.model_folder = model_dir

            self.model_path = os.path.join(model_dir, "model.h5")
            self.completed_epoch = 0
            self.current_batch = 0
            self.model_details = self.architecture
            self.model_url = "models/model.h5"
            self.model_filename = "model.h5"
            self.report_path = os.path.join(model_dir, "training_report.html")
            if self.getType() == "classifier":
                self.trainable = TrainableClassifier()
                self.trainable.createEmpty(self.model_path, self.train_classes, {TrainableClassifier.ARCHITECTURE: self.architecture})
            else:
                self.trainable = TrainableAutoEncoder()
                self.trainable.createEmpty(self.model_path, self.train_classes, {TrainableAutoEncoder.ARCHITECTURE: self.architecture})
        self.scorer.set_model_path(self.model_path)
        self.training_thread = TrainingThread(
            self,
            self.model_folder,
            self.training_folder,
            self.testing_folder,
            self.other_folder,
            self.trainable,
            onEpoch=lambda epoch,metrics: self.updateTrainingProgress(epoch,metrics),
            epochs=self.current_nr_epochs,
            batchSize=self.batch_size,
            onCompletion=lambda : self.setCompleted(),
            onEvaluationProgress=lambda f: self.updateEvaluationProgress(f),
            onBatch=lambda batch,epoch: self.updateTrainingBatch(batch),
            reportPath=self.report_path)

        self.training = True
        self.training_thread.start()
        return {}

    def get_training_report(self):
        if self.report_path:
            return open(self.report_path).read()
        else:
            return ""

    def get_status(self):
        return {
            "progress":self.progress,
            "training":self.training,
            "training_status":self.training_status,
            "metrics":self.metrics,
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

    def cancel(self):
        if self.trainable:
            return self.trainable.cancel()
        else:
            return False

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
        else:
            unpack_dir = partition_dir
        unpack_data(upload_path,unpack_dir)

        if partition == "training":
            self.training_folder = partition_dir
        if partition == "testing":
            self.testing_folder = partition_dir
        if partition == "other":
            # autoencoder
            self.other_folder = partition_dir

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

        return {}

    def update_chart_type(self,settings):
        self.chart_type = settings["chart_type"]
        self.metrics = [] if not self.trainable else self.trainable.getMetrics()
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

        metadata = read_metadata(self.model_path)
        del metadata["epochs"]

        self.model_details = metadata
        self.model_url = "models/"+path
        self.model_filename = path
        self.scorer.set_model_path(self.model_path)
        return {}

    def send_code(self):
        if self.architecture:
            cf = CodeFormatter()
            if self.getType() == "classifier":
                return cf.formatHTML(TrainableClassifier.getCode(self.architecture))
            elif self.getType() == "autoencoder":
                return cf.formatHTML(TrainableAutoEncoder.getCode(self.architecture))

        return "Select model options to view training code"



    def score(self):
        return self.scorer.score()

    def upload_image(self,path,data):
        return self.scorer.upload_image(path,data)

    def send_scoreimage(self,path):
        return self.scorer.send_scoreimage(path)

    def send_score_code(self):
        return self.scorer.send_score_code()


