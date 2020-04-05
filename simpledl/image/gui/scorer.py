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
from tkinter import filedialog
from PIL import Image

from simpledl.image.classifier.scorable import Scorable
from simpledl.utils.gui.tframe import TFrame
from simpledl.image.utils.image_utils import ImageUtils

class ScoreWindow(object):

	def __init__(self,scorable=None):
		self.frame = TFrame(title="SimpleDL Image Classifier",width=400, height=400)
		self.image_filename = ""
		self.score_ids = []
		self.scorable = scorable
		crow = 0
		if self.scorable is None:
			self.load_model_button = self.frame.addButton("load_model",text="Load Model",cb=self.loadModel,row=crow,col=0)
		crow += 1
		self.load_image_button = self.frame.addButton("load_image", text="Load Image", cb=self.loadImage, row=crow, col=0)
		crow += 1
		self.image = self.frame.addLabel("image",text="No Image Loaded",row=crow,col=0)
		crow += 1
		self.score_button = self.frame.addButton("score",text="Score",cb=self.doScore,row=crow,col=0)
		crow += 1
		self.score_row = crow
		self.updateButtonStatus()

	def open(self):
		self.frame.open()

	def updateButtonStatus(self):
		self.frame.setEnabled("score",self.image_filename and self.scorable)

	def loadModel(self):
		self.model_path = filedialog.askopenfilename(initialdir=".", title="Select model file")
		self.scorable = Scorable()
		self.scorable.load(self.model_path)
		self.clearScores()
		self.updateButtonStatus()

	def loadImage(self):
		self.image_filename = filedialog.askopenfilename(initialdir=".", title="Select Image File", filetypes=(
			("image files", ".jpg .jpeg .png .gif"), ("all files", "*.*")))
		load = Image.open(self.image_filename)
		resized = ImageUtils.resizeImage(load,300)
		self.frame.addLabel("image",text="",row=2,col=0,image=resized)
		self.clearScores()
		self.updateButtonStatus()

	def clearScores(self):
		for score_id in self.score_ids:
			self.frame.removeElement(score_id)
		self.scorelabels = []

	def doScore(self):
		self.clearScores()
		if self.scorable and self.image_filename:
			results = self.scorable.score(self.image_filename)
			ctr = 0
			for (clazz,prob) in results:
				score_id = "s"+str(ctr)
				self.frame.addLabel(score_id,text=str("%s: %f"%(clazz,prob)),row=self.score_row+ctr)
				ctr += 1
				self.score_ids.append(score_id)


if __name__ == "__main__":
	app = ScoreWindow()
	app.open()
	# app.configure(bg='white')
	# app.tk_setPalette(background='white', foreground='black',
	# 				   activeBackground='yellow', activeForeground='black')
	# root.mainloop()