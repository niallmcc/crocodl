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

from simpledl.image.model_factories.vgg16_factory import VGG16Factory
from simpledl.image.model_factories.mobilenetv2_factory import MobileNetV2Factory

class Factory(object):

    @staticmethod
    def getFactory(architecture):
        if architecture == VGG16Factory.getArchitectureName():
            return VGG16Factory()
        if architecture == MobileNetV2Factory.getArchitectureName():
            return MobileNetV2Factory()
        raise Exception("No factory found for architecture")

    @staticmethod
    def getAvailableArchitectures():
        return [
            VGG16Factory.getArchitectureName(),
            MobileNetV2Factory.getArchitectureName()
        ]

