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

from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from crocodl.utils.image_utils import ImageUtils
from crocodl.utils.h5utils import add_metadata

class ModelUtils(object):

    MNET_224 = "MobileNetV2 224x224"
    MNET_192 = "MobileNetV2 192x192"
    MNET_160 = "MobileNetV2 160x160"
    MNET_128 = "MobileNetV2 128x128"
    MNET_96 = "MobileNetV2 96x96"

    def __init__(self,architecture_name):
        self.architecture_name = architecture_name
        if architecture_name == ModelUtils.MNET_224:
            self.image_size = 224
        elif architecture_name == ModelUtils.MNET_192:
            self.image_size = 192
        elif architecture_name == ModelUtils.MNET_160:
             self.image_size = 160
        elif architecture_name == ModelUtils.MNET_128:
            self.image_size = 128
        elif architecture_name == ModelUtils.MNET_96:
            self.image_size = 96
        else:
            raise Exception("Architecture %s not recognised")

    def getArchitectureName(self):
        return self.architecture_name

    def load(self,path):
        return load_model(path)

    def save(self,model,path,logs,classes):
        model.save(path)
        metadata = {
            "type": "crocodl:classifier",
            "architecture": self.architecture_name,
            "epochs": logs,
            "image_size": self.image_size,
            "classes": classes
        }
        add_metadata(path, metadata)

    # create a model for transfer learning
    def createTransferModel(self,training_classes=2,settings={}):
        base_model = MobileNetV2(include_top=False, input_shape=(self.image_size, self.image_size, 3))
        for layer in base_model.layers:
            layer.trainable = False
        flat1 = Flatten()(base_model.layers[-1].output)
        class1 = Dense(128, activation='relu', kernel_initializer='he_uniform')(flat1)
        output = Dense(training_classes, activation='softmax')(class1)
        model = Model(inputs=base_model.inputs, outputs=output)
        model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    # create a model for image embedding
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

