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