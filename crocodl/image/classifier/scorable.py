#    Copyright (C) 2020 crocoDL developers
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import tempfile
import os.path
import subprocess
import sys
import requests
from time import sleep
import re

from crocodl.utils.web.browser import Browser
from crocodl.utils.code_utils import specialise_imports, expand_imports
from crocodl.runtime.h5_utils import read_metadata

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
		print("score")
		self.startServer()
		retry = 0
		while retry < 5:
			try:
				response = requests.get("http://localhost:"+str(self.port)+image_path)
				if response.status_code == 200:
					return response.json()
			except Exception as ex:
				print(ex)
				retry += 1
				sleep(5)

	def close(self):
		self.proc.terminate()
		self.tempfolder.cleanup()
		self.proc = None

	@staticmethod
	def getCode(architecture):
		from crocodl.image.model_registry.registry import Registry
		factory = Registry.getModel(architecture)
		script_src_path = os.path.join(os.path.split(__file__)[0], "score_classifier.py")
		code = open(script_src_path, "r").read()
		root_folder = os.path.join(os.path.split(__file__)[0], "..", "..", "..")
		code = specialise_imports(factory,code)
		code = expand_imports(code, re.compile("from (crocodl\.runtime\.[^ ]*) import .*"), root_folder)
		return code

if __name__ == '__main__':
	s = Scorable()
	s.load("/tmp/model.h5")
	score = s.score("/home/dev/github/crocodl/data/dogs_vs_cats/train/cats/cat.60.jpg")
	print(str(score))
	s.close()