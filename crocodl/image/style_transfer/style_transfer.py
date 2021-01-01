import requests
import sys
import subprocess
import os.path
import re

class StyleTransfer(object):

    code = ""

    @staticmethod
    def getCode():
        return StyleTransfer.code

    def __init__(self,folder="/tmp",iteration_cb=None):
        self.folder = folder
        self.iteration_cb = iteration_cb
        self.output_files = {}
        # files will be "out_at_iteration_X.png" where X is the iteration 0,1,2,...
        self.patt = re.compile("out_at_iteration_([0-9]+)\.png")
        self.proc = None

    def transfer(self,content_image_path,style_image_path,iter=1,content_weight=0.025,style_weight=1.0,tv_weight=1.0):
        self.clearOutput()
        script_path = os.path.join(self.folder,"neural_style_transfer.py")
        open(script_path,"wb").write(StyleTransfer.code)
        args = [sys.executable,script_path,content_image_path,style_image_path,"out",
                        "--iter",str(iter),
                        "--content_weight",str(content_weight),
                        "--style_weight", str(style_weight),
                        "--tv_weight",str(tv_weight)]
        self.proc = subprocess.Popen(args,cwd=self.folder)
        running = True
        while running:
            try:
                self.proc.wait(5)
                running = False
                self.scanOutput()
            except subprocess.TimeoutExpired:
                self.scanOutput()
        self.proc = None

    def cancel(self):
        if self.proc is not None:
            self.proc.terminate()

    def clearOutput(self):
        for filename in os.listdir(self.folder):
            if self.patt.match(filename):
                path = os.path.join(self.folder,filename)
                os.unlink(path)

    def scanOutput(self):
        last_output_files = self.output_files
        self.output_files = {}

        for filename in os.listdir(self.folder):
            m = self.patt.match(filename)
            if m:
                iteration = int(m.group(1))+1
                self.output_files[str(iteration)] = filename
        if self.output_files != last_output_files:
            if self.iteration_cb:
                print(str(self.output_files))
                self.iteration_cb(self.output_files)

response = requests.get("https://github.com/keras-team/keras/raw/f295e8ee39d4ba841ac281a9337d69c7bc5e0eb6/examples/neural_style_transfer.py")
StyleTransfer.code = response.content

if __name__ == '__main__':
    st = StyleTransfer("/tmp")
    st.transfer("/home/dev/tubingen.jpg","/home/dev/starry_night.jpg")
