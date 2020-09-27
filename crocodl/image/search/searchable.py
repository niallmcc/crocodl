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

import os
import re
import os.path
from crocodl.utils.web.browser import Browser
import subprocess
import sys
import json
import requests

from crocodl.utils.code_utils import expand_imports
from crocodl.runtime.image_store import ImageStore

class Searchable(object):

	def __init__(self,imagestore_path,architecture,folder):
		self.imagestore_path = imagestore_path
		self.architecture = architecture
		self.folder = folder

	def clear(self):
		os.path.unlink(self.imagestore_path)

	def __len__(self):
		if os.path.exists(self.imagestore_path):
			istore = ImageStore(self.imagestore_path)
			return len(istore)
		return 0

	def search(self,image_path):
		script_path = os.path.join(self.folder, "search_tool.py")
		results_path = os.path.join(self.folder, "results.json")

		with open(script_path, "w") as f:
			f.write(Searchable.getCode(self.architecture))

		tracker_port = Browser.getEphemeralPort()
		proc = subprocess.Popen([sys.executable, script_path,
									  "--db_path", self.imagestore_path,
									  "--tracker_port", str(tracker_port),
									  "--image_path", image_path,
									  "--architecture", str(self.architecture),
									 "--results_path", results_path],
									 cwd=self.folder)
		running = True
		while running:
			try:
				proc.wait(1)
				running = False
			except subprocess.TimeoutExpired:
				pass
		return json.loads(open(results_path).read())

	def load(self,image_folder,progress_cb=None):
		script_path = os.path.join(self.folder, "search_tool.py")

		with open(script_path, "w") as f:
			f.write(Searchable.getCode(self.architecture))

		tracker_port = Browser.getEphemeralPort()
		proc = subprocess.Popen([sys.executable, script_path,
									  "--db_path", self.imagestore_path,
									  "--tracker_port", str(tracker_port),
									  "--image_folder", image_folder,
									  "--architecture", str(self.architecture)],
									 cwd=self.folder)
		running = True
		while running:
			try:
				proc.wait(1)
				running = False
			except subprocess.TimeoutExpired:
				self.checkStatus(progress_cb,tracker_port)



	def checkStatus(self,progress_cb,port):
		try:
			response = requests.get("http://localhost:" + str(port))
			if response.status_code == 200:
				jo = response.json()
				if progress_cb:
					progress_cb(jo["status"],jo["latest_image_path"],jo["latest_image_uri"])
		except:
			pass

	@staticmethod
	def getCode(architecture):
		from crocodl.image.model_registry.registry import Registry
		factory = Registry.getModel(architecture)
		script_src_path = os.path.join(os.path.split(__file__)[0], "search_tool.py")
		code = open(script_src_path, "r").read()
		root_folder = os.path.join(os.path.split(__file__)[0], "..", "..", "..")
		code = code.replace("from crocodl.utils.mobilenetv2_utils import ModelUtils",
							"from %s import ModelUtils" % (factory.getModelUtilsModule()))
		code = expand_imports(code, re.compile("from (crocodl\.utils\.[^ ]*) import .*"), root_folder)
		return code
