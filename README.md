# crocoDL

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
pip install visigoth
sudo apt-get update
sudo apt-get install libatlas-base-dev
sudo apt-get install libhdf5-dev
(cd data; unzip dogs_vs_cats.zip)
```

## Train a Classification Model 

This service allows you to train a model to classify images.

Start a classification service and open its web page (which should happen automatically):

```
python3 -m simpledl.image.web.train_service
```

* First, in the `Data Settings` section, load the zip file containing the image files to train with.  Press the `Browse` button and select the data zip.  

The layout of the zip file groups sets of images into different classes.  

In the example below these classes are named class1, class2 and class3.  You can specify as many classes as you wish and any class names can be used but at least two are required.

```
root
  train
     class1
        image1.jpg
        image2.jpg
        ... 
     class2
        imageA.jpg
        ...
     class3
        ... 
  test
     class1
        imageX1.jpg
        imageX2.pg
        ...
     class2
        imageA.jpg
        image123.png
        ...
     class3
        ...
```

The model that you train will try to learn how to classify an image into one of these classes (in the example above, class1, class2 or class3)

For an example data folder layout, see the `data/dogs_vs_cats.zip` file.

* Next, in the `Model Settings` section, create a new empty model (`Create Model` button) or open an existing model (`Open Model` button, then browse for the existing model file) for continued training.  
If opening an existing model it must have been trained/created using this program on the same classes as the currently loaded data. 
If creating a new model, you can configure the architecture to be used - which will influence the size of the model, its training speed and its effectiveness on a particular classification task.

* In the `Training Settings` section, if necessary configure the number of epochs (training steps) and batch size (the number of images grouped into in each training batch), then press the `Train` button to start training the model.

* You are now ready to (re)train the model.  Press the `Start Training` button.

On each epoch, the model will learn from the images in the train folder, and then its accuracy on the test folder will be assessed.

When each epoch completes, the training chart will be updated with the model accuracy on the training and test data.  

* Once all the epochs have been run, in the `Download Model` section click on the link if you wish to save the changes to the model file - IMPORTANT changes to the model are not automatically saved.  

## Classify an Image 

This service allows you to make predictions with a pre-trained image classification model.

Start a scoring service and open its web page (which should happen automatically):

```
python3 -m simpledl.image.web.score_service
```

* In the `Model Settings` section select the model to be used to classify the image.  This model will have been downloaded from the classifier service (see above).

* In the `Image` section, select an image to be scored.

* When a model and image have been selected, the predicted classes will be listed in order of decreasing score.

## Search for similar images

This service allows you to create and search through a database of images to try to find those considered similar by the model to a candidate image.

Start a search service and open its web page (which should happen automatically):

```
python3 -m simpledl.image.web.search_service
```

* First use `Create Database` or `Upload Database` in the `Database` section to pick the database to use.

* To add images to a database, use `Choose Zip Containing Image Files` to specify a zip file containing images.  Then press `Load Images` to load all images located under this folder into the database.

for a simple example, you can use the file `data/dogs_vs_cats.zip` file.  The service will search all subfolders in the zip file looking for image files.

The database will store a thumbnail of the image along with an image embedding - a vector of numbers computed by a pre-trained model. 

* To search the database for similar images, in the `Search Database for Similar Images` section, select the image file to search for using the `Load Search Image` button.  Then press the `Search` button.

Thumbnails of the 3 images in the database deemed most similar will be displayed, ranked in order of decreasing similarity, along with a similarity score in the range 0.0 to 1.0.

## Use Neural Style Transfer to restyle an image

This service allows you to alter an image by borrowing the *style* from a different image.  This service downloads and runs the keras team's script `neural_style_transfer.py` described in https://keras.io/examples/neural_style_transfer/

For more details of the approach used please see https://arxiv.org/abs/1508.06576

Start a style transfer service and open its web page (which should happen automatically):

```
python3 -m simpledl.image.web.style_transfer_app
```

* First, in the `Input Images` section, upload the image to transform and the image from which the style is to be borrowed from your computer.  

For example, try the images from the repo: `data/style_transfer/tubingen.jpg` and `data/style_transfer/starry_night.jpg` respectively.

* Then specify the number of iterations to perform in the `Style Transfer Process` section and press `Start Restyling` to begin the restyling process.  Each iteration may a couple of minutes or more.

* During restyling, in the `Results` section the images produced by each iteration can be viewed.  Use `Right click` + `Save Image As...` to save images to your computer.

* Using the same images discussed in the paper, we see the following transformation after 1 iteration:

Main Input Image:

<img src="https://raw.githubusercontent.com/niallmcc/crocodl/master/data/style_transfer/tubingen.jpg" width="512" />

Style Input Image:

<img src="https://raw.githubusercontent.com/niallmcc/crocodl/master/data/style_transfer/starry_night.jpg" width="384" />

Restyled Main Input:

<img src="https://raw.githubusercontent.com/niallmcc/crocodl/master/data/style_transfer/starry_tubingen.png" width="512" />
