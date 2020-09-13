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

import argparse
from PIL import Image
from crocodl.utils.h5utils import read_metadata
from crocodl.utils.scoreutils import ScoreServer

from crocodl.utils.mobilenetv2_utils import ModelUtils

class ImageClassifier(object):

    def __init__(self, model_path):
        self.model_path = model_path
        self.metadata = read_metadata(self.model_path)
        print(self.metadata)
        self.model_utils = ModelUtils(self.metadata["architecture"])
        self.model = self.model_utils.load(model_path)

    def score(self, image_path):
        img = Image.open(image_path)
        img_arr = self.model_utils.prepare(img)
        probs = self.model_utils.score(self.model,img_arr)
        classprobs = zip(self.metadata["classes"], probs)
        # get top 3 in descending rank
        sortedscores = sorted(classprobs, key=lambda x: x[1], reverse=True)
        # ensure results are JSON-serializable
        return {"scores": list(map(lambda x: [x[0], float(x[1])], sortedscores))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="/tmp/model.h5", metavar="<MODEL-PATH>")
    parser.add_argument("--port", help="port for serving scores",
                        type=int, default=9099, metavar="<PORT>")

    args = parser.parse_args()
    scorer = ImageClassifier(args.model_path)
    st = ScoreServer(args.port,scorer)
    st.start()
