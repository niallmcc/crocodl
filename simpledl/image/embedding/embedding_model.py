# https://machinelearningmastery.com/how-to-develop-a-convolutional-neural-network-to-classify-photos-of-dogs-and-cats/
# pip3 install tensorflow keras pillow

import os
import os.path
from PIL import Image
import json

from simpledl.image.embedding.image_store import ImageStore
from simpledl.image.model_factories.factory import Factory

class EmbeddingModel(object):

	ARCHITECTURE="architecture"
	DEFAULT_ARCHITECTURE="VGG16"

	def __init__(self,path):
		self.path = path
		self.imagestore = None
		self.progress_cb = None
		self.imagestore = ImageStore(self.path)
		if not os.path.exists(self.path):
			raise FileNotFoundError(self.path)
		self.imagestore = ImageStore(self.path)

	@staticmethod
	def create(path,architecture):
		if os.path.exists(path):
			os.unlink(path)
		imagestore = ImageStore(path)
		imagestore.setArchitecture(architecture)

	def getArchitecture(self):
		return self.imagestore.getArchitecture()

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

		def process(filepath):
			try:
				image = Image.open(filepath)
				image_data = factory.prepare(image)
				if image_data is not None:
					scores = factory.getEmbedding(model,image_data)
					self.imagestore.addEmbedding(filepath, scores, image)
				return 1
			except Exception as ex:
				raise ex
				# return 0

		counter = 0
		import glob
		for filename in glob.iglob(folder + '/**', recursive=True):
			if os.path.isfile(filename):
				counter += process(filename)
				if counter % 10 == 0:
					self.progress_cb("Loaded " + str(counter) + " images")

		self.imagestore.close()
