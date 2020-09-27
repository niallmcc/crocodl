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

from crocodl.image.model_registry.base_models import BaseModel
from crocodl.image.model_registry.capability import Capability


class AutoencoderModel(BaseModel, object):

    BASIC1 = "autoencoder_basic1"
    BASIC2 = "autoencoder_basic2"

    def __init__(self,architecture_name):
        self.architecture_name = architecture_name
        if architecture_name == AutoencoderModel.BASIC1:
            self.image_size = 128
            self.stages = 3
            self.filters = 6
        elif architecture_name == AutoencoderModel.BASIC2:
            self.image_size = 256
            self.stages = 4
            self.filters = 6

    def getHyperParameters(self):
        return {
            "--image_size": self.image_size,
            "--stages": self.stages,
            "--filters": self.filters
        }

    @staticmethod
    def getArchitectureNames():
        return [AutoencoderModel.BASIC1, AutoencoderModel.BASIC2]

    @staticmethod
    def getCapabilities():
        return { Capability.autoencoder }

    @staticmethod
    def getModelUtilsModule():
        return "crocodl.runtime.keras.autoencoder_utils"

    @staticmethod
    def getTrainable():
        from crocodl.image.autoencoder.trainable import Trainable
        return Trainable()

    @staticmethod
    def getScorable():
        from crocodl.image.autoencoder.scorable import Scorable
        return Scorable()







