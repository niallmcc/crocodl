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
import subprocess
import sys
import requests
import json
import re

from crocodl.utils.h5utils import read_metadata
from crocodl.utils.web.browser import Browser
from crocodl.utils.codeutils import expand_imports

class Trainable(object):

	code = ""

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
		self.epochs = []
		self.model_path = ""

	def clearOutput(self):
		model_path = os.path.join(self.folder,"model.h5")
		if os.path.exists(model_path):
			os.unlink(model_path)
		json_path = os.path.join(self.folder,"status.json")
		if os.path.exists(json_path):
			os.unlink(json_path)

	def createEmpty(self,path,classes,metadata):
		self.architecture = metadata[Trainable.ARCHITECTURE]
		self.classes = classes
		self.epochs = []
		self.model_path = path

	def open(self,path):
		metadata = read_metadata(path)
		self.classes = metadata["classes"]
		self.epochs = metadata["epochs"]
		self.architecture = metadata["architecture"]
		self.model_path = path

	def train(self,folder,train_folder_path,test_folder_path,epochs=5,batch_size=16,
			  batch_callback=None,epoch_callback=None,completion_callback=None,):
		self.folder = folder
		self.batch_callback = batch_callback
		self.epoch_callback = epoch_callback
		self.clearOutput()
		self.completed_epochs = 0
		self.completed_batches = 0

		script_path = os.path.join(self.folder, "train_autoencoder.py")

		with open(script_path, "w") as f:
			f.write(Trainable.code)

		if self.model_path == "":
			self.model_path = os.path.join(self.folder, "model.h5")

		self.tracker_port = Browser.getEphemeralPort()
		self.proc = subprocess.Popen([sys.executable, script_path,
									  "--model_path", self.model_path,
									  "--tracker_port", str(self.tracker_port),
									  "--train_folder",train_folder_path,
									  "--validation_folder", test_folder_path,
									  "--epochs", str(epochs),
									  "--batch_size", str(batch_size),
									  "--architecture",str(self.architecture)],
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
				jo = json.loads(open(json_path,"r").read())
				self.epochs = jo["logs"]
				self.parseResponse(jo)
			completion_callback()
		self.proc = None

	def getEpochs(self):
		return self.epochs

	def cancel(self):
		if self.proc is not None:
			self.proc.terminate()

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

	@staticmethod
	def getCode(architecture):
		return Trainable.code

script_src_path = os.path.join(os.path.split(__file__)[0], "train_autoencoder.py")
code = open(script_src_path,"r").read()
root_folder = os.path.join(os.path.split(__file__)[0], "..", "..", "..")
Trainable.code = expand_imports(code,re.compile("from (crocodl\.utils\.[^ ]*) import .*"),root_folder)

if __name__ == '__main__':
	t = Trainable()
	t.createEmpty("", ["cats"], {"architecture":"autoencoder_basic1"})
	t.train(folder="/tmp",
			train_folder_path="/home/dev/github/crocodl/data/cats/train",
			test_folder_path="/home/dev/github/crocodl/data/cats/test")