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
import os.path

from crocodl.runtime.keras.autoencoder_utils import ModelUtils

# ref https://blog.keras.io/building-autoencoders-in-keras.html

from crocodl.runtime.http_utils import StatusServer, XCallback


class AutoEncoderTrainer(object):

    def __init__(self,model_path,status_server,architecture):
        self.model_path = model_path
        self.status_server = status_server
        self.architecture = architecture

    def train(self,training_folder,validation_folder,batch_size,epochs):
        utils = ModelUtils(self.architecture)
        train_it = utils.getInputIterator(training_folder,batch_size)
        test_it = utils.getInputIterator(validation_folder,batch_size)

        if os.path.exists(self.model_path):
            metadata,model = utils.load(self.model_path)
            metrics = metadata["metrics"]
        else:
            model = utils.createModel()
            metrics = []

        cb = XCallback(metrics)
        model.fit(train_it, validation_data=test_it,
                        epochs=epochs,
                        shuffle=True,
                        callbacks=[cb])

        utils.save(model, self.model_path, cb.getMetrics())

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="specify the path to the model",
                        type=str, default="/tmp/autoencoder.h5", metavar="<MODEL-PATH>")
    parser.add_argument("--train_folder", help="specify the folder with training data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/train", metavar="<TRAINING-FOLDER>")
    parser.add_argument("--validation_folder", help="specify the folder with validation data",
                        type=str, default="/home/dev/github/simpledl/data/dogs_vs_cats/test", metavar="<TEST-FOLDER>")
    parser.add_argument("--tracker_port", help="port for serving training status",
                    type=int, default=9099, metavar="<TRACKER-PORT>")
    parser.add_argument("--architecture", help="the model architecture",
                        type=str, default="autoencoder_basic1", metavar="<ARCHITECTURE>")
    parser.add_argument("--epochs", help="number of training epochs",
                        type=int, default=3, metavar="<NUMBER-OF-EPOCHS>")
    parser.add_argument("--batch_size", help="size of each training batch",
                        type=int, default=16, metavar="<BATCH-SIZE>")


    args = parser.parse_args()
    st = None
    if args.tracker_port > -1:
        st = StatusServer(args.tracker_port)
        st.start()


    t = AutoEncoderTrainer(args.model_path, st, args.architecture)
    t.train(training_folder=args.train_folder,
            validation_folder=args.validation_folder,
            epochs=args.epochs,
            batch_size=args.batch_size)