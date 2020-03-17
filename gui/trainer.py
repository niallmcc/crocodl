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

    def run(self):
        from imgclassifier.train import train
        train(self.foldername,self.updateStats,epochs=self.epochs,completion_callback=self.onCompletion)

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
        self.foldername = ""
        self.val_accs = []
        self.settings = { NR_EPOCHS:5 }
        self.inputlabel = None
        self.chartm = 25
        self.labelcanvas_width = 100
        self.chart_width = 200
        self.chart_height = 100
        self.stats = {}

        self.canvas=None
        self.epochlabel = None

        self.master.title("Train SimpleDL Image Classifier")


        crow = 0
        loadButton = ButtonWithFont(self.master, text="Load Data...",font=self.font,command=self.load_data)
        loadButton.grid(row=crow,column=0)
        self.inputlabel = LabelWithFont(self.master, text="No data selected", fg="red")
        self.inputlabel.grid(row=crow,column=1)
        crow += 1
        settingsButton = ButtonWithFont(self.master, text="Training Settings...", font=self.font, command=self.open_settings)
        settingsButton.grid(row=crow, column=0)
        crow += 1
        trainButton = ButtonWithFont(self.master, text="Train Model",font=self.font,command=self.train)
        trainButton.grid(row=crow,column=0)
        self.statuslabel = LabelWithFont(self.master, text="", font=self.font)
        self.statuslabel.grid(row=crow, column=1)
        self.status_row = crow
        crow += 1
        self.chart_row = crow
        self.drawChart()

    def setStatus(self,text,col="black"):
        self.statuslabel.grid_forget()
        self.statuslabel = LabelWithFont(self.master, text=text, font=self.font, colour=col)
        self.statuslabel.grid(row=self.status_row, column=1)

    def drawChart(self):

        if self.canvas:
            self.canvas.grid_forget()

        self.labelcanvas = Canvas(self.master, width=self.labelcanvas_width, height=self.chart_height + 2 * self.chartm)
        self.labelcanvas.grid(row=self.chart_row, column=0)

        self.labelcanvas.create_text(self.labelcanvas_width/2,self.chartm+self.chart_height/2-30,text="train accuracy", fill="red")
        self.labelcanvas_trainaccuracy_id = None
        self.labelcanvas.create_text(self.labelcanvas_width/2, self.chartm + self.chart_height/2+10, text="test accuracy", fill="blue")
        self.labelcanvas_testaccuracy_id = None
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

        if self.epochlabel:
            self.epochlabel.grid_forget()
        self.epochlabel = LabelWithFont(self.master, text="epochs", font=self.font)
        self.epochlabel.grid(row=self.chart_row+1, column=1)

    def updateStat(self,name,val):
        if name == "acc":
            if self.labelcanvas_trainaccuracy_id:
                self.labelcanvas.delete(self.labelcanvas_trainaccuracy_id)
            self.labelcanvas_trainaccuracy_id = self.labelcanvas.create_text(self.labelcanvas_width/2,self.chartm+self.chart_height/2-10,text=val,fill="red")
        elif name == "val_acc":
            if self.labelcanvas_testaccuracy_id:
                self.labelcanvas.delete(self.labelcanvas_testaccuracy_id)
            self.labelcanvas_testaccuracy_id = self.labelcanvas.create_text(self.labelcanvas_width/2,self.chartm+self.chart_height/2+30,text=val, fill="blue")


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

    def load_data(self):
        self.inputlabel.grid_forget()
        self.foldername = filedialog.askdirectory(initialdir=".", title="Select data folder",mustexist=True)
        from imgclassifier.trainutils import check_data_folder
        (summary, errors) = check_data_folder(self.foldername)

        if len(errors) > 0:
            self.foldername = None
            self.inputlabel = LabelWithFont(self.master, text=",".join(errors), colour="red")
        else:
            self.inputlabel = LabelWithFont(self.master, text="%s - %s"%(os.path.split(self.foldername)[1],summary), font=self.font)
        self.inputlabel.grid(row=0,column=1)

    def open_settings(self):
        def update_settings(new_settings):
            self.settings = new_settings
        d = SettingsDialog(self.master,self.settings,update_settings)
        self.master.wait_window(d.top)

    def getNrEpochs(self):
        return self.settings[NR_EPOCHS]

    def train(self):
        self.stats = {}
        self.drawChart()
        self.updateStat("val_acc","-")
        self.updateStat("acc","-")

        if not self.foldername:
            return

        def updateStats(epoch,stats):
            val_acc = float(stats["val_accuracy"])
            acc = float(stats["accuracy"])
            self.updateChart(epoch,[("val_acc",val_acc,"blue"),("acc",acc,"red")])

        def completed():
            self.setStatus("Training Complete")

        tt = TrainingThread(self.foldername,updateStats,epochs=self.getNrEpochs(),onCompletion=completed)
        tt.start()
        self.setStatus("Training In Progress...")

    def client_exit(self):
        exit()



if __name__ == "__main__":
    root = Tk()
    app = Window(root)
    root.geometry("500x300")
    root.mainloop()