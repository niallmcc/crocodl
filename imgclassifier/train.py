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

from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import Callback

from utils.h5utils import add_metadata

DEFAULT_DATA_FOLDER = 'data/dogs_vs_cats'


class XCallback(Callback):

	def __init__(self, callback):
		super(XCallback, self).__init__()
		self.cb = callback

	def on_epoch_end(self, epoch, logs=None):
		self.cb(epoch, logs)

class Train(object):

	def __init__(self):

		model = VGG16(include_top=False, input_shape=(224, 224, 3))

		for layer in model.layers:
			layer.trainable = False

		flat1 = Flatten()(model.layers[-1].output)
		class1 = Dense(128, activation='relu', kernel_initializer='he_uniform')(flat1)
		output = Dense(2, activation='softmax')(class1)

		self.model = Model(inputs=model.inputs, outputs=output)

		self.model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])


	def train(self,foldername,callback=None,epochs=5,completion_callback=None):

		if not foldername:
			foldername = DEFAULT_DATA_FOLDER

		self.training_folder = os.path.join(foldername,"train")
		self.testing_folder = os.path.join(foldername,"test")
		print(self.model.summary())
		# create data generator
		datagen = ImageDataGenerator(featurewise_center=True)
		# use RGB mean values consistent with VGG16 training
		datagen.mean = [123.68, 116.779, 103.939]
		# prepare iterator
		train_it = datagen.flow_from_directory(self.training_folder,
			class_mode='categorical', batch_size=32, target_size=(224, 224))
		test_it = datagen.flow_from_directory(self.testing_folder,
			class_mode='categorical', batch_size=32, target_size=(224, 224))

		callbacks = []
		if callback:
			callbacks.append(XCallback(callback))

		self.model.fit_generator(train_it, validation_data=test_it, epochs=epochs, verbose=1,
							callbacks=callbacks)
		if completion_callback:
			completion_callback()

	def save_model(self,path):
		self.model.save(path)
		classes = list(sorted(os.listdir(self.training_folder)))
		metadata = {"classes":classes}
		add_metadata(path,metadata)

