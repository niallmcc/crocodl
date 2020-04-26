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

from tkinter import *

class Chart(Canvas):

    def __init__(self, master, margin=20, width=400, height=400, xmin=0, xmax=1, ymin=0, ymax=0):
        super(Chart,self).__init__(master,width=width+2*margin, height=height+2*margin)

        self.chartm = margin
        self.chart_width = width
        self.chart_height = height

        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

        self.create_text(self.chartm, self.chartm + self.chart_height + self.chartm / 2, text=str(self.xmin))
        self.create_text(self.chartm + self.chart_width, self.chartm + self.chart_height + self.chartm / 2,
                                text=str(self.xmax))
        self.create_text(self.chartm - self.chartm / 2, self.chartm + self.chart_height, text=str(self.ymin))
        self.create_text(self.chartm - self.chartm / 2, self.chartm, text=str(self.ymax))
        self.create_line(self.chartm, self.chart_height + self.chartm, self.chartm + self.chart_width,
                                self.chartm + self.chart_height)
        self.create_line(self.chartm, self.chartm, self.chartm, self.chartm + self.chart_height)

        self.elts_by_colour = {}

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def  plotLine(self,coords,colour):
        if colour in self.elts_by_colour:
            for ele in self.elts_by_colour[colour]:
                self.delete(ele)
        self.elts_by_colour[colour] = []

        dx = self.chart_width / (self.xmax - self.xmin)
        dy = self.chart_height / (self.ymax - self.ymin)

        x0 = None
        y0 = None
        for (x,y) in coords:

            x1 = (x-self.xmin) * dx
            y1 = self.chart_height - (y-self.ymin) * dy

            if x0 is not None and y0 is not None:
                l = self.create_line(x0 + self.chartm, y0 + self.chartm, x1 + self.chartm, y1 + self.chartm, fill=colour)
                self.elts_by_colour[colour].append(y)

            p = self.create_circle(x1 + self.chartm, y1 + self.chartm, 3, fill=colour)
            self.elts_by_colour[colour].append(p)

            x0 = x1
            y0 = y1