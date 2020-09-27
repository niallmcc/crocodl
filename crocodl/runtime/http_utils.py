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

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import json

status = {}

from tensorflow.keras.callbacks import Callback

class XCallback(Callback):

    def __init__(self,metrics):
        super(XCallback, self).__init__()
        global status
        self.metrics = metrics
        status["state"] = "training"
        status["metrics"] = self.metrics
        status["completed_batch"] = 0

    def on_epoch_end(self, epoch, logs=None):
        global status
        if logs:
            self.metrics.append(logs)
            status["metrics"] = self.metrics
        status["completed_batch"] = 0

    def on_batch_end(self, batch, logs=None):
        global status
        status["completed_batch"] = batch

    def on_train_end(self,_):
        global status
        status["state"] = "trained"
        with open("status.json","w") as f:
            f.write(json.dumps(status))

    def getMetrics(self):
        return status["metrics"]

class StatusHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write(json.dumps(status).encode('utf-8'))

class StatusServer(Thread):

    def __init__(self,port):
        super().__init__()
        self.port = port
        self.setDaemon(True)

    def run(self):
        httpd = HTTPServer(('localhost', self.port), StatusHandler)
        httpd.serve_forever()
        httpd.server_close()

def set_status(new_status):
    global status
    status = new_status