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


import tempfile
import os.path
import subprocess
import sys
import requests
from time import sleep
import re

from crocodl.utils.web.browser import Browser

from crocodl.utils.codeutils import expand_imports
from crocodl.utils.h5utils import read_metadata

class Scorable(object):

	def __init__(self):
		self.model_path = None
		self.metadata = None
		self.factory = None
		self.tempfolder = tempfile.TemporaryDirectory()
		self.proc = None

	def load(self,model_path):
		self.model_path = model_path
		self.metadata = read_metadata(model_path)

	def getClasses(self):
		return self.metadata["classes"]

	def startServer(self):
		if self.proc is None:
			script_path = os.path.join(self.tempfolder.name, "score_classifier.py")

			with open(script_path, "w") as f:
				f.write(Scorable.getCode(self.metadata["architecture"]))

			self.port = Browser.getEphemeralPort()
			self.proc = subprocess.Popen([sys.executable, script_path,
									  "--model_path", self.model_path,
									  "--port", str(self.port)],
									 cwd=self.tempfolder.name)


	def score(self,image_path):
		self.startServer()
		retry = 0
		while retry < 5:
			try:
				response = requests.get("http://localhost:"+str(self.port)+image_path)
				if response.status_code == 200:
					return response.json()
			except Exception as ex:
				retry += 1
				sleep(5)

	def close(self):
		self.proc.terminate()
		self.tempfolder.cleanup()
		self.proc = None

	@staticmethod
	def getCode(architecture):
		script_src_path = os.path.join(os.path.split(__file__)[0], "score_autoencoder.py")
		code = open(script_src_path, "r").read()
		return code

if __name__ == '__main__':
	s = Scorable()
	s.load("/tmp/model.h5")
	score = s.score("/home/dev/github/crocodl/data/dogs_vs_cats/train/cats/cat.60.jpg")
	score2 = s.score("/home/dev/github/crocodl/data/dogs_vs_cats/train/dogs/dog.9822.jpg")
	print(str(score))
	print(str(score2))

	s.close()