import os

BASEDIR = os.path.abspath("./")

STATIC_FILES_DIR = os.path.join(BASEDIR, "static")
if not os.path.exists(STATIC_FILES_DIR):
    os.makedirs(STATIC_FILES_DIR)

IMG_DIR = os.path.join(STATIC_FILES_DIR, "images")
if not os.path.exists(IMG_DIR):
    os.mkdir(IMG_DIR)
