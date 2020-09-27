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

from crocodl.image.model_registry.vgg_models import VGGModel
from crocodl.image.model_registry.mobilenetv2_models import MobileNetV2Model
from crocodl.image.model_registry.autoencoder_models import AutoencoderModel

class Registry(object):

    MODELS = [MobileNetV2Model, VGGModel, AutoencoderModel]

    @staticmethod
    def getModel(architecture_name):
        if architecture_name in VGGModel.getArchitectureNames():
            return VGGModel(architecture_name)
        if architecture_name in MobileNetV2Model.getArchitectureNames():
            return MobileNetV2Model(architecture_name)
        if architecture_name in AutoencoderModel.getArchitectureNames():
            return AutoencoderModel(architecture_name)
        raise Exception("No model found for architecture named %s"%(architecture_name))

    @staticmethod
    def getAvailableArchitectures(capability=None):
        architecture_names = []
        for valid_factory in Registry.MODELS:
            if capability is None or capability in valid_factory.getCapabilities():
                architecture_names += valid_factory.getArchitectureNames()
        return architecture_names

