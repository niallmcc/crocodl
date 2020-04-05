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
from simpledl.image.model_factories.factory import Factory
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.models import load_model
from simpledl.utils.h5utils import add_metadata, read_metadata
from simpledl.image.classifier.scorable import Scorable

class XCallback(Callback):

	def __init__(self, trainable, callback):
		super(XCallback, self).__init__()
		self.trainable = trainable
		self.cb = callback

	def on_epoch_end(self, epoch, logs=None):
		self.trainable.addEpoch(logs)
		self.cb(epoch, logs)

class Trainable(object):

	BATCH_SIZE = "batch_size"
	DEFAULT_BATCH_SIZE = 16

	ARCHITECTURE = "architecture"
	DEFAULT_ARCHITECTURE = "MobileNetV2"

	def __init__(self):
		self.factory = None
		self.model = None
		self.classes = []
		self.epochs = []

	def createEmpty(self,classes,settings):
		architecture = settings[Trainable.ARCHITECTURE]
		self.factory = Factory.getFactory(architecture)
		self.model = self.factory.createTransferModel(training_classes=len(classes),settings=settings)
		self.classes = classes
		self.epochs = []

	def open(self,path):
		self.model = load_model(path)
		metadata = read_metadata(path)
		self.factory = Factory.getFactory(metadata["architecture"])
		self.classes = metadata["classes"]
		self.epochs = metadata["epochs"]

	def getClasses(self):
		return self.classes

	def getEpochs(self):
		return self.epochs

	def isTrained(self):
		return len(self.epochs) > 0

	def train(self,foldername,epoch_callback=None,epochs=5,completion_callback=None,settings={}):
		self.training_folder = os.path.join(foldername,"train")
		self.testing_folder = os.path.join(foldername,"test")

		training_classes = list(sorted(os.listdir(self.training_folder)))
		if training_classes != self.classes:
			raise Exception("classes mismatch, unable to train")

		batch_size = settings.get(Trainable.BATCH_SIZE,Trainable.DEFAULT_BATCH_SIZE)
		train_it = self.factory.getInputIterator(self.training_folder,batch_size=batch_size)
		test_it = self.factory.getInputIterator(self.testing_folder,batch_size=batch_size)

		callbacks = []
		if epoch_callback:
			callbacks.append(XCallback(self,epoch_callback))

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
			"architecture": self.factory.getArchitectureName(),
			"classes": self.classes,
			"epochs": self.epochs
		}

	def saveModel(self,path):
		self.model.save(path)
		add_metadata(path,self.getMetadata())

	def getScorable(self):
		return Scorable(self.model,self.getMetadata())

	def __repr__(self):
		return "(%s, %d classes, %d epochs)"%(self.factory.getArchitectureName(),len(self.classes),len(self.epochs))