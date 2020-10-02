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
from PIL import Image
from crocodl.runtime.model_utils import createModelUtils
from crocodl.runtime.h5_utils import read_metadata
from crocodl.image.classifier.score_classifier import ImageClassifier

class ImageClassifierEvaluator(object):

    def __init__(self,model_path):
        self.model_path = model_path

    def evaluate(self,training_folder,validation_folder,report_path):

        metadata = read_metadata(self.model_path)
        architecture = metadata["architecture"]
        metrics = metadata["metrics"]

        classifier = ImageClassifier(self.model_path)
        scores = {}
        stats = {}
        misclassifications = {}
        for (partition,folder) in [("train",training_folder),("test",validation_folder)]:
            partition_scores = {}
            partition_stats = {}
            partition_misclassifications = {}
            classes = os.listdir(folder)
            for actual_cls in classes:
                cls_path = os.path.join(folder, actual_cls)
                if not os.path.isdir(cls_path):
                    continue
                for filename in os.listdir(cls_path):
                    filepath = os.path.join(cls_path,filename)
                    if not os.path.isfile(filepath):
                        continue
                    imagescores = classifier.score(filepath)["scores"]
                    (predicted_cls,_) = imagescores[0]
                    if predicted_cls != actual_cls:
                        mlist = partition_misclassifications.get((predicted_cls,actual_cls),[])
                        mlist.append((filepath,imagescores))
                        partition_misclassifications[(predicted_cls,actual_cls)] = mlist
                    freq = partition_scores.get((predicted_cls,actual_cls),0)
                    partition_scores[(predicted_cls,actual_cls)] = freq+1

                    class_count = partition_stats.get(predicted_cls,0)
                    partition_stats[predicted_cls] = class_count+1

            scores[partition] = partition_scores
            stats[partition] = partition_stats
            misclassifications[partition] = partition_misclassifications

        from crocodl.runtime.chart_utils import ChartUtils
        cu = ChartUtils()

        cu.addClassInfo(stats["train"],stats["test"])

        cu.addAccuracyChart(metrics)
        cu.addLossChart(metrics)

        cu.addConfusionMatrices(metadata["classes"],scores["train"],scores["test"])
        cu.addMisclassificationExamples(misclassifications["train"],misclassifications["test"])
        open(report_path, "w").write(cu.exportHTML())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="/tmp/model.h5", metavar="<MODEL-PATH>")
    parser.add_argument("--train_folder", help="specify the folder with training data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/train", metavar="<TRAINING-FOLDER>")
    parser.add_argument("--validation_folder", help="specify the folder with validation data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/test", metavar="<TEST-FOLDER>")
    parser.add_argument("--report_path", help="path for writing the report",
                    type=str, default="report.html", metavar="<REPORT-PATH>")
    parser.add_argument("--architecture", help="the architecture of the model",
                        type=str, default="", metavar="<ARCHITECTURE>")


    args = parser.parse_args()
    ice = ImageClassifierEvaluator(args.model_path,)

    ice.evaluate(training_folder=args.train_folder,
            validation_folder=args.validation_folder,
                 report_path=args.report_path)