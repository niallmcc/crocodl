# simpledl

simple deep learning demo

## installation

```
python3 -m venv ~/simpledl_env
. ~/simpledl_env/bin/activate
pip3 install -r requirements.txt
(cd data; unzip dogs_vs_cats.zip)
```

## train model (dogs vs cats classifier based on VGG16)

```
python3 train.py
```

## score sample images - opens simple gui

```
python3 score.py
```

