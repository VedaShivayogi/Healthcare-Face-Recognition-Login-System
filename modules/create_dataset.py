"""KLIKE – Webcam face capture module."""
import cv2
import os

ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data")

def start_capture(name):
    path         = os.path.join(DATA_DIR, name)
    num_of_images = 0
    cascade_path  = os.path.join(DATA_DIR, "haarcascade_frontalface_default.xml")
    detector      = cv2.CascadeClassifier(cascade_path)
    os.makedirs(path, exist_ok=True)
    vid = cv2.VideoCapture(0)

    while True:
        ret, img = vid.read()
        new_img  = None
        grayimg  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face     = detector.detectMultiScale(image=grayimg, scaleFactor=1.1, minNeighbors=5)
        for x, y, w, h in face:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), 2)
            cv2.putText(img, "KLIKE: Face Detected", (x, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 180))
            cv2.putText(img, f"{num_of_images} images captured", (x, y+h+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 180))
            new_img = img[y:y+h, x:x+w]
        cv2.imshow("KLIKE – Face Capture", img)
        key = cv2.waitKey(1) & 0xFF
        try:
            cv2.imwrite(os.path.join(path, f"{num_of_images}{name}.jpg"), new_img)
            num_of_images += 1
        except:
            pass
        if key in (ord("q"), 27) or num_of_images > 300:
            break

    cv2.destroyAllWindows()
    return num_of_images
