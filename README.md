# simpledl

Simple Deep Learning Demo, does not require GPU.  

Currently supports:

* Image Classification (with transfer learning, based on VGG16)

## installation

```
python3 -m venv ~/simpledl_env
. ~/simpledl_env/bin/activate
pip3 install -r requirements.txt
(cd data; unzip dogs_vs_cats.zip)
```

## installation - Raspberry Pi 4 / Raspian Buster

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


## train model (open folder data/dogs_vs_cats for example)

```
python3 -m gui.trainer
```

## score an image (need to train a model first, see above)

```
python3 -m gui.scorer
```

