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

from zipfile import ZipFile
import os

def unpack_data(zip_path,unpack_folder):
    zf = ZipFile(zip_path)
    zf.extractall(unpack_folder)

def locate_testtrain_subdir(folder):
    test_folder= ""
    train_folder = ""
    for f in os.listdir(folder):
        p = os.path.join(folder,f)
        if f == "test" and os.path.isdir(p):
            test_folder = p
        if f == "train" and os.path.isdir(p):
            train_folder = p

    if test_folder and train_folder:
        return (train_folder,test_folder,folder)

    for f in os.listdir(folder):
        p = os.path.join(folder,f)
        if os.path.isdir(p):
            (train_folder,test_folder,parent_folder) = locate_testtrain_subdir(p)
            if parent_folder:
                return (train_folder,test_folder,parent_folder)

    return ("","","")

def get_classes(folder):
    classes = []
    for f in os.listdir(folder):
        p = os.path.join(folder,f)
        if os.path.isdir(p):
            classes.append(f)
    return sorted(classes)