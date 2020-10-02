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

from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from crocodl.runtime.image_utils import ImageUtils
from crocodl.runtime.h5_utils import add_metadata, read_metadata

class MobilenetModelUtils(object):

    MNET_224 = "MobileNetV2 224x224"
    MNET_192 = "MobileNetV2 192x192"
    MNET_160 = "MobileNetV2 160x160"
    MNET_128 = "MobileNetV2 128x128"
    MNET_96 = "MobileNetV2 96x96"

    @staticmethod
    def createModelUtils(architecture_name):
        return MobilenetModelUtils(architecture_name)

    @staticmethod
    def getArchitectureNames():
        return [MobilenetModelUtils.MNET_224,
                MobilenetModelUtils.MNET_192,
                MobilenetModelUtils.MNET_160,
                MobilenetModelUtils.MNET_128,
                MobilenetModelUtils.MNET_96]

    def __init__(self,architecture_name):
        self.architecture_name = architecture_name
        if architecture_name == MobilenetModelUtils.MNET_224:
            self.image_size = 224
        elif architecture_name == MobilenetModelUtils.MNET_192:
            self.image_size = 192
        elif architecture_name == MobilenetModelUtils.MNET_160:
             self.image_size = 160
        elif architecture_name == MobilenetModelUtils.MNET_128:
            self.image_size = 128
        elif architecture_name == MobilenetModelUtils.MNET_96:
            self.image_size = 96
        else:
            raise Exception("Architecture %s not recognised")

    def getArchitectureName(self):
        return self.architecture_name

    def load(self,path):
        metadata = read_metadata(path)
        return metadata,load_model(path)

    def save(self,model,path,metrics,classes):
        model.save(path)
        metadata = {
            "type": "crocodl:classifier",
            "architecture": self.architecture_name,
            "metrics": metrics,
            "image_size": self.image_size,
            "classes": classes
        }
        add_metadata(path, metadata)

    # create a model for transfer learning
    def createModel(self,training_classes=2,settings={}):
        base_model = MobileNetV2(include_top=False, input_shape=(self.image_size, self.image_size, 3))
        for layer in base_model.layers:
            layer.trainable = False
        flat1 = Flatten()(base_model.layers[-1].output)
        class1 = Dense(128, activation='relu', kernel_initializer='he_uniform')(flat1)
        output = Dense(training_classes, activation='softmax')(class1)
        model = Model(inputs=base_model.inputs, outputs=output)
        model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    # create a model for image search
    def createEmbeddingModel(self):
        base_model = MobileNetV2(weights="imagenet",input_shape=(self.image_size, self.image_size, 3))
        base_model.summary()
        model = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)
        return model

    def getInputIterator(self,folder,batch_size):
        datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        return datagen.flow_from_directory(folder, class_mode='categorical', batch_size=batch_size, target_size=(self.image_size, self.image_size))

    def prepare(self,img):
        img = ImageUtils.convertImage(img,target_size=(self.image_size, self.image_size))
        img_arr = img_to_array(img)
        img_arr = img_arr.reshape(1, self.image_size, self.image_size, 3)
        img_arr = img_arr.astype('float32')
        img_arr = preprocess_input(img_arr)
        return img_arr

    def score(self,model,prepared_image):
        result = model.predict(prepared_image)
        probs = result[0].tolist()
        return probs

    def getEmbedding(self,embedding_model,prepared_image):
        sc = self.score(embedding_model,prepared_image)
        return sc

