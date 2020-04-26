from logging import Logger, INFO, StreamHandler, Formatter
import sys

def createLogger(name):
    logger = Logger(name)
    logger.setLevel(INFO)
    sh = StreamHandler(sys.stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
