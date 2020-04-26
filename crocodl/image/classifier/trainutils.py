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

import os

def check_data_dir(folder):
	subfolders = os.listdir(folder)
	train_ok = False
	test_ok = False
	for subfolder in subfolders:
		if subfolder == "train":
			train_ok = True
		if subfolder == "test":
			test_ok = True
	if not train_ok or not test_ok:
		return ([],"train and test subfolders not found")
	summary = {}
	for subfolder in ["train","test"]:
		target_folder = os.path.join(folder,subfolder)
		target_summary = {}
		for target_class in os.listdir(target_folder):
			class_folder = os.path.join(target_folder,target_class)
			count = len(os.listdir(class_folder))
			target_summary[target_class] = count
		summary[subfolder] = target_summary
	classes = sorted(list(set(list(set(summary["train"].keys())) + list(set(summary["test"].keys())))))
	summary_text = ""
	for target_class in classes:
		summary_text += target_class
		summary_text += " ("
		for subfolder in ["train","test"]:
			count = summary[subfolder].get(target_class,0)
			summary_text += str(count)
			if subfolder == "train":
				summary_text += ","
		summary_text += " ) "
	return (classes,"")

def getConfusionMatrix(self,folder,scorable):
	results = {} # actual => predicted => count
	classes = scorable.getClasses()
	for actual in classes:
		results[actual] = {}
		for predicted in classes:
			results[actual][predicted] = 0

	for actual in os.listdir(folder):
		clazz_dir = os.path.join(folder,actual)
		for file in os.listdir(clazz_dir):
			image_path = os.path.join(clazz_dir,file)
			scores = scorable.score(image_path)
			predicted = scores[0][0]
			results[actual][predicted] = results[actual][predicted]+1
	return results