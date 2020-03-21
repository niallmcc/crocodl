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

# based on http://code.activestate.com/recipes/580778-tkinter-custom-fonts/

import os.path
from PIL import Image, ImageFont, ImageDraw, ImageTk
from tkinter import Label,Button

raleway_font_path = os.path.join(os.path.split(__file__)[0],"Raleway-Regular.ttf")

def TTF(size,font_path=raleway_font_path):
    return ImageFont.truetype(font_path, size)

raleway_14 = TTF(14)

class ButtonWithFont(Button):

    def __init__(self, root, text, font=raleway_14, colour="black", margin=3, **kwargs):
        (w,h) = font.getsize(text)
        image = Image.new("RGBA", (w+2*margin,h+2*margin), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((margin, margin), text, font=font, fill=colour)

        self._photoimage = ImageTk.PhotoImage(image)
        Button.__init__(self, root, image=self._photoimage, **kwargs)


class LabelWithFont(Label):

    def __init__(self, root, text, font=raleway_14, colour="black", margin=3, **kwargs):
        (w,h) = font.getsize(text)
        image = Image.new("RGBA", (w+2*margin,h+2*margin), color=(0,0,0,0))
        draw = ImageDraw.Draw(image)
        draw.text((margin, margin), text, font=font, fill=colour)
        self._photoimage = ImageTk.PhotoImage(image)
        Label.__init__(self, root, image=self._photoimage, **kwargs)

