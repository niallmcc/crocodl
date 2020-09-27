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

import os.path
import shutil
from flask import Flask, request, send_from_directory, jsonify
import threading
from flask import current_app
from crocodl.utils.web.code_formatter import CodeFormatter

from flask import Blueprint

from crocodl.image.style_transfer.style_transfer import StyleTransfer

style_blueprint = Blueprint('style_blueprint', __name__)

from crocodl.utils.log_utils import createLogger

r = None
base_image_path = ""
base_image_url = ""
style_image_path = ""
style_image_url = ""
restyling = False
completed_restyling_iteration = 0
restyling_iterations = 0
restyled_images = {}


class Restyler(threading.Thread):

    def __init__(self,working_dir):
        super().__init__()

        def progress_callback(output_image_paths):
            global restyled_images
            restyled_images = output_image_paths
            global completed_restyling_iteration
            if len(restyled_images) == 0:
                completed_restyling_iteration = 0
            else:
                for iteration in restyled_images:
                    i = int(iteration)
                    if i > completed_restyling_iteration:
                        completed_restyling_iteration = i

        self.working_dir = working_dir
        self.st = StyleTransfer(working_dir,progress_callback)

    def run(self):
        global restyling, restyled_images
        restyling = True
        restyled_images = {}
        self.st.transfer(base_image_path,style_image_path,restyling_iterations)
        restyling = False
        global r
        r = None

    def cancel(self):
        self.st.cancel()


class StyleBlueprint(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("style_transfer")

    ####################################################################################################################
    # Main end points, invoked from index.html
    #

    @staticmethod
    @style_blueprint.route('/restyle',methods = ['POST'])
    def restyler():
        settings = request.json
        global restyling_iterations
        restyling_iterations = settings["nr_iterations"]

        working_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "restyle")
        if os.path.isdir(working_dir):
            shutil.rmtree(working_dir)
        os.makedirs(working_dir)

        global completed_restyling_iteration
        completed_restyling_iteration = 0
        global r
        r = Restyler(working_dir)
        r.start()
        return jsonify({})

    @staticmethod
    @style_blueprint.route('/cancel', methods=['POST'])
    def cancel():
        global r
        if r != None:
            r.cancel()
        return jsonify(True)

    @staticmethod
    @style_blueprint.route('/base_image_upload/<path:path>', methods=['POST'])
    def upload_base_image(path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image", "base")
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.makedirs(image_dir)

        global base_image_path
        base_image_path = os.path.join(image_dir, path)
        open(base_image_path, "wb").write(request.data)

        global base_image_url
        base_image_url = "style_image/base/" + path

        return jsonify({"url":base_image_url})

    @staticmethod
    @style_blueprint.route('/style_image_upload/<path:path>', methods=['POST'])
    def upload_style_image(path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image", "style")
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        os.makedirs(image_dir)

        global style_image_path
        style_image_path = os.path.join(image_dir, path)
        open(style_image_path, "wb").write(request.data)

        global style_image_url
        style_image_url =  "style_image/style/" + path

        return jsonify({"url":style_image_url})

    @staticmethod
    @style_blueprint.route('/style_image/<path:path>', methods=['GET'])
    def send_styleimage(path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "image")
        return send_from_directory(image_dir, path)

    @staticmethod
    @style_blueprint.route('/view_code', methods=['GET'])
    def send_code():
        cf = CodeFormatter()
        html = cf.formatHTML(StyleTransfer.getCode())
        return html

    @staticmethod
    @style_blueprint.route('/restyled_image/<path:path>', methods=['GET'])
    def send_restyledimage(path):
        image_dir = os.path.join(current_app.config["WORKSPACE_DIR"], "restyle")
        return send_from_directory(image_dir, path)



    @staticmethod
    @style_blueprint.route('/status', methods=['GET'])
    def status():
        s = {}
        s["restyling"] = restyling
        if restyling:
            s["restyling_info"] = "Style transfer running: %d/%d iterations"%(completed_restyling_iteration+1,restyling_iterations)
        else:
            s["restyling_info"] = ""
        s["base_image_uploaded"] = base_image_path != ""
        s["style_image_uploaded"] = style_image_path != ""
        s["completed_iterations"] = completed_restyling_iteration
        s["iterations"] = restyling_iterations
        s["restyled_images"] = restyled_images
        s["base_image_url"] = base_image_url
        s["style_image_url"] = style_image_url
        return jsonify(s)


