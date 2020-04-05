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

from tkinter import *
from tkinter import filedialog, ttk
import os.path
from PIL import Image, ImageTk

from simpledl.image.embedding.embedding_model import EmbeddingModel
from simpledl.image.model_factories.factory import Factory
from simpledl.image.utils.image_utils import ImageUtils
import threading
from simpledl.utils.gui.tframe import TFrame

ARCHITECTURE = "architecture"
PATH = "path"

class TrainingThread(threading.Thread):

    def __init__(self,embedding_model,images_folder,onProgress=None,onCompletion=None,settings={}):
        super(TrainingThread,self).__init__(target=self)
        self.embedding_model = embedding_model
        self.images_folder = images_folder
        self.onProgress=onProgress
        self.onCompletion=onCompletion

    def run(self):
        self.embedding_model.train(self.images_folder,progress_cb=self.onProgress)
        if self.onCompletion:
            self.onCompletion()

class SettingsDialog(object):

    def __init__(self,update_settings):
        self.frame = TFrame(title="settings")
        self.update_settings = update_settings
        self.database_path = ""

        crow = 0
        architectures = Factory.getAvailableArchitectures()
        self.architecture= architectures[0]

        self.frame.addLabel("arch_label", text="Architecture",row=crow, col=0)
        self.frame.addOptionMenu("arch_menu",choices=architectures,initial_choice=self.architecture,cb=self.setArchitecture,row=crow, col=1)
        crow += 1

        self.frame.addButton("select_db", text="Select database...", cb=self.selectDatabase, row=crow, col=0, sticky=E)
        self.frame.addLabel("selected_database", text="No database selected", row=crow, col=1, sticky=W)
        crow += 1

        self.frame.addButton("create_database",text="Create", cb=self.doCreate,row=crow,col=0,columnspan=2)
        self.frame.setEnabled("create_database",False)

    def open(self):
        self.frame.open()

    def setArchitecture(self,architecture):
        self.architecture = architecture

    def selectDatabase(self):
        database_path = filedialog.asksaveasfilename(initialdir=".", title="Select database file",filetypes = (("db files","*.db"),("all files","*.*")))
        if database_path:
            if not os.path.splitext(database_path)[1]:
                database_path += ".db"
            self.database_path = database_path
            t = os.path.split(self.database_path)[1]
            self.frame.addLabel("selected_database", text=t)
            self.frame.setEnabled("create_database",True)

    def doCreate(self):
        new_settings = {
            ARCHITECTURE:self.architecture,
            PATH:self.database_path
        }
        self.update_settings(new_settings)
        self.frame.close()

class EmbeddingsWindow(object):

    def __init__(self):
        self.frame = TFrame(title="SimpleDL Image Embedding Search",height=600,width=800)
        self.store_file = ""
        self.images_folder = ""
        self.status = ""
        self.loading = False
        self.embedding_model = None
        self.img = None

        crow = 0

        self.frame.addButton("create_database", text="Create Database", cb=self.createDatabase, row=crow, col=0, sticky=E)

        crow += 1
        self.frame.addButton("open_database", text="Open Database", cb=self.selectDatabase, row=crow, col=0, sticky=E)
        self.frame.addLabel("selected_database", text="No Database Selected", row=crow, col=1, sticky=W, columnspan=2)

        crow += 1
        self.frame.addSeparator("s1", orient=HORIZONTAL, row=crow,col=0, columnspan=3, sticky="ew")

        crow += 1

        self.frame.addLabel("add_images", text="Add Images to Database",row=crow,col=0,columnspan=2)

        crow += 1
        self.frame.addButton("select_images", text="Select Images Folder", cb=self.selectImages, row=crow, col=0, sticky=E)
        self.frame.addLabel("selected_images", text="No Images Selected", row=crow, col=1, sticky=W)

        crow += 1
        self.frame.addButton("load_images", text="Load Images", cb=self.doLoad, row=crow, col=0, sticky=E)
        self.frame.addLabel("status", text=self.status, row=crow, col=1, sticky=W)

        crow += 1
        self.frame.addSeparator("s2",orient=HORIZONTAL, row=crow,col=0, columnspan=3, sticky="ew", padx=0, pady=10)

        crow += 1
        self.frame.addLabel("search", text="Search Database", row=crow, col=0, columnspan=2)

        crow += 1
        self.frame.addButton("load_image", text="Load Search Image", cb=self.selectSearchImage, row=crow, col=0, sticky=E)
        self.frame.addLabel("search_image_label", text="", row=crow, col=1, sticky=W)
        self.frame.addLabel("search_image", text="", row=crow, col=2, sticky=W)

        crow += 1
        self.frame.addButton("search_btn", text="Search!", cb=self.doSearch, row=crow,col=0, sticky=E)
        self.frame.addLabel("search_status_label", text="", row=crow, col=1, sticky=W)

        crow += 1
        self.search_image_path = None
        self.search_image = None
        self.search_results_row = crow
        self.search_results_ids = []

        self.updateButtonStatus()

    def open(self):
        self.frame.open()

    def createDatabase(self):
        def do_create(create_settings):
            path = create_settings[PATH]
            architecture = create_settings[ARCHITECTURE]
            EmbeddingModel.create(path,architecture)
            self.openDatabase(path)
        d = SettingsDialog(do_create)
        d.open()

    def selectDatabase(self):
        path = filedialog.askopenfilename(initialdir=".", title="Select database file", filetypes = (("db files","*.db"),("all files","*.*")))
        if path:
            self.openDatabase(path)

    def openDatabase(self,path):
        self.store_file = path
        self.embedding_model = EmbeddingModel(self.store_file)
        t = os.path.split(self.store_file)[1] + " (%s, %d images)"%(self.embedding_model.getArchitecture(),len(self.embedding_model))
        self.frame.addLabel("selected_database", text=t)
        self.updateButtonStatus()
        self.clearSearchResults()

    def selectImages(self):
        path = filedialog.askdirectory(initialdir=".", title="Select images folder")
        if path:
            self.images_folder = path
            t = os.path.split(self.images_folder)[1]
            self.frame.addLabel("selected_images", text=t)
            self.updateButtonStatus()

    def selectSearchImage(self):
        path = filedialog.askopenfilename(initialdir=".", title="Select Image File", filetypes=(
			("image files", ".jpg .jpeg .png .gif"), ("all files", "*.*")))
        if path:
            self.search_image_path = path
            t = os.path.split(self.search_image_path)[1]
            self.frame.addLabel("search_image_label", text=t)
            self.search_image = Image.open(self.search_image_path)
            thumb = ImageUtils.resizeImage(self.search_image,200)
            self.frame.addLabel("search_image",image=thumb)
            self.clearSearchResults()
            self.updateButtonStatus()

    def doLoad(self):
        self.updateStatus("Loading database...")
        self.loading = True
        self.updateButtonStatus()
        tt = TrainingThread(self.embedding_model,self.images_folder,lambda msg:self.loadProgress(msg), lambda: self.loadComplete())
        tt.start()

    def loadProgress(self,msg):
        self.updateStatus("Loading: "+msg)

    def loadComplete(self):
        self.updateStatus("Loaded database")
        self.loading = False
        self.updateButtonStatus()

    def updateStatus(self,status):
        self.status = status
        self.frame.addLabel("status", text=self.status)

    def updateButtonStatus(self):
        self.frame.setEnabled("load_images",self.images_folder and self.store_file and not self.loading)

    def clearSearchResults(self):
        for id in self.search_results_ids:
            self.frame.removeElement(id)
        self.search_results_ids = []
        self.searchProgress("")

    def searchProgress(self,progress):
        self.frame.addLabel("search_status_label",text=str(progress))

    def doSearch(self):
        if self.embedding_model and self.search_image:

            self.clearSearchResults()

            def progress_cb(progress):
                self.searchProgress(progress)

            self.searchProgress("Starting search...")

            matches = self.embedding_model.search(self.search_image,progress_cb)

            index = 0
            for (path,similarity,bestimage) in matches:
                bml = "l"+str(index)
                bmi = "b"+str(index)
                img = ImageUtils.resizeImage(bestimage, 200)
                self.frame.addLabel(bml,text=str(similarity), row=self.search_results_row+index, col=0, sticky=E)
                self.frame.addLabel(bmi,image=img,row=self.search_results_row+index, col=1, columnspan=3, sticky=W)
                self.search_results_ids.append(bmi)
                self.search_results_ids.append(bml)
                index += 1

if __name__ == "__main__":
    EmbeddingsWindow().open()