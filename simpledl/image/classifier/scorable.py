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

from PIL import Image
from tensorflow.keras.models import load_model
from simpledl.utils.h5utils import read_metadata
from simpledl.image.model_factories.factory import Factory

class Scorable(object):

	def __init__(self,model=None,metadata=None):
		self.model = model
		self.metadata = metadata
		self.factory = None

	def load(self,modelpath):
		self.model = load_model(modelpath)
		self.metadata = read_metadata(modelpath)

	def getClasses(self):
		return self.metadata["classes"]

	def score(self,image_path):
		if self.factory == None:
			self.factory = Factory.getFactory(self.metadata["architecture"])

		img = Image.open(image_path)
		img_arr = self.factory.prepare(img)
		result = self.model.predict(img_arr)
		probs = result[0]
		classprobs = zip(self.metadata["classes"],probs)
		return sorted(classprobs,key=lambda x:x[1],reverse=True)[:3]


