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


import os
import subprocess
import sys
import requests
import json
import re

from crocodl.runtime.h5_utils import read_metadata
from crocodl.utils.web.browser import Browser
from crocodl.utils.code_utils import specialise_imports, expand_imports

class Trainable(object):

	BATCH_SIZE = "batch_size"
	DEFAULT_BATCH_SIZE = 16

	ARCHITECTURE = "architecture"
	DEFAULT_ARCHITECTURE = "autoencoder_basic1"

	def __init__(self):
		self.completed_epochs = 0
		self.completed_batches = 0
		self.batch_callback = None
		self.epoch_callback = None
		self.tracker_port = 0
		self.metrics = []
		self.model_path = ""
		self.model_folder = ""
		self.train_folder = ""
		self.test_folder = ""

	def clearOutput(self):
		model_path = os.path.join(self.model_folder,"model.h5")
		if os.path.exists(model_path):
			os.unlink(model_path)
		json_path = os.path.join(self.model_folder,"status.json")
		if os.path.exists(json_path):
			os.unlink(json_path)

	def createEmpty(self,path,classes,metadata):
		self.architecture = metadata[Trainable.ARCHITECTURE]
		self.classes = classes
		self.metrics = []
		self.model_path = path

	def open(self,path):
		metadata = read_metadata(path)
		self.classes = metadata["classes"]
		self.metrics = metadata["metrics"]
		self.architecture = metadata["architecture"]
		self.model_path = path

	def train(self,model_folder,train_folder_path,test_folder_path,epochs=5,batch_size=16,
			  batch_callback=None,epoch_callback=None,completion_callback=None,):
		self.model_folder = model_folder
		self.train_folder = train_folder_path
		self.test_folder = test_folder_path
		self.batch_callback = batch_callback
		self.epoch_callback = epoch_callback
		self.clearOutput()
		self.completed_epochs = 0
		self.completed_batches = 0

		script_path = os.path.join(self.model_folder, "train_autoencoder.py")

		with open(script_path, "w") as f:
			f.write(Trainable.getCode(self.architecture))

		if self.model_path == "":
			self.model_path = os.path.join(self.model_folder, "model.h5")

		self.tracker_port = Browser.getEphemeralPort()
		self.proc = subprocess.Popen([sys.executable, script_path,
									  "--model_path", self.model_path,
									  "--tracker_port", str(self.tracker_port),
									  "--train_folder",self.train_folder,
									  "--validation_folder", self.test_folder,
									  "--epochs", str(epochs),
									  "--batch_size", str(batch_size),
									  "--architecture",str(self.architecture)],
									   cwd=self.model_folder)
		running = True
		self.completed_epochs = 0
		self.completed_batches = 0
		while running:
			try:
				self.proc.wait(1)
				running = False
				self.checkStatus()
			except subprocess.TimeoutExpired:
				self.checkStatus()

		json_path = os.path.join(self.model_folder, "status.json")
		if completion_callback:
			if os.path.exists(json_path):
				jo = json.loads(open(json_path,"r").read())
				self.metrics = jo["metrics"]
				self.parseResponse(jo)
			completion_callback()
		self.proc = None

	def getEpochs(self):
		return self.epochs

	def cancel(self):
		if self.proc is not None:
			self.proc.terminate()
			return True
		else:
			return False

	def checkStatus(self):
		try:
			response = requests.get("http://localhost:"+str(self.tracker_port))
			if response.status_code == 200:
				jo = response.json()
				self.parseResponse(jo)
		except:
			pass

	def parseResponse(self,jo):
		metrics = jo["metrics"]
		epochs_completed = len(metrics)
		batches_completed = jo["completed_batch"]
		if self.batch_callback and \
				(batches_completed > self.completed_batches) or (epochs_completed > self.completed_epochs):
			self.batch_callback(batches_completed, epochs_completed)
			self.completed_batches = batches_completed
		if epochs_completed > self.completed_epochs:
			if self.epoch_callback:
				self.epoch_callback(epochs_completed, metrics)
			self.completed_epochs = epochs_completed
			self.completed_batches = 0
			self.metrics = metrics

	@staticmethod
	def getCode(architecture):
		from crocodl.image.model_registry.registry import Registry
		factory = Registry.getModel(architecture)
		script_src_path = os.path.join(os.path.split(__file__)[0], "train_autoencoder.py")
		code = open(script_src_path, "r").read()
		root_folder = os.path.join(os.path.split(__file__)[0], "..", "..", "..")
		code = specialise_imports(factory,code)
		code = expand_imports(code, re.compile("from (crocodl\.runtime\.[^ ]*) import .*"), root_folder)
		return code

if __name__ == '__main__':
	t = Trainable()
	t.createEmpty("", ["cats"], {"architecture":"autoencoder_basic1"})
	t.train(model_folder="/tmp",
			train_folder_path="/home/dev/github/crocodl/data/cats/train",
			test_folder_path="/home/dev/github/crocodl/data/cats/test")