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

from crocodl.image.model_factories.vgg16_factory import VGG16Factory
from crocodl.image.model_factories.mobilenetv2_factory import MobileNetV2Factory

class Factory(object):

    FACTORIES = [MobileNetV2Factory,VGG16Factory]

    @staticmethod
    def getFactory(architecture_name):
        if architecture_name in VGG16Factory.getArchitectureNames():
            return VGG16Factory(architecture_name)
        if architecture_name in MobileNetV2Factory.getArchitectureNames():
            return MobileNetV2Factory(architecture_name)
        raise Exception("No factory found for architecture named %s"%(architecture_name))

    @staticmethod
    def getAvailableArchitectures(capability=None):
        architecture_names = []
        for valid_factory in Factory.FACTORIES:
            if capability is None or capability in valid_factory.getCapabilities():
                architecture_names += valid_factory.getArchitectureNames()
        return architecture_names

