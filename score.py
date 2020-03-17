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

import json
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import load_model

model = load_model('model.h5')
metadata = json.loads(open('model.json').read())

def load_image(filename):
	img = load_img(filename, target_size=(224, 224))
	img = img_to_array(img)
	img = img.reshape(1, 224, 224, 3)
	img = img.astype('float32')
	img = img - [123.68, 116.779, 103.939]
	return img

def score(path):
	img = load_image(path)
	result = model.predict(img)
	probs = result[0]
	classprobs = zip(metadata["classes"],probs)
	return sorted(classprobs,key=lambda x:x[1],reverse=True)[:3]

class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.init_window()
		self.filename = ""
		self.img = None
		self.scorelabels = []

	def init_window(self):
		self.master.title("SimpleDL Image Classifier")
		self.pack(fill=BOTH, expand=1)
		menu = Menu(self.master)
		self.master.config(menu=menu)
		file = Menu(menu)
		file.add_command(label="Load Img", command=self.load_img)
		file.add_command(label="Exit", command=self.client_exit)

		menu.add_cascade(label="File", menu=file)
		scoreButton = Button(self, text="Score",command=self.score)
		scoreButton.pack()

	def load_img(self):
		self.filename = filedialog.askopenfilename(initialdir=".", title="Select Image File", filetypes=(
			("image files", ".jpg .jpeg .png .gif"), ("all files", "*.*")))
		load = Image.open(self.filename)
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