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
from crocodl.image.model_factories.factory import Factory
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.models import load_model
from crocodl.utils.h5utils import add_metadata, read_metadata
from crocodl.image.classifier.scorable import Scorable

from crocodl.image.model_factories.mobilenetv2_factory import MobileNetV2Factory

class XCallback(Callback):

	def __init__(self, trainable, epoch_callback, batch_callback=None):
		super(XCallback, self).__init__()
		self.trainable = trainable
		self.epoch_callback = epoch_callback
		self.batch_callback = batch_callback

	def on_epoch_end(self, epoch, logs=None):
		self.trainable.addEpoch(logs)
		if self.epoch_callback:
			self.epoch_callback(epoch, logs)

	def on_batch_end(self, epoch, logs=None):
		if self.batch_callback:
			self.batch_callback(epoch, logs)

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
		self.path = ""

	def createEmpty(self,path,classes,settings):
		architecture = settings[Trainable.ARCHITECTURE]
		self.factory = Factory.getFactory(architecture)
		self.model = self.factory.createTransferModel(training_classes=len(classes),settings=settings)
		self.classes = classes
		self.epochs = []
		self.path = path

	def open(self,path):
		self.model = load_model(path)
		metadata = read_metadata(path)
		self.factory = Factory.getFactory(metadata["architecture"])
		self.classes = metadata["classes"]
		self.epochs = metadata["epochs"]
		self.path = path

	def getFactory(self):
		return self.factory

	def getClasses(self):
		return self.classes

	def getEpochs(self):
		return self.epochs

	def isTrained(self):
		return len(self.epochs) > 0

	def train(self,foldername,epoch_callback=None,epochs=5,batchSize=16,completion_callback=None,batch_callback=None):
		self.training_folder = os.path.join(foldername,"train")
		self.testing_folder = os.path.join(foldername,"test")

		training_classes = list(sorted(os.listdir(self.training_folder)))
		if training_classes != self.classes:
			raise Exception("classes mismatch, unable to train")

		train_it = self.factory.getInputIterator(self.training_folder,batch_size=batchSize)
		test_it = self.factory.getInputIterator(self.testing_folder,batch_size=batchSize)

		callbacks = []
		if epoch_callback or batch_callback:
			callbacks.append(XCallback(self,epoch_callback,batch_callback))

		self.model.fit(train_it, validation_data=test_it, epochs=epochs, verbose=1, callbacks=callbacks)
		if completion_callback:
			completion_callback()

	def addEpoch(self,stats):
		val_acc = float(stats["val_accuracy"])
		acc = float(stats["accuracy"])
		self.epochs.append({
			"accuracy":acc,
			"val_accuracy":val_acc
		})

	def getMetadata(self):
		return {
			"architecture": self.getFactory().getArchitectureName(),
			"classes": self.classes,
			"epochs": self.epochs
		}

	def getPath(self):
		return self.path

	def saveModel(self,path=None):
		if not path:
			path = self.path
		self.model.save(path)
		add_metadata(path,self.getMetadata())

	def getScorable(self):
		return Scorable(self.model,self.getMetadata())

	def __repr__(self):
		return "(%s, %d classes, %d epochs)"%(self.factory.getArchitectureName(),len(self.classes),len(self.epochs))