import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FACES_DIR = DATA_DIR / "faces"
CLASSIFIERS_DIR = DATA_DIR / "classifiers"


def sanitize_name(name):
    return "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in str(name).strip())


def train_face_model(username):
    username = sanitize_name(username)
    if not username:
        raise ValueError("Username is required before training.")

    user_dir = FACES_DIR / username
    if not user_dir.exists():
        raise FileNotFoundError(f"No training images found for {username}.")

    faces = []
    ids = []
    image_files = sorted(user_dir.glob("*.jpg")) + sorted(user_dir.glob("*.jpeg")) + sorted(user_dir.glob("*.png"))
    if not image_files:
        raise FileNotFoundError(f"No image files found under {user_dir}.")

    for file_path in image_files:
        try:
            image = Image.open(file_path).convert("L")
            image_array = np.array(image, dtype="uint8")
            id_value = 1
            faces.append(image_array)
            ids.append(id_value)
        except Exception:
            continue

    if not faces:
        raise ValueError("No valid training samples were loaded.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))
    CLASSIFIERS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = CLASSIFIERS_DIR / f"{username}.xml"
    recognizer.write(str(model_path))
    return {"success": True, "username": username, "model_path": str(model_path), "images": len(faces)}
