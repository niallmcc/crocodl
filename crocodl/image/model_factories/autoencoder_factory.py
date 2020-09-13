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

from crocodl.image.model_factories.base_factory import BaseFactory
from crocodl.image.model_factories.capability import Capability


class AutoencoderFactory(BaseFactory,object):

    BASIC1 = "autoencoder_basic1"
    BASIC2 = "autoencoder_basic2"

    def __init__(self,architecture_name):
        self.architecture_name = architecture_name
        if architecture_name == AutoencoderFactory.BASIC1:
            self.image_size = 128
            self.stages = 3
            self.filters = 6
        elif architecture_name == AutoencoderFactory.BASIC2:
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
        return [AutoencoderFactory.BASIC1,AutoencoderFactory.BASIC2]

    @staticmethod
    def getCapabilities():
        return { Capability.autoencoder }

    @staticmethod
    def getModelUtilsModule():
        return "crocodl.utils.autoencoder_utils"

    @staticmethod
    def getTrainable():
        from crocodl.image.autoencoder.trainable import Trainable
        return Trainable()

    @staticmethod
    def getScorable():
        from crocodl.image.autoencoder.scorable import Scorable
        return Scorable()







