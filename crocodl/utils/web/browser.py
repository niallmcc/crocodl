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

import webbrowser
import time
from threading import Thread

class Browser(Thread):

    def __init__(self,url,delay_secs=3):
        Thread.__init__(self)
        self.url = url
        self.delay_secs = delay_secs

    def launch(self):
        self.start()

    def run(self):
        print("Opening web browser tab/window for %s, please wait..."%(self.url))
        time.sleep(self.delay_secs)
        webbrowser.open_new_tab(self.url)

    @staticmethod
    def getEphemeralPort():
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    @staticmethod
    def getArgParser():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", help="specify the host name",
                            type=str, default="localhost", metavar="<HOST-NAME>")
        parser.add_argument("--port", help="specify the port number",
                            type=int, default=0, metavar="<PORT-NUMBER>")
        parser.add_argument("--noclient", help="do not launch a web client",
                            action="store_true")
        return parser