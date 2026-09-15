import io
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CASCADE_PATH = DATA_DIR / "haarcascade_frontalface_default.xml"
CLASSIFIERS_DIR = DATA_DIR / "classifiers"


def sanitize_name(name):
    return "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in str(name).strip())


def _detect_face(gray_frame):
    if not CASCADE_PATH.exists():
        raise FileNotFoundError("Face cascade XML not found.")
    cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
    faces = cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    return faces


def _load_image_from_bytes(image_bytes):
    if not image_bytes:
        raise ValueError("No image data received.")
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(image)
    return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)


def verify_user_face(username, image_bytes, threshold=80):
    if not username:
        return {"success": False, "verified": False, "message": "Username required for face verification."}

    classifier_path = CLASSIFIERS_DIR / f"{sanitize_name(username)}.xml"
    if not classifier_path.exists():
        return {"success": False, "verified": False, "message": "No face model found for this user."}

    try:
        frame = _load_image_from_bytes(image_bytes)
    except Exception:
        return {"success": False, "verified": False, "message": "Unable to decode uploaded image."}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _detect_face(gray)
    if len(faces) == 0:
        return {"success": False, "verified": False, "message": "No face detected."}
    if len(faces) > 1:
        return {"success": False, "verified": False, "message": "Multiple faces detected. Please capture one face only."}

    x, y, w, h = faces[0]
    face_roi = gray[y:y + h, x:x + w]
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(classifier_path))
    label, distance = recognizer.predict(face_roi)
    confidence = max(0, 100 - int(distance))

    if confidence >= threshold:
        return {"success": True, "verified": True, "confidence": confidence, "message": "Identity verified."}

    return {"success": True, "verified": False, "confidence": confidence, "message": "Face not recognized. Confidence below threshold."}


def save_face_sample(username, image_bytes, counter=None):
    username = sanitize_name(username)
    if not username:
        raise ValueError("Username is required to save a sample.")
    sample_dir = DATA_DIR / "faces" / username
    sample_dir.mkdir(parents=True, exist_ok=True)

    try:
        frame = _load_image_from_bytes(image_bytes)
    except Exception as exc:
        raise ValueError(f"Invalid image: {exc}") from exc

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _detect_face(gray)
    if len(faces) == 0:
        raise ValueError("No face detected in the uploaded image.")
    if len(faces) > 1:
        raise ValueError("Multiple faces detected. Please upload one face only.")

    x, y, w, h = faces[0]
    face_roi = gray[y:y + h, x:x + w]
    output_name = f"{counter if counter is not None else len(list(sample_dir.glob('*')))}_{username}.jpg"
    target_path = sample_dir / output_name
    cv2.imwrite(str(target_path), face_roi)
    return str(target_path)
