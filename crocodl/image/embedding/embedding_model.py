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
import os.path
from PIL import Image

from crocodl.image.embedding.image_store import ImageStore
from crocodl.image.model_factories.factory import Factory
from crocodl.image.utils.image_utils import ImageUtils

# ref: https://machinelearningmastery.com/how-to-develop-a-convolutional-neural-network-to-classify-photos-of-dogs-and-cats/

class EmbeddingModel(object):

	ARCHITECTURE="architecture"
	DEFAULT_ARCHITECTURE="VGG16"

	def __init__(self,imagestore):
		self.imagestore = imagestore
		self.progress_cb = None

	@staticmethod
	def create(path,architecture):
		if os.path.exists(path):
			os.unlink(path)
		imagestore = ImageStore(path)
		imagestore.setArchitecture(architecture)
		return EmbeddingModel(imagestore)

	def getArchitecture(self):
		return self.imagestore.getArchitecture()

	def setArchitecture(self,architecture):
		return self.imagestore.setArchitecture(architecture)

	def clear(self):
		self.imagestore.clear()

	def __len__(self):
		return len(self.imagestore)

	def search(self,image, progress_cb=None):
		factory = Factory.getFactory(self.imagestore.getArchitecture())
		model = factory.createEmbeddingModel()
		scores = factory.getEmbedding(model, factory.prepare(image))
		matches = self.imagestore.similaritySearch(scores,firstN=3,progress_cb=progress_cb)
		return matches

	def train(self,folder,progress_cb=None):
		self.progress_cb = progress_cb
		factory = Factory.getFactory(self.imagestore.getArchitecture())
		model = factory.createEmbeddingModel()
		self.imagestore.open()

		def process(relpath,image):
			image_data = factory.prepare(image)
			if image_data is not None:
				scores = factory.getEmbedding(model,image_data)
				self.imagestore.addEmbedding(relpath, scores, image)

		counter = 0
		import glob
		for filepath in glob.iglob(folder + '/**', recursive=True):
			if os.path.isfile(filepath):
				try:
					image = Image.open(filepath)
					relpath = os.path.relpath(filepath, start=folder)
					process(relpath,image)
					counter += 1
					if counter % 10 == 0:
						self.progress_cb("Loaded " + str(counter) + " images",relpath,ImageUtils.ImageToDataUri(image,160))
				except Exception as ex:
					print(str(ex))
		self.imagestore.close()
