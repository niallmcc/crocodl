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

import base64
from visigoth.diagram import Diagram
from visigoth.charts import Line
from visigoth.common import Legend
from visigoth.utils.colour import DiscretePalette

class ChartUtils(object):

    @staticmethod
    def createAccuracyChart(data, total_epochs):
        return ChartUtils.createChart("Accuracy %","accuracy","val_accuracy",lambda y:y*100,data,total_epochs,100)

    @staticmethod
    def createLossChart(data,total_epochs):
        return ChartUtils.createChart("Loss","loss","val_loss",lambda y:y,data,total_epochs,None)

    @staticmethod
    def createChart(y_axis,train_key,test_key,y_fn,data,total_epochs,max_y):
        dataset = [[idx + 1, y_fn(data[idx][train_key]), "training"] for idx in range(len(data))]
        dataset += [[idx + 1, y_fn(data[idx][test_key]), "test"] for idx in range(len(data))]

        min_y = 0 if len(dataset) == 0 else 10 * (min(map(lambda x: x[1], dataset)) // 10)
        min_x = 0 if total_epochs == 1 else 1

        d = Diagram(fill="white")

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

        d.add(al)

        legend = Legend(al.getPalette(), 400, legend_columns=2, stroke_width=5)
        legend.setDiscreteMarkerStyle('line')

        d.add(legend)
        d.connect(legend, "brushing", al, "brushing")
        d.connect(al, "brushing", legend, "brushing")

        html = d.draw(format="html", include_footer=False)
        return html


    @staticmethod
    def encodeSvgAsDataUri(svg):
        return b'data:image/svg+xml;base64,'+base64.b64encode(svg)

if __name__ == '__main__':
    html = ChartUtils.createAccuracyChart([{"accuracy":0.7,"val_accuracy":0.6},{"accuracy":0.75,"val_accuracy":0.7}],10)
    open("/tmp/test.html","wb").write(html)