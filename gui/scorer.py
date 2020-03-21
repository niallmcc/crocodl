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
from PIL import Image, ImageTk

from fonts.tk_ttf import ButtonWithFont, TTF
from imgclassifier.score import Score

class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.font = TTF(16)
		self.master = master
		self.image_filename = ""
		self.img = None
		self.score = None
		self.scorelabels = []

		self.master.title("SimpleDL Image Classifier")
		self.pack(fill=BOTH, expand=1)
		self.load_image_button = ButtonWithFont(self, text="Load Image", font=self.font, command=self.loadImage)
		self.load_image_button.pack()
		self.load_model_button = ButtonWithFont(self, text="Load Model", font=self.font, command=self.loadModel)
		self.load_model_button.pack()
		self.score_button = ButtonWithFont(self, text="Score",font=self.font,command=self.doScore)
		self.score_button.pack()
		self.updateButtonStatus()

	def updateButtonStatus(self):
		if self.image_filename and self.score:
			self.score_button.configure(state="normal")
		else:
			self.score_button.configure(state="disabled")

	def loadModel(self):
		self.model_path = filedialog.askopenfilename(initialdir=".", title="Select model file")
		self.score = Score(self.model_path)
		self.updateButtonStatus()

	def loadImage(self):
		self.image_filename = filedialog.askopenfilename(initialdir=".", title="Select Image File", filetypes=(
			("image files", ".jpg .jpeg .png .gif"), ("all files", "*.*")))
		load = Image.open(self.image_filename)
		w = 300
		wfrac = (w / float(load.size[0]))
		h = int((float(load.size[1]) * wfrac))
		load2 = load.resize((w, h), Image.ANTIALIAS)
		render = ImageTk.PhotoImage(load2)
		if self.img:
			self.img.pack_forget()
			self.img = None
		if self.scorelabels:
			for scorelabel in self.scorelabels:
				scorelabel.pack_forget()
			self.scorelabels = []
		self.img = Label(self, image=render)
		self.img.image = render
		self.img.pack()
		self.updateButtonStatus()

	def doScore(self):
		if self.score and self.image_filename:
			results = self.score.score(self.image_filename)
			if self.scorelabels:
				for scorelabel in self.scorelabels:
					scorelabel.pack_forget()
				self.scorelabels = []
			for (clazz,prob) in results:
				scorelabel = Label(self,text=str("%s: %f"%(clazz,prob)))
				scorelabel.pack()
				self.scorelabels.append(scorelabel)

if __name__ == "__main__":
	root = Tk()
	app = Window(root)
	root.geometry("400x400")
	app.configure(bg='white')
	app.tk_setPalette(background='white', foreground='black',
					   activeBackground='yellow', activeForeground='black')
	root.mainloop()