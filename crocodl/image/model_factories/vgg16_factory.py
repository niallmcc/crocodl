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

from crocodl.utils.vgg_utils import ModelUtils as VGGUtils
from crocodl.image.model_factories.capability import Capability
from crocodl.image.model_factories.base_factory import BaseFactory
from crocodl.image.classifier.trainable import Trainable
from crocodl.image.classifier.scorable import Scorable

class VGG16Factory(BaseFactory,VGGUtils):

    def __init__(self,architecture_name):
        super().__init__(architecture_name)

    @staticmethod
    def getArchitectureNames():
        return ["VGG16"]

    @staticmethod
    def getCapabilities():
        return { Capability.feature_extraction, Capability.classification }

    @staticmethod
    def getModelUtilsModule():
        return "crocodl.utils.vgg_utils"

    @staticmethod
    def getTrainable():
        return Trainable()

    @staticmethod
    def getScorable():
        return Scorable()
