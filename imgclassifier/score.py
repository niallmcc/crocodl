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

from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from utils.h5utils import read_metadata

class Score(object):

	def __init__(self,modelpath):
		self.model = load_model(modelpath)
		self.metadata = read_metadata(modelpath)

	@staticmethod
	def load_image(filename):
		img = load_img(filename, target_size=(224, 224))
		img = img_to_array(img)
		img = img.reshape(1, 224, 224, 3)
		img = img.astype('float32')
		img = img - [123.68, 116.779, 103.939]
		return img

	def score(self,imgpath):
		img = Score.load_image(imgpath)
		result = self.model.predict(img)
		probs = result[0]
		classprobs = zip(self.metadata["classes"],probs)
		return sorted(classprobs,key=lambda x:x[1],reverse=True)[:3]


