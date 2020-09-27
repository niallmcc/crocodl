import argparse
import os.path
import json
from PIL import Image

from crocodl.runtime.image_store import ImageStore
from crocodl.runtime.image_utils import ImageUtils
from crocodl.runtime.http_utils import StatusServer, set_status

from crocodl.runtime.keras.mobilenetv2_utils import ModelUtils

class SearchTool(object):

    def __init__(self,architecture,db_path):
        self.architecture = architecture
        self.db_path = db_path

    def open(self):
        if os.path.exists(self.db_path):
            self.imagestore = ImageStore(self.db_path)
            existing_architecture = self.imagestore.getArchitecture()
            if existing_architecture != self.architecture:
                os.unlink(self.db_path)
                self.imagestore = None
        if not self.imagestore:
            self.imagestore = ImageStore(self.db_path)
            self.imagestore.setArchitecture(self.architecture)

        self.architecture = self.imagestore.getArchitecture()
        self.model_utils = ModelUtils(self.architecture)
        self.embedding_model = self.model_utils.createEmbeddingModel()

    def search(self,image_path):
        image = Image.open(image_path)
        scores = self.model_utils.getEmbedding(self.embedding_model, self.model_utils.prepare(image))
        matches = self.imagestore.similaritySearch(scores, firstN=3)
        matches = list(map(lambda x:(x[0],x[1],ImageUtils.ImageToDataUri(x[2], 160)),matches))
        return matches

    def load_images(self,folder):
        self.imagestore.open()

        def process(relpath, image):
            image_data = self.model_utils.prepare(image)
            if image_data is not None:
                scores = self.model_utils.getEmbedding(self.embedding_model, image_data)
                self.imagestore.addEmbedding(relpath, scores, image)

        counter = 0
        import glob
        for filepath in glob.iglob(folder + '/**', recursive=True):
            if os.path.isfile(filepath):
                try:
                    image = Image.open(filepath)
                    relpath = os.path.relpath(filepath, start=folder)
                    process(relpath, image)
                    counter += 1
                    if counter % 10 == 0:
                        set_status({"status":"Loaded %d images"%(counter),
                                    "latest_image_path":relpath,
                                    "latest_image_uri":ImageUtils.ImageToDataUri(image, 160)})
                except Exception as ex:
                    print(str(ex))
        self.imagestore.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--db_path", help="specify the path to the image database",
                        type=str, default="/tmp/image.db", metavar="<MODEL-PATH>")
    parser.add_argument("--image_folder", help="specify the folder with images to load into the database",
                        type=str, default="", metavar="<IMAGE-FOLDER>")
    parser.add_argument("--image_path", help="specify the path of the image to search",
                        type=str, default="",
                        metavar="<IMAGE-PATH>")
    parser.add_argument("--results_path", help="specify the path to the search results",
                        type=str, default="",
                        metavar="<RESULTS-PATH>")
    parser.add_argument("--tracker_port", help="port for services",
                    type=int, default=9099, metavar="<TRACKER-PORT>")
    parser.add_argument("--architecture", help="the architecture of the model",
                        type=str, default="", metavar="<ARCHITECTURE>")

    args = parser.parse_args()
    st = None
    if args.tracker_port > -1:
        st = StatusServer(args.tracker_port)
        st.start()
    st = SearchTool(args.architecture,args.db_path)
    st.open()
    if args.image_folder:
        st.load_images(args.image_folder)
    if args.image_path:
        results = st.search(args.image_path)
        if args.results_path:
            open(args.results_path,"w").write(json.dumps(results))
