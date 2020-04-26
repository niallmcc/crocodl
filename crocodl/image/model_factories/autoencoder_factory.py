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

from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ref https://blog.keras.io/building-autoencoders-in-keras.html

datagen = ImageDataGenerator(rescale=1.0/255.0)

SZ=128
EPOCHS=30
STAGES=3

train_it = datagen.flow_from_directory(
    directory="/home/dev/github/crocodl/data/autoencoder_cats/train",
    target_size=(SZ, SZ),
    color_mode="rgb",
    batch_size=32,
    class_mode="input",
    shuffle=True,
    seed=42
)

test_it = datagen.flow_from_directory(
    directory="/home/dev/github/crocodl/data/autoencoder_cats/test",
    target_size=(SZ, SZ),
    color_mode="rgb",
    batch_size=32,
    class_mode="input",
    shuffle=True,
    seed=42
)


input_img = Input(shape=(SZ, SZ, 3))  # adapt this if using `channels_first` image data format

x = input_img
filters = 6
for stage in range(STAGES):
    x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    filters = filters * 2

for stage in range(STAGES):
    x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    filters = filters // 2
decoded = Conv2D(3, (2, 2), activation='sigmoid', padding='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='adam', loss='mean_squared_error')

autoencoder.summary()


from tensorflow.keras.callbacks import TensorBoard
import matplotlib.pyplot as plt

autoencoder.fit(train_it, validation_data=test_it,
                epochs=EPOCHS,
                shuffle=True,
                callbacks=[TensorBoard(log_dir='/tmp/autoencoder')])

autoencoder.save("autocats.h5")
# autoencoder = load_model("autoencoder.h5")

test_inputs = []
test_outputs = []

test_it.reset()

for batch in test_it.next():
    predictions = autoencoder.predict(batch)
    for c in range(10):
        test_inputs.append(batch[c])
        test_outputs.append(predictions[c])

test = []

n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
    # display original
    ax = plt.subplot(2, n, i+1)
    plt.imshow(test_inputs[i].reshape(SZ, SZ, 3))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # display reconstruction
    ax = plt.subplot(2, n, i + 1 + n)
    plt.imshow(test_outputs[i].reshape(SZ, SZ, 3))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()