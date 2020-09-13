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
import json
import subprocess
import requests
import re
import sys


from crocodl.utils.h5utils import read_metadata
from crocodl.image.classifier.scorable import Scorable
from crocodl.utils.codeutils import expand_imports

from crocodl.image.model_factories.mobilenetv2_factory import MobileNetV2Factory

from crocodl.utils.web.browser import Browser

class Trainable(object):

	BATCH_SIZE = "batch_size"
	DEFAULT_BATCH_SIZE = 16

	ARCHITECTURE = "architecture"
	DEFAULT_ARCHITECTURE = MobileNetV2Factory.MNET_160

	def __init__(self):
		self.factory = None
		self.model = None
		self.classes = []
		self.epochs = []
		self.model_path = ""
		self.architecture = ""

	def createEmpty(self,path,classes,settings):
		self.architecture = settings[Trainable.ARCHITECTURE]
		self.classes = classes
		self.epochs = []
		self.model_path = path

	def open(self,path):
		metadata = read_metadata(path)
		self.architecture = metadata["architecture"]
		self.classes = metadata["classes"]
		self.epochs = metadata["epochs"]
		self.model_path = path

	def getFactory(self):
		return self.factory

	def getClasses(self):
		return self.classes

	def getEpochs(self):
		return self.epochs

	def isTrained(self):
		return len(self.epochs) > 0

	def train(self,folder,train_folder_path,test_folder_path,epoch_callback=None,epochs=5,batch_size=16,completion_callback=None,batch_callback=None):
		self.folder = folder
		training_classes = list(sorted(os.listdir(train_folder_path)))
		if training_classes != self.classes:
			raise Exception("classes mismatch, unable to train")

		self.batch_callback = batch_callback
		self.epoch_callback = epoch_callback

		self.completed_epochs = 0
		self.completed_batches = 0

		script_path = os.path.join(self.folder, "train_classifier.py")

		with open(script_path, "w") as f:
			f.write(Trainable.getCode(self.architecture))

		if self.model_path == "":
			self.model_path = os.path.join(self.folder, "model.h5")

		self.tracker_port = Browser.getEphemeralPort()
		self.proc = subprocess.Popen([sys.executable, script_path,
									  "--model_path", self.model_path,
									  "--tracker_port", str(self.tracker_port),
									  "--train_folder", train_folder_path,
									  "--validation_folder", test_folder_path,
									  "--epochs", str(epochs),
									  "--batch_size", str(batch_size),
									  "--architecture", str(self.architecture)],
									 cwd=self.folder)
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

		json_path = os.path.join(self.folder, "status.json")
		if completion_callback:
			if os.path.exists(json_path):
				jo = json.loads(open(json_path, "r").read())
				self.epochs = jo["logs"]
				self.parseResponse(jo)
			completion_callback()
		self.proc = None

	def checkStatus(self):
		try:
			response = requests.get("http://localhost:"+str(self.tracker_port))
			if response.status_code == 200:
				jo = response.json()
				# print("STATUS",json.dumps(jo))
				self.parseResponse(jo)
		except:
			pass

	def parseResponse(self,jo):
		epochs_completed = jo["completed_epoch"]
		batches_completed = jo["completed_batch"]
		if self.batch_callback and \
				(batches_completed > self.completed_batches) or (epochs_completed > self.completed_epochs):
			self.batch_callback(batches_completed, epochs_completed)
			self.completed_batches = batches_completed
		if epochs_completed > self.completed_epochs:
			if self.epoch_callback:
				self.epoch_callback(epochs_completed, jo["logs"])
			self.completed_epochs = epochs_completed
			self.completed_batches = 0
			self.epochs = jo["logs"]

	def addEpoch(self,stats):
		val_acc = float(stats["val_accuracy"])
		acc = float(stats["accuracy"])
		val_loss = float(stats["val_loss"])
		loss = float(stats["loss"])
		self.epochs.append({
			"accuracy":acc,
			"val_accuracy":val_acc,
			"loss":loss,
			"val_loss": val_loss
		})

	def getMetadata(self):
		return {
			"type": "crocodl:classifier",
			"architecture": self.getFactory().getArchitectureName(),
			"classes": self.classes,
			"epochs": self.epochs
		}

	def getPath(self):
		return self.path

	def getScorable(self):
		scorable = Scorable()
		scorable.load(self.model_path)
		return scorable

	@staticmethod
	def getCode(architecture):
		from crocodl.image.model_factories.factory import Factory
		factory = Factory.getFactory(architecture)
		script_src_path = os.path.join(os.path.split(__file__)[0], "train_classifier.py")
		code = open(script_src_path, "r").read()
		root_folder = os.path.join(os.path.split(__file__)[0], "..", "..", "..")
		code = code.replace("from crocodl.utils.mobilenetv2_utils import ModelUtils","from %s import ModelUtils"%(factory.getModelUtilsModule()))
		code = expand_imports(code, re.compile("from (crocodl\.utils\.[^ ]*) import .*"), root_folder)
		return code

	def __repr__(self):
		return "(%s, %d classes, %d epochs)"%(self.factory.getArchitectureName(),len(self.classes),len(self.epochs))

if __name__ == '__main__':
	t = Trainable()
	t.createEmpty("/tmp/model.h5",["cats","dogs"],{"architecture":"MobileNetV2 96x96"})
	t.train(folder="/tmp",
			train_folder_path="/home/dev/github/crocodl/data/dogs_vs_cats/train",
			test_folder_path="/home/dev/github/crocodl/data/dogs_vs_cats/test",epoch_callback=lambda x,y:print("epoch CB"),batch_callback=lambda x,y:print("batch CB"),completion_callback=lambda:print("completion CB"))