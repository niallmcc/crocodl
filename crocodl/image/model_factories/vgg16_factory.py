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

from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from crocodl.image.utils.image_utils import ImageUtils
from crocodl.image.model_factories.capability import Capability
from crocodl.image.model_factories.base_factory import BaseFactory

class VGG16Factory(BaseFactory):

    def __init__(self,architecture_name):
        super().__init__(architecture_name)
        pass

    @staticmethod
    def getArchitectureNames():
        return ["VGG16"]

    @staticmethod
    def getCapabilities():
        return { Capability.feature_extraction, Capability.classification }

    def load(self,path):
        return load_model(path)

    # create a transfer learning model
    def createTransferModel(self,training_classes=2,settings={}):
        base_model = VGG16(include_top=False, input_shape=(224, 224, 3))

        for layer in base_model.layers:
            layer.trainable = False

        flat1 = Flatten()(base_model.layers[-1].output)
        class1 = Dense(128, activation='relu', kernel_initializer='he_uniform')(flat1)
        output = Dense(training_classes, activation='softmax')(class1)

        model = Model(inputs=base_model.inputs, outputs=output)

        model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def createEmbeddingModel(self):
        base_model = VGG16(weights="imagenet")
        model = Model(inputs=base_model.input, outputs=base_model.get_layer("fc1").output)
        return model

    def getInputIterator(self,folder,batch_size):
        datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        return  datagen.flow_from_directory(folder, class_mode='categorical', batch_size=batch_size, target_size=(224, 224))

    def prepare(self,img):
        img = ImageUtils.convertImage(img,target_size=(224, 224))
        img_arr = img_to_array(img)
        img_arr = img_arr.reshape(1, 224, 224, 3)
        img_arr = img_arr.astype('float32')
        img_arr = preprocess_input(img_arr)
        return img_arr

    def score(self,model,prepared_image):
        result = model.predict(prepared_image)
        probs = result[0].tolist()
        return probs

    def getEmbedding(self,embedding_model,prepared_image):
        return self.score(embedding_model,prepared_image)

