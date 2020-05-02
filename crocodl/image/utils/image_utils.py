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
import os.path
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