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
import json
import subprocess
import requests
import re
import sys

from crocodl.runtime.h5_utils import read_metadata
from crocodl.image.classifier.scorable import Scorable
from crocodl.utils.code_utils import expand_imports

from crocodl.image.model_registry.mobilenetv2_models import MobileNetV2Model

from crocodl.utils.web.browser import Browser

class Trainable(object):

	BATCH_SIZE = "batch_size"
	DEFAULT_BATCH_SIZE = 16

	ARCHITECTURE = "architecture"
	DEFAULT_ARCHITECTURE = MobileNetV2Model.MNET_160

	def __init__(self):
		self.factory = None
		self.model = None
		self.classes = []
		self.metrics = []
		self.model_path = ""
		self.architecture = ""
		self.model_folder = ""
		self.train_folder = ""
		self.test_folder = ""

	def createEmpty(self,path,classes,settings):
		self.architecture = settings[Trainable.ARCHITECTURE]
		self.classes = classes
		self.metrics = []
		self.model_path = path

	def open(self,path):
		metadata = read_metadata(path)
		self.architecture = metadata["architecture"]
		self.classes = metadata["classes"]
		self.metrics = metadata["metrics"]
		self.model_path = path

	def getFactory(self):
		return self.factory

	def getClasses(self):
		return self.classes

	def getMetrics(self):
		return self.metrics

	def isTrained(self):
		return len(self.metrics) > 0

	def train(self,model_folder,train_folder_path,test_folder_path,epoch_callback=None,epochs=5,batch_size=16,completion_callback=None,batch_callback=None):
		self.model_folder = model_folder
		training_classes = list(sorted(os.listdir(train_folder_path)))
		if training_classes != self.classes:
			raise Exception("classes mismatch, unable to train")

		self.batch_callback = batch_callback
		self.epoch_callback = epoch_callback

		self.completed_epochs = len(self.metrics)
		self.completed_batches = 0

		script_path = os.path.join(self.model_folder, "train_classifier.py")

		with open(script_path, "w") as f:
			f.write(Trainable.getCode(self.architecture))

		if self.model_path == "":
			self.model_path = os.path.join(self.model_folder, "model.h5")

		self.tracker_port = Browser.getEphemeralPort()
		self.proc = subprocess.Popen([sys.executable, script_path,
									  "--model_path", self.model_path,
									  "--tracker_port", str(self.tracker_port),
									  "--train_folder", train_folder_path,
									  "--validation_folder", test_folder_path,
									  "--epochs", str(epochs),
									  "--batch_size", str(batch_size),
									  "--architecture", str(self.architecture)],
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
				jo = json.loads(open(json_path, "r").read())
				self.parseResponse(jo)
			completion_callback()

		self.proc = None

	def checkStatus(self):
		try:
			response = requests.get("http://localhost:"+str(self.tracker_port))
			if response.status_code == 200:
				jo = response.json()
				print("STATUS",json.dumps(jo))
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

	def getMetadata(self):
		return {
			"type": "crocodl:classifier",
			"architecture": self.getFactory().getArchitectureName(),
			"classes": self.classes,
			"metrics": self.metrics
		}

	def getScorable(self):
		scorable = Scorable()
		scorable.load(self.model_path)
		return scorable

	@staticmethod
	def getCode(architecture):
		from crocodl.image.model_registry.registry import Registry
		factory = Registry.getModel(architecture)
		script_src_path = os.path.join(os.path.split(__file__)[0], "train_classifier.py")
		code = open(script_src_path, "r").read()
		root_folder = os.path.join(os.path.split(__file__)[0], "..", "..", "..")
		code = code.replace("from crocodl.utils.mobilenetv2_utils import ModelUtils","from %s import ModelUtils"%(factory.getModelUtilsModule()))
		code = expand_imports(code, re.compile("from (crocodl\.utils\.[^ ]*) import .*"), root_folder)
		return code

	def __repr__(self):
		return "(%s, %d classes, %d epochs)"%(self.architecture,len(self.classes),len(self.metrics))

if __name__ == '__main__':
	t = Trainable()
	t.createEmpty("/tmp/model.h5",["cats","dogs"],{"architecture":"MobileNetV2 96x96"})
	t.train(model_folder="/tmp",
			train_folder_path="/home/dev/github/crocodl/data/dogs_vs_cats/train",
			test_folder_path="/home/dev/github/crocodl/data/dogs_vs_cats/test",
			epoch_callback=lambda x,y:print("epoch CB"),
			batch_callback=lambda x,y:print("batch CB"),
			completion_callback=lambda:print("completion CB"))