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

import argparse

from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ref https://blog.keras.io/building-autoencoders-in-keras.html

from crocodl.utils.httputils import StatusServer, XCallback
from crocodl.utils.h5utils import add_metadata

class AutoEncoderTrainer(object):

    def __init__(self,model_path,status_server):
        self.model_path = model_path
        self.status_server = status_server

    def train(self,training_folder,validation_folder,image_size,batch_size,epochs,stages,filters):
        self.datagen = ImageDataGenerator(rescale=1.0 / 255.0)
        train_it = self.datagen.flow_from_directory(
            directory=training_folder,
            target_size=(image_size, image_size),
            color_mode="rgb",
            batch_size=batch_size,
            class_mode="input",
            shuffle=True,
            seed=42
        )

        test_it = self.datagen.flow_from_directory(
            directory=validation_folder,
            target_size=(image_size, image_size),
            color_mode="rgb",
            batch_size=batch_size,
            class_mode="input",
            shuffle=True,
            seed=42
        )

        input_img = Input(shape=(image_size,image_size, 3))  # assuming RGB colour channels

        x = input_img

        # for each stage, halve the image size and double the number of filters
        for stage in range(stages):
            x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
            x = MaxPooling2D((2, 2), padding='same')(x)
            filters = filters * 2

        # reverse the process to reconstruct the original layer
        for stage in range(stages):
            x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
            x = UpSampling2D((2, 2))(x)
            filters = filters // 2

        # final convolution to decode the output
        decoded = Conv2D(3, (2, 2), activation='sigmoid', padding='same')(x)

        autoencoder = Model(input_img, decoded)
        autoencoder.compile(optimizer='adam', loss='mean_squared_error')

        autoencoder.summary()

        cb = XCallback()
        autoencoder.fit(train_it, validation_data=test_it,
                        epochs=epochs,
                        shuffle=True,
                        callbacks=[cb])

        autoencoder.save(self.model_path)
        metadata = {
            "type": "crocodl:autoencoder",
            "architecture": "",
            "epochs": cb.getLogs()
        }
        add_metadata(self.model_path,metadata)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="/tmp/autoencoder.h5", metavar="<MODEL-PATH>")
    parser.add_argument("--train_folder", help="specify the folder with training data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/train", metavar="<TRAINING-FOLDER>")
    parser.add_argument("--validation_folder", help="specify the folder with validation data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/test", metavar="<TEST-FOLDER>")
    parser.add_argument("--tracker_port", help="port for serving training status",
                    type=int, default=9099, metavar="<TRACKER-PORT>")
    parser.add_argument("--image_size", help="image size presented to the input layer",
                        type=int, default=128, metavar="<INPUT-LAYER-SIZE>")

    parser.add_argument("--epochs", help="number of training epochs",
                        type=int, default=3, metavar="<NUMBER-OF-EPOCHS>")
    parser.add_argument("--batch_size", help="size of each training batch",
                        type=int, default=16, metavar="<BATCH-SIZE>")
    parser.add_argument("--stages", help="number of autoencoder stages",
                        type=int, default=3, metavar="<NUMBER-OF-STAGES>")
    parser.add_argument("--filters", help="number of layer filters",
                        type=int, default=6, metavar="<NUMBER-OF-FILTERS>")

    args = parser.parse_args()
    st = None
    if args.tracker_port > -1:
        st = StatusServer(args.tracker_port)
        st.start()
    t = AutoEncoderTrainer(args.model_path,st)
    t.train(training_folder=args.train_folder,
            validation_folder=args.validation_folder,
            image_size=args.image_size,
            epochs=args.epochs,
            batch_size=args.batch_size,
            stages=args.stages,
            filters=args.filters)