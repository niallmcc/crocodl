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

import argparse
from PIL import Image
from crocodl.runtime.h5_utils import read_metadata
from crocodl.runtime.score_utils import ScoreServer

from crocodl.runtime.model_utils import createModelUtils

class ImageAutoencoderScore(object):

    def __init__(self, model_path):
        self.model_path = model_path
        self.metadata = read_metadata(self.model_path)
        self.model_utils = createModelUtils(self.metadata["architecture"])
        _,self.model = self.model_utils.load(model_path)

    def score(self, image_path):
        img = Image.open(image_path)
        img_arr = self.model_utils.prepare(img)
        return self.model_utils.score(self.model,img_arr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="/tmp/model.h5", metavar="<MODEL-PATH>")
    parser.add_argument("--port", help="port for serving scores",
                        type=int, default=9099, metavar="<PORT>")

    args = parser.parse_args()
    scorer = ImageAutoencoderScore(args.model_path)
    st = ScoreServer(args.port,scorer)
    st.start()
