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

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import json

status = {}

from tensorflow.keras.callbacks import Callback

class XCallback(Callback):

    def __init__(self):
        super(XCallback, self).__init__()
        global status
        status["state"] = "training"
        status["logs"] = []
        status["completed_batch"] = 0
        status["completed_epoch"] = 0

    def on_epoch_end(self, epoch, logs=None):
        global status
        status["logs"].append({"epoch":epoch,"logs":logs})
        status["completed_epoch"] = epoch
        status["completed_batch"] = 0

    def on_batch_end(self, batch, logs=None):
        global status
        status["completed_batch"] = batch

    def on_train_end(self,_):
        global status
        status["state"] = "trained"
        with open("status.json","w") as f:
            f.write(json.dumps(status))

    def getLogs(self):
        return status["logs"]

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

