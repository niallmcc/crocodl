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

import base64
from visigoth.diagram import Diagram
from visigoth.charts import Line
from visigoth.common import Legend
from visigoth.utils.colour import DiscretePalette

class ChartUtils(object):

    @staticmethod
    def createAccuracyChart(data, total_epochs):
        return ChartUtils.createChart("Accuracy %","accuracy","val_accuracy",lambda y:y*100,data,total_epochs)

    @staticmethod
    def createLossChart(data,total_epochs):
        return ChartUtils.createChart("Loss","loss","val_loss",lambda y:y,data,total_epochs)

    @staticmethod
    def createChart(y_axis,train_key,test_key,y_fn,data,total_epochs):
        dataset = [[idx + 1, y_fn(data[idx][train_key]), "training"] for idx in range(len(data))]
        dataset += [[idx + 1, y_fn(data[idx][test_key]), "test"] for idx in range(len(data))]

        min_y = 0 if len(dataset) == 0 else 10 * (min(map(lambda x: x[1], dataset)) // 10)

        d = Diagram(fill="white")

        palette = DiscretePalette()
        palette.addCategory("training", "red")
        palette.addCategory("test", "blue")

        al = Line(dataset, x=0, y=1, colour=2, width=600, height=200, font_height=14, palette=palette, line_width=5)

        (ax, ay) = al.getAxes()
        ax.setLabel("Epochs")
        ax.setMinValue(0)
        ax.setMaxValue(total_epochs)
        ax.setFontHeight(12)
        ay.setLabel(y_axis)
        ay.setMinValue(min_y)
        ay.setMaxValue(100.0)
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