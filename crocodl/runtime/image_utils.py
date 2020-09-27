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
from io import BytesIO
from PIL import Image

class ImageUtils(object):

    @staticmethod
    def ImageToDataUri(image,max_w=160):
        return 'data:image/jpeg;base64,'+ImageUtils.encodeThumbnail(image,max_w).decode("utf-8")

    @staticmethod
    def resizeImage(image,w):
        wfrac = (w / float(image.size[0]))
        h = int((float(image.size[1]) * wfrac))
        return image.resize((w, h), Image.ANTIALIAS)

    @staticmethod
    def encodeThumbnail(image,max_w=160):
        image_w = image.size[0]
        if image_w > max_w:
            image = ImageUtils.resizeImage(image,max_w)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue())

    @staticmethod
    def decodeThumbnail(s):
        return Image.open(BytesIO(base64.b64decode(s)))

    @staticmethod
    def convertImage(image,color_mode="rgb",target_size=None):
        if color_mode == 'grayscale':
            image = image.convert('L')
        elif color_mode == 'rgb':
            if image.mode != 'RGB':
                image = image.convert('RGB')
        else:
            raise Exception("Invalid color mode %s"%(color_mode))
        if target_size is not None:
            width_height_tuple = (target_size[1], target_size[0])
            if image.size != width_height_tuple:
                image = image.resize(width_height_tuple)
        return image