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

from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from crocodl.runtime.image_utils import ImageUtils
from crocodl.runtime.h5_utils import add_metadata, read_metadata

class ModelUtils(object):

    def __init__(self,architecture_name):
        self.architecture_name = architecture_name
        self.image_size = 224

    def load(self,path):
        metadata = read_metadata(path)
        return metadata, load_model(path)

    def save(self,model,path,metrics):
        model.save(path)
        metadata = {
            "type": "crocodl:classifier",
            "architecture": self.architecture_name,
            "metrics": metrics
        }
        add_metadata(path, metadata)

    # create a transfer learning model
    def createModel(self,training_classes=2,settings={}):
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
        return datagen.flow_from_directory(folder, class_mode='categorical', batch_size=batch_size, target_size=(224, 224))

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

