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

from fonts.tk_ttf import LabelWithFont, ButtonWithFont, TTF

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

Canvas.create_circle = _create_circle

class TrainingThread(threading.Thread):

    def __init__(self,foldername,updateStats,epochs=5,onCompletion=None):
        super(TrainingThread,self).__init__(target=self)
        self.foldername = foldername
        self.updateStats = updateStats
        self.epochs=epochs
        self.onCompletion=onCompletion
        from imgclassifier.train import Train
        self.train = Train()

    def run(self):
        self.train.train(self.foldername,self.updateStats,epochs=self.epochs,completion_callback=self.onCompletion)

    def save(self,folder):
        self.train.save_model(folder)

class SettingsDialog(object):

    def __init__(self,parent,settings,update_settings):
        self.font = TTF(16)
        self.update_settings = update_settings
        top = self.top = Toplevel(parent)
        crow = 0
        label = LabelWithFont(top, text="Number of Epochs",font=self.font)
        label.grid(row=crow,column=0)
        v = DoubleVar(value=settings["nr_epochs"])
        self.nr_epochs = Spinbox(top,from_=1,to_=1000,textvariable=v)
        self.nr_epochs.grid(row=crow,column=1)
        crow += 1
        b = ButtonWithFont(top, text="OK", command=self.ok,font=self.font)
        b.grid(row=crow,column=0,columnspan=2)

    def ok(self):
        new_settings = {
            "nr_epochs":int(self.nr_epochs.get())
        }
        self.update_settings(new_settings)
        self.top.destroy()

NR_EPOCHS = "nr_epochs"

class Window(Frame):


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.font = TTF(16)
        self.master = master
        self.model_path = "./model.h5"
        self.val_accs = []
        self.settings = { NR_EPOCHS:5 }

        self.chartm = 25
        self.label_canvas_width = 100
        self.chart_width = 200
        self.chart_height = 100
        self.stats = {}

        self.data_dir = ""
        self.training = False
        self.trained = False
        self.error_message = ""

        self.canvas=None
        self.epoch_label = None

        self.master.title("Train SimpleDL Image Classifier")

        crow = 0
        self.load_button = ButtonWithFont(self.master, text="Load Data...",font=self.font,command=self.loadData)
        self.load_button.grid(row=crow,column=0,sticky=E)
        self.input_label = LabelWithFont(self.master, text="No data selected", fg="red")
        self.input_label.grid(row=crow,column=1,sticky=W)
        crow += 1
        self.settings_button = ButtonWithFont(self.master, text="Training Settings...", font=self.font, command=self.openSettings)
        self.settings_button.grid(row=crow, column=0,sticky=E)
        crow += 1
        self.train_button = ButtonWithFont(self.master, text="Train Model",font=self.font,command=self.doTrain,state="disabled")
        self.train_button.grid(row=crow,column=0,sticky=E)
        self.status_label = LabelWithFont(self.master,text="", font=self.font)
        self.status_label.grid(row=crow, column=1, sticky=W)
        self.status_row = crow
        crow += 1
        self.chart_row = crow
        self.drawChart()
        crow += 2
        model_path_button = ButtonWithFont(self.master, text="Model Path",font=self.font,command=self.chooseModelPath)
        model_path_button.grid(row=crow,column=0,sticky=E)

        self.model_path_label = LabelWithFont(self.master, text=self.model_path)
        self.model_path_label.grid(row=crow,column=1,sticky=W)
        self.model_path_row = crow

        crow += 1
        self.save_button = ButtonWithFont(self.master, text="Save Model",font=self.font,command=self.saveModel,state="disabled")
        self.save_button.grid(row=crow,column=0,sticky=E)

    def showStatus(self):
        col = "black"
        if self.data_dir:
            self.train_button.configure(state="normal")
            text = "Ready to Train"
            self.train_button.configure(state="normal")
        if self.trained:
            self.save_button.configure(state="normal")
            text = "Training Complete"
        else:
            self.save_button.configure(state="disabled")
        if self.training:
            self.train_button.configure(state="disabled")
            text = "Training"
        if self.error_message:
            col = "red"
            text = self.error_message
        self.status_label.grid_forget()
        self.status_label = LabelWithFont(self.master, text=text, font=self.font, colour=col)
        self.status_label.grid(row=self.status_row, column=1)

    def drawChart(self):

        if self.canvas:
            self.canvas.grid_forget()

        self.label_canvas = Canvas(self.master, width=self.label_canvas_width, height=self.chart_height + 2 * self.chartm)
        self.label_canvas.grid(row=self.chart_row, column=0)

        self.label_canvas.create_text(self.label_canvas_width/2,self.chartm+self.chart_height/2-30,text="train accuracy", fill="red")
        self.label_canvas_trainaccuracy_id = None
        self.label_canvas.create_text(self.label_canvas_width/2, self.chartm + self.chart_height/2+10, text="test accuracy", fill="blue")
        self.label_canvas_testaccuracy_id = None
        self.canvas = Canvas(self.master, width=self.chart_width + 2 * self.chartm,
                             height=self.chart_height + 2 * self.chartm)
        self.canvas.grid(row=self.chart_row, column=1)

        self.canvas.create_text(self.chartm, self.chartm + self.chart_height + self.chartm / 2, text="0")
        self.canvas.create_text(self.chartm + self.chart_width, self.chartm + self.chart_height + self.chartm / 2,
                                text=str(self.getNrEpochs()))
        self.canvas.create_text(self.chartm - self.chartm / 2, self.chartm + self.chart_height, text="0.0")
        self.canvas.create_text(self.chartm - self.chartm / 2, self.chartm, text="1.0")
        self.canvas.create_line(self.chartm, self.chart_height + self.chartm, self.chartm + self.chart_width,
                                self.chartm + self.chart_height)
        self.canvas.create_line(self.chartm, self.chartm, self.chartm, self.chartm + self.chart_height)

        if self.epoch_label:
            self.epoch_label.grid_forget()
        self.epoch_label = LabelWithFont(self.master, text="epochs", font=self.font)
        self.epoch_label.grid(row=self.chart_row+1, column=1)

    def updateStat(self,name,val):
        if name == "acc":
            if self.label_canvas_trainaccuracy_id:
                self.label_canvas.delete(self.label_canvas_trainaccuracy_id)
            self.label_canvas_trainaccuracy_id = self.label_canvas.create_text(self.label_canvas_width/2,self.chartm+self.chart_height/2-10,text=val,fill="red")
        elif name == "val_acc":
            if self.label_canvas_testaccuracy_id:
                self.label_canvas.delete(self.label_canvas_testaccuracy_id)
            self.label_canvas_testaccuracy_id = self.label_canvas.create_text(self.label_canvas_width/2,self.chartm+self.chart_height/2+30,text=val, fill="blue")

    def updateChart(self,epoch,stats):
        dx = self.chart_width / self.getNrEpochs()
        for (name,v,col) in stats:
            self.updateStat(name,"%0.2f"%(v))
            last_v = self.stats.get(name,0.0)
            x0 = (epoch)*dx
            x1 = (epoch+1) * dx

            y0 = self.chart_height - (self.chart_height * last_v)
            y1 = self.chart_height - (self.chart_height * v)

            if epoch:
                self.canvas.create_line(x0+self.chartm,y0+self.chartm,x1+self.chartm,y1+self.chartm,fill=col)

            self.canvas.create_circle(x1+self.chartm,y1+self.chartm,3,fill=col)
            self.stats[name] = v

    def loadData(self):
        self.input_label.grid_forget()
        self.data_dir = filedialog.askdirectory(initialdir=".", title="Select data folder",mustexist=True)
        from imgclassifier.trainutils import check_data_dir
        (summary, errors) = check_data_dir(self.data_dir)

        if len(errors) > 0:
            self.data_dir = None
            self.input_label = LabelWithFont(self.master, text=",".join(errors), colour="red")
        else:
            self.input_label = LabelWithFont(self.master, text="%s - %s"%(os.path.split(self.data_dir)[1],summary), font=self.font)
        self.input_label.grid(row=0,column=1)
        self.showStatus()

    def openSettings(self):
        def update_settings(new_settings):
            self.settings = new_settings
        d = SettingsDialog(self.master,self.settings,update_settings)
        self.master.wait_window(d.top)

    def getNrEpochs(self):
        return self.settings[NR_EPOCHS]

    def doTrain(self):
        self.stats = {}
        self.drawChart()
        self.updateStat("val_acc","-")
        self.updateStat("acc","-")

        self.error_message = ""
        self.training = True
        self.trained = False

        if not self.data_dir:
            return

        def updateStats(epoch,stats):
            val_acc = float(stats["val_accuracy"])
            acc = float(stats["accuracy"])
            self.updateChart(epoch,[("val_acc",val_acc,"blue"),("acc",acc,"red")])

        def completed():
            self.setTrainingComplete()

        self.tt = TrainingThread(self.data_dir,updateStats,epochs=self.getNrEpochs(),onCompletion=completed)
        self.tt.start()
        self.showStatus()

    def chooseModelPath(self):
        self.model_path = filedialog.asksaveasfilename(initialfile=self.model_path, title="Select model file")
        self.model_path_label.grid_forget()
        self.model_path_label = LabelWithFont(self.master, text=self.model_path)
        self.model_path_label.grid(row=self.model_path_row, column=1)

    def saveModel(self):
        if self.tt and self.model_path:
            self.tt.save(self.model_path)

    def setTrainingComplete(self):
        self.training = False
        self.trained = True
        self.showStatus()



if __name__ == "__main__":
    root = Tk()
    app = Window(root)
    root.geometry("500x500")
    root.configure(bg='white')
    root.tk_setPalette(background='white', foreground='black',
                       activeBackground='yellow', activeForeground='black')
    root.mainloop()