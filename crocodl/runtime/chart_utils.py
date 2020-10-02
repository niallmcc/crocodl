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

from PIL import Image as PIL_Image
from crocodl.runtime.image_utils import ImageUtils
from io import BytesIO

from visigoth.diagram import Diagram
from visigoth.containers import Grid
from visigoth.charts import Line
from visigoth.common import Legend, Text, Image
from visigoth.charts import Table
from visigoth.utils.colour import DiscretePalette

class ChartUtils(object):

    def __init__(self):
        self.diagram = Diagram(fill="white")
        self.diagram.add(Text("Training Report",font_height=28))

    def addClassInfo(self,training_freqs,test_freqs):
        self.diagram.add(Text("Classes", font_height=24))
        classes = []
        for freqs in [training_freqs,test_freqs]:
            for key in freqs:
                if key not in classes:
                    classes.append(key)
        data = []
        classes = sorted(classes)
        for key in classes:
            training_count = training_freqs.get(key,0)
            testing_count = test_freqs.get(key, 0)
            data.append({"class":key,"training count":training_count,"testing count":testing_count})
        t = Table(data=data,headings=["class","training count","testing count"],font_height=18)
        self.diagram.add(t)

    def addConfusionMatrices(self,classes,training_score_freqs,test_score_freqs):
        self.diagram.add(Text("Confusion Matrix - Training", font_height=24))
        self.addConfusionMatrix(classes,training_score_freqs)
        self.diagram.add(Text("Confusion Matrix - Testing", font_height=24))
        self.addConfusionMatrix(classes, test_score_freqs)

    def addConfusionMatrix(self,classes,score_freqs):
        data = [{} for cls in classes]
        for predicted_class in classes:
            row = classes.index(predicted_class)

            for actual_class in classes:
                freq = score_freqs.get((predicted_class,actual_class),0)
                data[row][actual_class] = freq
                data[row][""] = predicted_class

        t = Table(data=data, headings=[""]+classes, font_height=18, header_text_attributes={})
        g = Grid()
        actual_text = Text("Actual Class",font_height=18)
        predicted_text = Text("Predicted Class",font_height=18)
        g.add(0,1,actual_text)
        g.add(1,0,predicted_text)
        g.add(1,1,t)
        self.diagram.add(g)

    def addMisclassificationExamples(self,training_misclassifications,test_misclassifications):
        self.diagram.add(Text("Example Misclassifications - Training", font_height=24))
        self.addMisclassifications(training_misclassifications)
        self.diagram.add(Text("Example Misclassifications - Testing", font_height=24))
        self.addMisclassifications(test_misclassifications)

    def addMisclassifications(self,misclassifications):
        for (predicted,actual) in misclassifications:
            self.diagram.add(Text("predicted: %s, actual: %s"%(predicted,actual)))
            g = Grid(stroke="grey",stroke_width=2,padding=20)
            imagelist = misclassifications[(predicted,actual)]
            row = 0
            col = 0
            for (path,scores) in imagelist:
                image = PIL_Image.open(path)
                thumbnail_image = ImageUtils.resizeImage(image,160)
                buffered = BytesIO()
                thumbnail_image.save(buffered, format="JPEG")
                content_bytes = buffered.getvalue()

                g.add(row,col,Image(content_bytes=content_bytes,mime_type="image/jpeg"))
                col += 1
                if col > 2:
                    col = 0
                    row += 1
            self.diagram.add(g)

    def addAccuracyChart(self, metrics):
        self.diagram.add(Text("Accuracy", font_height=24))
        total_epochs = len(metrics)
        self.addChart("Accuracy %","accuracy","val_accuracy",lambda y:y*100,metrics,total_epochs,100)

    def addLossChart(self,metrics):
        self.diagram.add(Text("Loss", font_height=24))
        total_epochs = len(metrics)
        self.addChart("Loss","loss","val_loss",lambda y:y,metrics,total_epochs,None)

    def addChart(self,y_axis,train_key,test_key,y_fn,data,total_epochs,max_y):
        dataset = [[idx + 1, y_fn(data[idx][train_key]), "training"] for idx in range(len(data))]
        dataset += [[idx + 1, y_fn(data[idx][test_key]), "test"] for idx in range(len(data))]

        min_y = 0 if len(dataset) == 0 else 10 * (min(map(lambda x: x[1], dataset)) // 10)
        min_x = 0 if total_epochs == 1 else 1

        palette = DiscretePalette()
        palette.addCategory("training", "red")
        palette.addCategory("test", "blue")

        al = Line(dataset, x=0, y=1, colour=2, width=600, height=200, font_height=14, palette=palette, line_width=5)

        (ax, ay) = al.getAxes()
        ax.setLabel("Epochs")
        ax.setMinValue(min_x)
        ax.setMaxValue(total_epochs)
        ax.setFontHeight(12)
        ay.setLabel(y_axis)
        ay.setMinValue(min_y)
        if max_y is not None:
            ay.setMaxValue(max_y)
        ay.setFontHeight(12)

        self.diagram.add(al)

        legend = Legend(al.getPalette(), 400, legend_columns=2, stroke_width=5)
        legend.setDiscreteMarkerStyle('line')

        self.diagram.add(legend)
        self.diagram.connect(legend, "brushing", al, "brushing")
        self.diagram.connect(al, "brushing", legend, "brushing")

    def exportHTML(self):
        return self.diagram.draw(format="html", include_footer=False)


