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

import os.path
import shutil

from flask import current_app

from crocodl.utils.log_utils import createLogger
from crocodl.runtime.h5_utils import read_metadata
from crocodl.image.model_registry.registry import Registry
from crocodl.image.classifier.scorable import Scorable as ScorableClassifier
from crocodl.utils.web.code_formatter import CodeFormatter

class Scorer(object):
    """
    Define the handlers for scoring web services
    """

    def __init__(self):
        self.scorable = None
        self.model_path = ""
        self.image_path = ""
        self.model_loaded = False
        self.architecture = ""

    logger = createLogger("scorer")

    def set_model_path(self,model_path):
        self.model_path = model_path
        self.model_loaded = False
        self.scorable = None

    def load_model(self):
        try:
            metadata = read_metadata(self.model_path)
            self.architecture = metadata["architecture"]
            factory = Registry.getModel(self.architecture)
            self.scorable = self.getScorable()
            self.scorable.load(self.model_path)
            if "metrics" in metadata:
                del metadata["metrics"]
            self.model_loaded = True
            return metadata
        except Exception as ex:
            Scorer.logger.error(ex)

    def score(self):
        if not self.model_loaded:
            self.load_model()
        return self.scorable.score(self.image_path)

    def upload_model(self,path,data):
        model_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "model")
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
        os.makedirs(model_dir)

        self.model_path = os.path.join(model_dir, path)
        open(self.model_path, "wb").write(data)
        return self.load_model()

    def upload_image(self,path,data):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.makedirs(image_dir)

        self.image_path = os.path.join(image_dir, path)
        open(self.image_path, "wb").write(data)

        return "score_image/"+path

    def send_scoreimage(self,path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        return (image_dir, path)

    def send_score_code(self):
        if not self.model_loaded:
            self.load_model()
        if self.model_loaded:
            cf = CodeFormatter()
            if self.getType() == "classifier":
                return cf.formatHTML(ScorableClassifier.getCode(self.architecture))

        return "Select model options to view scoring code"

class ClassifierScorer(Scorer):

    def getType(self):
        return "classifier"

    def getScorable(self):
        return ScorableClassifier()
