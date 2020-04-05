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

import os

from tkinter import *
from tkinter import filedialog
import threading

from simpledl.image.classifier.trainable import Trainable
from simpledl.image.model_factories.factory import Factory
from simpledl.image.gui.scorer import ScoreWindow
from simpledl.utils.gui.tframe import TFrame

class TrainingThread(threading.Thread):

    def __init__(self,foldername,trainable,updateStats,epochs=5,onCompletion=None,settings={}):
        super(TrainingThread,self).__init__(target=self)
        self.foldername = foldername
        self.updateStats = updateStats
        self.epochs=epochs
        self.onCompletion=onCompletion
        self.settings = settings
        self.trainable = trainable

    def run(self):
        self.trainable.train(self.foldername,self.updateStats,epochs=self.epochs,completion_callback=self.onCompletion,settings=self.settings)

class TrainSettingsDialog(object):

    def __init__(self,nr_epochs,settings,update_settings):
        self.update_settings = update_settings
        self.frame = TFrame(title="Training Settings")

        self.batch_size = settings[Trainable.BATCH_SIZE]
        self.nr_epochs = nr_epochs
        crow = 0

        self.frame.addLabel("batch_size",text="Batch Size",row=crow,col=0)
        self.frame.addSpinbox("batch_size_spinner",val=self.batch_size,cb=self.setBatchSize,minval=1,maxval=1000,row=crow,col=1)
        crow += 1

        self.frame.addLabel("nr_epochs_label", text="Number of Epochs", row=crow, col=0, sticky=E)
        self.frame.addSpinbox("nr_epochs", self.nr_epochs, cb=self.setNrEpochs, minval=1, maxval=1000, row=crow,
                              col=1, sticky=W)

        crow += 1
        self.frame.addButton("ok",text="OK", cb=self.doOk, row=crow,col=0,columnspan=2)

    def open(self):
        self.frame.open()

    def setBatchSize(self,batch_size):
        self.batch_size = batch_size

    def setNrEpochs(self, nr_epochs):
        self.nr_epochs = nr_epochs

    def doOk(self):
        new_settings = {
            Trainable.BATCH_SIZE: self.batch_size,
        }
        self.update_settings(self.nr_epochs,new_settings)
        self.frame.close()

class CreateModelSettingsDialog(object):

    def __init__(self,settings,update_settings):
        self.update_settings = update_settings
        self.frame = TFrame(title="Create Model Settings")

        self.architecture = settings[Trainable.ARCHITECTURE]
        self.model_path = None
        crow = 0

        architectures = Factory.getAvailableArchitectures()
        self.frame.addLabel("architecture",text="Architecture",row=crow, col=0)
        self.frame.addOptionMenu("arch_menu",choices=architectures,initial_choice=self.architecture,cb=self.setArchitecture,row=crow,col=1)
        crow += 1

        self.frame.addButton("select_model", text="Model file...", cb=self.selectModel, row=crow, col=0, sticky=E)
        self.frame.addLabel("selected_model", text="No file selected", row=crow, col=1, sticky=W)
        crow += 1

        self.frame.addButton("create_model",text="Create Model", cb=self.doCreate, row=crow,col=0,sticky=E)
        self.frame.addLabel("create_model_label", text="", row=crow, col=1, sticky=W)
        self.frame.setEnabled("create_model", False)

    def open(self):
        self.frame.open()

    def selectModel(self):
        model_path = filedialog.asksaveasfilename(initialdir=".", title="Select model file",filetypes = (("h5 files","*.h5"),("all files","*.*")))
        if model_path:
            if not os.path.splitext(model_path)[1]:
                model_path += ".h5"
            self.model_path = model_path
            t = os.path.split(self.model_path)[1]
            self.frame.addLabel("selected_model", text=t)
            self.frame.setEnabled("create_model", True)

    def setArchitecture(self,architecture):
        self.architecture = architecture

    def doCreate(self):
        new_settings = {
            Trainable.ARCHITECTURE: self.architecture,
            TrainerWindow.MODEL_PATH: self.model_path
        }
        self.frame.addLabel("create_model_label", text="Creating Model...")
        self.update_settings(new_settings)
        self.frame.close()

class TrainerWindow(object):

    MODEL_PATH = "model_path"
    DEFAULT_EPOCHS = 2

    def __init__(self):
        self.frame = TFrame(title="Train SimpleDL Image Classifier",width=500,height=800)
        self.model_path = ""

        self.settings = { Trainable.BATCH_SIZE: Trainable.DEFAULT_BATCH_SIZE,
                          Trainable.ARCHITECTURE: Trainable.DEFAULT_ARCHITECTURE }

        self.chartm = 25
        self.label_canvas_width = 100
        self.chart_width = 200
        self.chart_height = 100
        self.nr_epochs = TrainerWindow.DEFAULT_EPOCHS
        self.data_classes = []

        self.data_dir = ""
        self.training = False
        self.trainable = None
        self.error_message = ""

        self.canvas=None
        self.epoch_label = None

        crow = 0
        self.frame.addButton("load_data", text="Load Data", row=crow, col=0, sticky=E, cb=self.doLoadData)
        self.frame.addLabel("selected_data", text="No data selected", row=crow, col=1, sticky=W)

        crow += 1
        self.frame.addSeparator("s1",row=crow,columnspan=2)

        crow += 1
        self.frame.addButton("create_model", text="Create Model", cb=self.doCreateModel, row=crow, col=0, sticky=E)
        self.frame.setEnabled("create_model", False)

        crow += 1
        self.frame.addButton("open_model", text="Open Model", cb=self.doOpenModel, row=crow, col=0, sticky=E)
        self.frame.addLabel("model_path_label", text=self.model_path, row=crow, col=1, sticky=W)
        self.frame.setEnabled("open_model", False)

        crow += 1
        self.frame.addSeparator("s2", row=crow, columnspan=2)

        crow += 1
        self.frame.addButton("train_settings", text="Training Settings", cb=self.doOpenTrainSettings, row=crow, col=0, sticky=E)
        self.frame.setEnabled("train_settings", False)
        self.frame.addLabel("train_settings_summary", text="", row=crow, col=1, sticky=W)
        self.updateTrainSettingsSummary()

        crow += 1
        self.frame.addButton("train_model", text="Train Model", cb=self.doTrain, row=crow,col=0,sticky=E)
        self.frame.setEnabled("train_model",False)

        self.frame.addLabel("status_label" ,text="", row=crow, col=1, sticky=W)

        crow += 1
        self.drawChart(crow)

        crow += 2
        self.frame.addButton("save_model", text="Save Model",cb=self.saveModel, row=crow,col=0,sticky=E)
        self.frame.setEnabled("save_model",False)

        crow += 1
        self.frame.addButton("score_model", text="Score Model...", cb=self.openScore, row=crow, col=0, sticky=E)
        self.frame.setEnabled("score_model",False)

    def open(self):
        self.frame.open()

    def showStatus(self):
        if self.training:
            self.frame.setEnabled("load_data", False)
            self.frame.setEnabled("create_model", False)
            self.frame.setEnabled("open_model",False)
            self.frame.setEnabled("train_settings", False)
            self.frame.setEnabled("train_model", False)
            self.frame.setEnabled("save_model", False)
            self.frame.setEnabled("score_model", False)
            text = "Training..."
        else:
            self.frame.setEnabled("load_data",True)
            self.frame.setEnabled("create_model",self.data_dir != "")
            self.frame.setEnabled("open_model",self.data_dir != "")
            self.frame.setEnabled("train_settings", self.trainable != None)
            self.frame.setEnabled("train_model",self.trainable != None)
            self.frame.setEnabled("save_model",self.model_path != "")
            self.frame.setEnabled("score_model",self.trainable != None and self.trainable.isTrained())
            text = ""

        if self.error_message:
            text = self.error_message

        self.frame.addLabel("status_label", text=text)

    def drawChart(self,chart_row):

        self.ylabel_canvas = self.frame.addCanvas("ylabel_canvas", width=self.label_canvas_width, height=self.chart_height + 2 * self.chartm, row=chart_row, col=0, sticky=E)

        self.ylabel_canvas.create_text(self.label_canvas_width/2,self.chartm+self.chart_height/2-30,text="train accuracy", fill="red")
        self.label_canvas_trainaccuracy_id = None
        self.ylabel_canvas.create_text(self.label_canvas_width/2, self.chartm + self.chart_height/2+10, text="test accuracy", fill="blue")
        self.label_canvas_testaccuracy_id = None

        self.chart = self.frame.addChart("accuracy", margin=self.chartm, width=self.chart_width,
                             height=self.chart_height, range=((0,0),(self.nr_epochs,1.0)),
                                row=chart_row, col=1,sticky=W)

        self.xlabel_canvas = self.frame.addCanvas("xlabel_canvas", width=self.chart_width + 2*self.chartm,
                                                  height=self.chartm, row=chart_row+1, col=1,
                                                  sticky=W)

        self.xlabel_canvas.create_text(self.chartm + self.chart_width / 2, self.chartm / 2, text="epochs")

    def rescaleChart(self):
        total_epochs = len(self.trainable.getEpochs()) + self.nr_epochs
        self.chart = self.frame.addChart("accuracy", margin=self.chartm, width=self.chart_width,
                                         height=self.chart_height, range=((0, 0), (total_epochs, 1.0)))
        self.updateChart()

    def updateStat(self,name,val):
        if name == "accuracy":
            if self.label_canvas_trainaccuracy_id:
                self.ylabel_canvas.delete(self.label_canvas_trainaccuracy_id)
            self.label_canvas_trainaccuracy_id = self.ylabel_canvas.create_text(self.label_canvas_width/2,self.chartm+self.chart_height/2-10,text=val,fill="red")
        elif name == "val_accuracy":
            if self.label_canvas_testaccuracy_id:
                self.ylabel_canvas.delete(self.label_canvas_testaccuracy_id)
            self.label_canvas_testaccuracy_id = self.ylabel_canvas.create_text(self.label_canvas_width/2,self.chartm+self.chart_height/2+30,text=val, fill="blue")

    def updateChart(self):
        history = { "accuracy":[], "val_accuracy":[]}
        epochs = self.trainable.getEpochs()
        for i in range(len(epochs)):
            epoch = epochs[i]
            history["accuracy"].append(epoch["accuracy"])
            history["val_accuracy"].append(epoch["val_accuracy"])

        for key in history:
            coords = []
            epoch = 1
            colour = "red" if key == "accuracy" else "blue"
            for value in history[key]:
                coords.append((epoch,value))
                epoch += 1
            self.chart.plotLine(coords,colour)

    def doLoadData(self):
        self.frame.addLabel("selected_data", text="")
        data_dir = filedialog.askdirectory(initialdir=".", title="Select data folder",mustexist=True)
        if not data_dir:
            return
        from simpledl.image.classifier.trainutils import check_data_dir
        (summary, error) = check_data_dir(data_dir)
        if error:
            self.data_dir = ""
            self.frame.addLabel("selected_data", text=error, fg="red")
        else:
            self.data_dir = data_dir
            self.data_classes = summary
            self.frame.addLabel("selected_data", text="%s (%d classes)"%(os.path.split(self.data_dir)[1],len(self.data_classes)))
            self.frame.setEnabled("create_model", True)
            self.frame.setEnabled("open_model", True)
        self.showStatus()

    def doCreateModel(self):
        def update_settings(settings):
            self.frame.addLabel("model_path_label", "Creating model...")
            model_path = settings[TrainerWindow.MODEL_PATH]
            del settings[TrainerWindow.MODEL_PATH]
            self.trainable = Trainable()
            self.trainable.createEmpty(self.data_classes,settings)
            self.trainable.saveModel(model_path)
            self.loadedModel(model_path)
        d = CreateModelSettingsDialog(self.settings,update_settings)
        d.open()

    def doOpenModel(self):
        model_path = filedialog.askopenfilename(initialfile=self.model_path, title="Select model file",filetypes = (("h5 files","*.h5"),("all files","*.*")))
        self.frame.addLabel("model_path_label", "Opening model...")
        self.trainable = Trainable()
        self.trainable.open(model_path)
        self.loadedModel(model_path)
        self.rescaleChart()

    def loadedModel(self,path):
        self.model_path = path
        self.frame.addLabel("model_path_label", os.path.split(self.model_path)[1]+" "+str(self.trainable))
        self.showStatus()

    def openScore(self):
        ScoreWindow(self.trainable.getScorable()).open()

    def doOpenTrainSettings(self):
        def update_settings(nr_epochs,settings):
            self.nr_epochs = nr_epochs
            self.train_settings = settings
            self.updateTrainSettingsSummary()
            self.rescaleChart()

        d = TrainSettingsDialog(self.nr_epochs,self.settings,update_settings)
        d.open()

    def updateTrainSettingsSummary(self):
        self.frame.addLabel("train_settings_summary","train for %d epochs"%(self.nr_epochs))

    def doTrain(self):

        self.updateStat("val_accuracy","-")
        self.updateStat("accuracy","-")

        if self.training:
            return

        self.error_message = ""
        self.training = True

        if not self.data_dir:
            return

        def updateStats(epoch,stats):

            val_acc = float(stats["val_accuracy"])
            acc = float(stats["accuracy"])
            self.updateStat("val_accuracy", "%0.2f" % (val_acc))
            self.updateStat("accuracy", "%0.2f" % (acc))

            self.updateChart()

        def completed():
            self.setTrainingComplete()

        self.rescaleChart()
        tt = TrainingThread(self.data_dir,self.trainable,updateStats,epochs=self.nr_epochs,onCompletion=completed,settings=self.settings)
        tt.start()
        self.showStatus()

    def saveModel(self):
        if self.trainable and self.model_path:
            self.trainable.saveModel(self.model_path)

    def setTrainingComplete(self):
        self.training = False
        self.showStatus()

if __name__ == "__main__":
    tw = TrainerWindow()
    tw.open()
