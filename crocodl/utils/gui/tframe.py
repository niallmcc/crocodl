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

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from crocodl.utils.gui.chart import Chart

class TFrame(ttk.Frame):

    root = None

    def __init__(self, title="", width=500, height=200, *args, **kwargs):

        self.elements = {}
        if TFrame.root is None:
            TFrame.root = tk.Tk()
            self.container = TFrame.root
        else:
            self.container = tk.Toplevel(TFrame.root)
        self.container.geometry("%dx%d"%(width,height))
        self.background = "white"
        super().__init__(self.container, *args, **kwargs)
        self.container.configure(background=self.background)
        self.container.title(title)

        canvas = tk.Canvas(self, bg=self.background)
        vscrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        hscrollbar = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.background)

        def configure_cb(event):
            canvas.configure(scrollregion=canvas.bbox("all"), background=self.background)

        self.scrollable_frame.bind("<Configure>",configure_cb)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=vscrollbar.set,xscrollcommand=hscrollbar.set,background=self.background)

        hscrollbar.pack(side="bottom", fill="x")
        vscrollbar.pack(side="right", fill="y")
        canvas.pack(side="top", fill="both", expand=True)
        self.pack(fill="both", expand=True)

        self.padx = 10
        self.pady = 10

    def setPadding(self,padx,pady):
        self.padx = padx
        self.pady = pady

    def addButton(self,id,text,cb=None,row=0,col=0,columnspan=1,rowspan=1,sticky=None):
        if id in self.elements:
            (old, row, col, columnspan, rowspan, sticky) = self.elements[id]
            old.grid_forget()
        b = tk.Button(self.scrollable_frame, text=text, command=cb, bg=self.background)
        b.grid(row=row, column=col,columnspan=columnspan,rowspan=rowspan,sticky=sticky,padx=self.padx, pady=self.pady)
        if id:
            self.elements[id] = (b,row,col,columnspan,rowspan,sticky)
        return b

    def addSpinbox(self,id,val=0,cb=None,minval=0,maxval=100,row=0,col=0,columnspan=1,rowspan=1,sticky=None):
        if id in self.elements:
            (old, row, col, columnspan, rowspan, sticky) = self.elements[id]
            old.grid_forget()

        if isinstance(val,int):
            v = tk.IntVar(self.container)
            v.set(val)
        else:
            v = tk.DoubleVar(self.container)
            v.set(val)

        sb = tk.Spinbox(self.scrollable_frame, from_=minval, to_=maxval, textvariable=v, command=lambda:cb(v.get()))
        sb.grid(row=row, column=col, columnspan=columnspan,rowspan=rowspan,sticky=sticky,padx=self.padx, pady=self.pady)
        if id:
            self.elements[id] = (sb, row, col, columnspan, rowspan, sticky)
        return sb

    def addLabel(self,id,text="",image=None,row=0,col=0,columnspan=1,rowspan=1,sticky=None,fg="black"):
        if id in self.elements:
            (old,row,col,columnspan,rowspan,sticky) = self.elements[id]
            old.grid_forget()
        if image:
            render = ImageTk.PhotoImage(image)
            lbl = tk.Label(self.scrollable_frame, image=render)
            lbl.image = render
        else:
            lbl = tk.Label(self.scrollable_frame, text=text, fg=fg, bg=self.background)
        lbl.grid(row=row,column=col,columnspan=columnspan,rowspan=rowspan,sticky=sticky,padx=self.padx, pady=self.pady)
        if id:
            self.elements[id] = (lbl, row, col,columnspan,rowspan,sticky)
        return lbl

    def addOptionMenu(self,id,choices,initial_choice,cb,row=0,col=0,columnspan=1,rowspan=1,sticky=None):
        if id in self.elements:
            (old, row, col, columnspan, rowspan, sticky) = self.elements[id]
            old.grid_forget()
        svar = tk.StringVar(self.container)
        svar.set(initial_choice)
        menu = tk.OptionMenu(self.scrollable_frame, svar, *choices, command=cb)
        menu.grid(row=row, column=col, columnspan=columnspan, rowspan=rowspan, sticky=sticky, padx=self.padx, pady=self.pady)
        if id:
            self.elements[id] = (menu, row, col, columnspan, rowspan, sticky)

    def addCanvas(self,id,width,height,row=0,col=0,columnspan=1,rowspan=1,sticky=None):
        if id in self.elements:
            (old, row, col, columnspan, rowspan, sticky) = self.elements[id]
            old.grid_forget()
        canvas = tk.Canvas(self.scrollable_frame,width=width,height=height)
        canvas.grid(row=row, column=col, columnspan=columnspan, rowspan=rowspan, sticky=sticky, padx=self.padx, pady=self.pady)
        if id:
            self.elements[id] = (canvas, row, col, columnspan, rowspan, sticky)
        return canvas

    def addChart(self, id, margin, width, height, range, row=0, col=0, columnspan=1, rowspan=1, sticky=None):
        if id in self.elements:
            (old, row, col, columnspan, rowspan, sticky) = self.elements[id]
            old.grid_forget()
        ((xmin,ymin),(xmax,ymax)) = range
        chart = Chart(self.scrollable_frame,margin=margin,width=width,height=height,xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax)
        chart.grid(row=row, column=col, columnspan=columnspan, rowspan=rowspan, sticky=sticky, padx=self.padx,
                    pady=self.pady)
        if id:
            self.elements[id] = (chart, row, col, columnspan, rowspan, sticky)
        return chart

    def addSeparator(self, id, orient=tk.HORIZONTAL, row=0,col=0,columnspan=1,rowspan=1,sticky="ew",padx=None,pady=None):
        if id in self.elements:
            (old,_,_,_,_,_) = self.elements[id]
            old.grid_forget()

        s = ttk.Separator(self.scrollable_frame,orient=orient)
        if padx is None:
            padx = self.padx
        if pady is None:
            pady = self.pady
        s.grid(row=row,column=col, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        if id:
            self.elements[id] = (s, row, col, columnspan, rowspan, sticky)
        return s

    def removeElement(self,id):
        (element,_,_,_,_,_) = self.elements[id]
        element.grid_forget()
        del self.elements[id]

    def setEnabled(self,id,enabled):
        (element,_,_,_,_,_) = self.elements[id]
        if enabled:
            element.configure(state="normal")
        else:
            element.configure(state="disabled")

    def open(self):
        self.pack()
        self.container.mainloop()

    def close(self):
        if self.container == TFrame.root:
            TFrame.root = None
        self.container.destroy()

