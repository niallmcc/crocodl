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

## train model (open folder data/dogs_vs_cats for example)

```
python3 -m gui.trainer
```

## score an image (need to train a model first, see above)

```
python3 -m gui.scorer
```

