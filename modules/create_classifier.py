"""KLIKE – AI model training module."""
import numpy as np
from PIL import Image
import os
import cv2

ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data")

def train_classifer(name):
    path = os.path.join(DATA_DIR, name)
    faces, ids = [], []

    for root_dir, dirs, files in os.walk(path):
        for pic in files:
            img_path = os.path.join(root_dir, pic)
            img      = Image.open(img_path).convert('L')
            image_np = np.array(img, 'uint8')
            try:
                id_val = int(pic.split(name)[0])
            except ValueError:
                continue
            faces.append(image_np)
            ids.append(id_val)

    ids = np.array(ids)
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)

    out_dir = os.path.join(DATA_DIR, "classifiers")
    os.makedirs(out_dir, exist_ok=True)
    clf.write(os.path.join(out_dir, f"{name}_classifier.xml"))
