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
from crocodl.image.autoencoder.score_autoencoder import ImageAutoencoderScore

class ImageAutoencoderEvaluator(object):

    def __init__(self,model_path):
        self.model_path = model_path

    def evaluate(self,training_folder,validation_folder,other_folder,report_path):
        print("Evaluating:"+report_path)
        metadata = read_metadata(self.model_path)
        architecture = metadata["architecture"]
        metrics = metadata["metrics"]

        scorer = ImageAutoencoderScore(self.model_path)
        scores = {}
        stats = {}

        for (partition,folder) in [("train",training_folder),("test",validation_folder),(("other",other_folder))]:
            distances = []
            partition_size = 0

            if folder:
                folder = os.path.join(folder,"auto")
                if os.path.isdir(folder):
                    for filename in os.listdir(folder):
                            filepath = os.path.join(folder,filename)
                            if not os.path.isfile(filepath):
                                continue
                            distance = scorer.score(filepath)["distance"]
                            distances.append(distance)
                            partition_size += 1

            scores[partition] = distances
            stats[partition] = {"count":partition_size}


        from crocodl.runtime.chart_utils import ChartUtils
        cu = ChartUtils()

        cu.addAutoencoderInfo(stats["train"],stats["test"],stats.get("other",None))

        cu.addLossChart(metrics)

        cu.addAutoencoderHistograms(scores["train"],scores["test"],scores["other"])

        open(report_path, "w").write(cu.exportHTML())
        print("Evaluated")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="", metavar="<MODEL-PATH>")
    parser.add_argument("--train_folder", help="specify the folder with training data",
                        type=str, default="", metavar="<TRAINING-FOLDER>")
    parser.add_argument("--validation_folder", help="specify the folder with validation data",
                        type=str, default="", metavar="<TEST-FOLDER>")
    parser.add_argument("--other_folder", help="specify the folder with other (anomalous) data",
                       type=str, default="", metavar="<TEST-FOLDER>")
    parser.add_argument("--report_path", help="path for writing the report",
                    type=str, default="report.html", metavar="<REPORT-PATH>")
    parser.add_argument("--architecture", help="the architecture of the model",
                        type=str, default="", metavar="<ARCHITECTURE>")

    args = parser.parse_args()
    iae = ImageAutoencoderEvaluator(args.model_path)

    iae.evaluate(training_folder=args.train_folder,
            validation_folder=args.validation_folder,
                 other_folder=args.other_folder,
                 report_path=args.report_path)