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
from imgclassifier.score import score

class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.font = TTF(16)
		self.master = master
		self.init_window()
		self.filename = ""
		self.img = None
		self.scorelabels = []

	def init_window(self):
		self.master.title("SimpleDL Image Classifier")
		self.pack(fill=BOTH, expand=1)
		loadButton = ButtonWithFont(self, text="Load Image", font=self.font, command=self.load_img)
		loadButton.pack()

		scoreButton = ButtonWithFont(self, text="Score",font=self.font,command=self.score)
		scoreButton.pack()

	def load_img(self):
		self.filename = filedialog.askopenfilename(initialdir=".", title="Select file",
												   filetypes=(("jpeg files", "*.jpeg"), ("all files", "*.*")))
		load = Image.open(self.filename)
		render = ImageTk.PhotoImage(load)
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

	def client_exit(self):
		exit()

	def score(self):
		if self.filename:
			results = score(self.filename)
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
	root.mainloop()