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