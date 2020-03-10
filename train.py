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

from keras.applications.vgg16 import VGG16
from keras.models import Model
from keras.layers import Dense
from keras.layers import Flatten
from keras.preprocessing.image import ImageDataGenerator

DEFAULT_TRAINING_FOLDER = 'data/dogs_vs_cats/train/'
DEFAULT_TEST_FOLDER = 'data/dogs_vs_cats/test/'

def create_model():

	model = VGG16(include_top=False, input_shape=(224, 224, 3))

	for layer in model.layers:
		layer.trainable = False

	flat1 = Flatten()(model.layers[-1].output)
	class1 = Dense(128, activation='relu', kernel_initializer='he_uniform')(flat1)
	output = Dense(2, activation='softmax')(class1)

	model = Model(inputs=model.inputs, outputs=output)

	model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])
	return model


def train():

	model = create_model()
	print(model.summary())
	# create data generator
	datagen = ImageDataGenerator(featurewise_center=True)
	# use RGB mean values consistent with VGG16 training
	datagen.mean = [123.68, 116.779, 103.939]
	# prepare iterator
	train_it = datagen.flow_from_directory(DEFAULT_TRAINING_FOLDER,
		class_mode='categorical', batch_size=64, target_size=(224, 224))
	test_it = datagen.flow_from_directory(DEFAULT_TEST_FOLDER,
		class_mode='categorical', batch_size=64, target_size=(224, 224))
	# fit model
	model.fit_generator(train_it, validation_data=test_it, epochs=5, verbose=1)
	# save model
	model.save('model.h5')

	classes = list(sorted(os.listdir(DEFAULT_TRAINING_FOLDER)))
	with open("model.json", "w") as f:
		f.write(json.dumps({"classes":classes}))

train()