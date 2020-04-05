# SimpleDL

Simple and easy to use Deep Learning avoiding the need for a GPU or powerful hardware.  

Powered by Tensorflow 2.0, Keras API

Currently supports:

* Image Classification (with transfer learning, based on VGG16 or MobileNetV2)
* Image Search (using image embeddings computed using VGG16 or MobileNetV2)

## Installation

```
python3 -m venv ~/simpledl_env
. ~/simpledl_env/bin/activate
pip3 install -r requirements.txt
(cd data; unzip dogs_vs_cats.zip)
```
## installation - Raspberry Pi 4 - Raspian Buster

pip install of tensorflow may install an older (pre 2.0) tensorflow.  You can try the following steps to manually install tensorflow pre-built (from https://github.com/lhelontra/tensorflow-on-arm/releases).

```
python3 -m venv ~/simpledl_env
. ~/simpledl_env/bin/activate
wget https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.1.0/tensorflow-2.1.0-cp37-none-linux_armv7l.whl
pip install --upgrade pip
pip install tensorflow-2.1.0-cp37-none-linux_armv7l.whl
pip install pillow
sudo apt-get update
sudo apt-get install libatlas-base-dev
sudo apt-get install libhdf5-dev
(cd data; unzip dogs_vs_cats.zip)
```

## Train a Classification Model 

This tool allows you to train a model to classify images.

Open the GUI:

```
python3 -m simpledl.image.gui.trainer
```

* First load the data folder.  Press the `Load Data` button and select the data folder.  

The layout of the data folder groups sets of images into different classes.  

In the example below these classes are named class1, class2 and class3.  You can specify as many classes as you wish and any class names can be used but at least two are required.

```
<data folder>
  train
     class1
        training image files for class1... 
     class2
        training image files for class2...
     class3
        training image files for class3...
  test
     class1
        test image files for class1... 
     class2
        test image files for class2...
     class3
        test image files for class3...
```

The model that you train will try to learn how to classify an image into one of these classes (in the example above, class1, class2 or class3)

For an example data folder layout, see the `data/dogs_vs_cats` folder.

* Next create a new empty model (`Create Model` button) or open an existing model (`Open Model` button) for continued training.  If opening an existing model it must have been trained/created on the same classes as the currently loaded data. 

* You are now ready to (re)train the model.  Press the `Training Settings` button to configure the number of epochs (training steps) and batch size, then press the `Train` button to start training the model.

On each epoch, the model will learn from the images in the train folder, and then its accuracy on the test folder will be assessed.

When each epoch completes, the training graph will be updated with the model accuracy on the training and test data.  

* Once all the epochs have been run, press the `Save Model` button if you wish to save the changes to the model file - IMPORTANT changes to the model are not automatically saved.  

* To test a trained model by scoring a selected image, press the `Score Model...` button.

## Classify an Image 

This tool allows you to make predictions with a pre-trained classifier model.

Open the GUI:

```
python3 -m simpledl.image.gui.scorer
```

* Press the `Load Model` button to select the model to be used to classify the image

* Press the `Load Image` button to select the image to be classified.

* Press the `Score` button to compute the scores.  The predicted classes will be listed in order of decreasing probability.

## Search for similar images

This tool allows you to search through a database of images to try to find those considered similar by the model to a candidate image.

Open the GUI:

```
python3 -m simpledl.image.gui.search
```

* First use `Create Database` or `Open Database` to pick the database to use.

* To add images to a database, use `Select Images Folder` to specify a folder.  Then press `Load Images` to load all images located under this folder into the database.

The database will store a thumbnail of the image. 

* To search the database for similar images, select the image file to search for using the `Load Search Image` button.  Then press the `Search` button.

Thumbnails of the 3 images in the database deemed most similar will be displayed, ranked in order of decreasing similarity, along with a similarity score in the range 0.0 to 1.0.