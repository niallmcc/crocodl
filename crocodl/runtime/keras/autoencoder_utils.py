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

from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D
from tensorflow.keras.models import Model, load_model

from crocodl.runtime.image_utils import ImageUtils
from crocodl.runtime.h5_utils import add_metadata, read_metadata



class AutoencoderModelUtils(object):

    AUTOENCODER_BASIC1 = "autoencoder_basic1"
    AUTOENCODER_BASIC2 = "autoencoder_basic2"

    @staticmethod
    def createModelUtils(architecture_name):
        return AutoencoderModelUtils(architecture_name)

    @staticmethod
    def getArchitectureNames():
        return [AutoencoderModelUtils.AUTOENCODER_BASIC1, AutoencoderModelUtils.AUTOENCODER_BASIC2]

    def __init__(self,architecture_name):
        self.architecture_name = architecture_name
        if architecture_name == AutoencoderModelUtils.AUTOENCODER_BASIC1:
            self.image_size = 128
            self.stages = 3
            self.filters = 6
        elif architecture_name == AutoencoderModelUtils.AUTOENCODER_BASIC2:
            self.image_size = 192
            self.stages = 3
            self.filters = 6
        else:
            raise Exception("Architecture %s not recognised")

    def getArchitectureName(self):
        return self.architecture_name

    def getImageSize(self):
        return self.image_size

    def createModel(self):
        input_img = Input(shape=(self.image_size,self.image_size, 3))  # assuming RGB colour channels

        x = input_img

        # for each stage, halve the image size and double the number of filters
        filters = self.filters
        for stage in range(self.stages):
            x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
            x = MaxPooling2D((2, 2), padding='same')(x)
            filters = filters * 2

        # reverse the process to reconstruct the original layer
        for stage in range(self.stages):
            x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
            x = UpSampling2D((2, 2))(x)
            filters = filters // 2

        # final convolution to decode the output
        decoded = Conv2D(3, (2, 2), activation='sigmoid', padding='same')(x)

        autoencoder = Model(input_img, decoded)
        autoencoder.compile(optimizer='adam', loss='mean_squared_error')
        return autoencoder

    def load(self,path):
        metadata = read_metadata(path)
        return metadata,load_model(path)

    def save(self,model,path,metrics):
        model.save(path)
        metadata = {
            "type": "crocodl:autoencoder",
            "architecture": self.architecture_name,
            "metrics": metrics
        }
        add_metadata(path, metadata)


    def getInputIterator(self,folder,batch_size):
        self.datagen = ImageDataGenerator(rescale=1.0 / 255.0)
        return self.datagen.flow_from_directory(
            directory=folder,
            target_size=(self.image_size, self.image_size),
            color_mode="rgb",
            batch_size=batch_size,
            class_mode="input",
            shuffle=True,
            seed=42
        )

    def prepare(self,img):
        img = ImageUtils.convertImage(img,target_size=(self.image_size, self.image_size))
        img_arr = img_to_array(img)
        img_arr = img_arr.reshape(1, self.image_size, self.image_size, 3)
        img_arr = img_arr.astype('float32')
        img_arr *= 1.0/255.0
        return img_arr

    def score(self,model,prepared_image):
        result = model.predict(prepared_image)
        distance = float(np.mean(np.power(result[0]-prepared_image,2)))
        return {"distance":distance}

    def getEmbedding(self,embedding_model,prepared_image):
        sc = self.score(embedding_model,prepared_image)
        return sc

