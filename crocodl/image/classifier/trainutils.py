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