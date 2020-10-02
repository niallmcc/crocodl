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

from flask import Flask, send_from_directory

# flask initialisation and configuration (see config.py)
app = Flask(__name__)
app.config.from_object('config.Config')

from crocodl.utils.log_utils import createLogger

from crocodl.image.web.style_blueprint import style_blueprint
from crocodl.image.web.search_blueprint import search_blueprint
from crocodl.image.web.train_classifier_blueprint import train_classifier_blueprint
from crocodl.image.web.train_autoencoder_blueprint import train_autoencoder_blueprint
from crocodl.image.web.score_classifier_blueprint import score_classifier_blueprint
from crocodl.image.web.score_autoencoder_blueprint import score_autoencoder_blueprint

app.register_blueprint(style_blueprint,url_prefix="/style_transfer")
app.register_blueprint(search_blueprint,url_prefix="/search")
app.register_blueprint(train_classifier_blueprint,url_prefix="/train_classifier")
app.register_blueprint(train_autoencoder_blueprint,url_prefix="/train_autoencoder")
app.register_blueprint(score_classifier_blueprint,url_prefix="/score_classifier")
app.register_blueprint(score_autoencoder_blueprint,url_prefix="/score_autoencoder")

class App(object):
    """
    Define the routes and handlers for the web service
    """

    logger = createLogger("app")


    ####################################################################################################################
    # Service static files
    #

    @staticmethod
    @app.route('/css/<path:path>',methods = ['GET'])
    def send_css(path):
        """serve CSS files"""
        return send_from_directory('static/css', path)

    @staticmethod
    @app.route('/js/<path:path>', methods=['GET'])
    def send_js(path):
        """serve JS files"""
        return send_from_directory('static/js', path)

    @staticmethod
    @app.route('/images/<path:path>', methods=['GET'])
    def send_images(path):
        """serve image files"""
        return send_from_directory('static/images', path)

    @staticmethod
    @app.route('/favicon.ico', methods=['GET'])
    def send_favicon():
        """serve image files"""
        return send_from_directory('static/images', "favicon.ico")

    @staticmethod
    @app.route('/<path:path>', methods=['GET'])
    def fetch(path):
        """Serve the main page containing the form"""
        return send_from_directory('static/html', path)

    @staticmethod
    @app.route('/', methods=['GET'])
    def index():
        """Serve the main page containing the form"""
        return send_from_directory('static/html', 'index.html')


    @app.after_request
    def add_header(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        return r


if __name__ == '__main__':
    from crocodl.utils.web.browser import Browser

    args = Browser.getArgParser().parse_args()
    # start the service and try to open a new browser tab if required
    host = args.host
    port = Browser.getEphemeralPort() if args.port <= 0 else args.port
    if not args.noclient:
        Browser("http://%s:%d/index.html" % (host, port)).launch()
    app.run(host=host, port=port)




