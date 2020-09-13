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
import os

from crocodl.utils.httputils import StatusServer, XCallback
from crocodl.utils.mobilenetv2_utils import ModelUtils

class ImageClassifierTrainer(object):

    def __init__(self,model_path,status_server):
        self.model_path = model_path
        self.status_server = status_server

    def train(self,training_folder,validation_folder,batch_size,epochs,architecture):

        classes = list(sorted(os.listdir(training_folder)))

        utils = ModelUtils(architecture)
        if os.path.exists(self.model_path):
            model = utils.load(self.model_path)
        else:
            model = utils.createTransferModel()

        train_it = utils.getInputIterator(training_folder, batch_size=batch_size)
        test_it = utils.getInputIterator(validation_folder, batch_size=batch_size)

        cb = XCallback()
        callbacks = [cb]

        model.fit(train_it, validation_data=test_it, epochs=epochs, verbose=1, callbacks=callbacks)
        utils.save(model,self.model_path,cb.getLogs(), classes)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="/tmp/model.h5", metavar="<MODEL-PATH>")
    parser.add_argument("--train_folder", help="specify the folder with training data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/train", metavar="<TRAINING-FOLDER>")
    parser.add_argument("--validation_folder", help="specify the folder with validation data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/test", metavar="<TEST-FOLDER>")
    parser.add_argument("--tracker_port", help="port for serving training status",
                    type=int, default=9099, metavar="<TRACKER-PORT>")
    parser.add_argument("--architecture", help="the architecture of the model",
                        type=str, default="", metavar="<ARCHITECTURE>")
    parser.add_argument("--epochs", help="number of training epochs",
                        type=int, default=3, metavar="<NUMBER-OF-EPOCHS>")
    parser.add_argument("--batch_size", help="size of each training batch",
                        type=int, default=16, metavar="<BATCH-SIZE>")

    args = parser.parse_args()
    st = None
    if args.tracker_port > -1:
        st = StatusServer(args.tracker_port)
        st.start()
    t = ImageClassifierTrainer(args.model_path,st)
    t.train(training_folder=args.train_folder,
            validation_folder=args.validation_folder,
            epochs=args.epochs,
            batch_size=args.batch_size,
            architecture=args.architecture)