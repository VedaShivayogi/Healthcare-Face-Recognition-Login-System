"""KLIKE – Face recognition / authentication engine."""
import cv2
import os
from time import time
from tkinter import messagebox, simpledialog

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data")

def main_app(name=None, timeout=5):
    if name is None or str(name).strip() == "":
        name = simpledialog.askstring("KLIKE – Input", "Enter registered patient/staff name:")
        if not name:
            messagebox.showerror("KLIKE – Error", "No name provided!")
            return

    face_cascade_path = os.path.join(DATA_DIR, "haarcascade_frontalface_default.xml")
    classifier_path   = os.path.join(DATA_DIR, "classifiers", f"{name}_classifier.xml")

    if not os.path.exists(classifier_path):
        choice = messagebox.askyesno(
            "KLIKE – Profile Not Found",
            f"No biometric profile found for '{name}'.\n\nWould you like to register a new profile?")
        if choice:
            messagebox.showinfo("KLIKE – Info", f"Please complete registration for '{name}' first.")
        else:
            messagebox.showinfo("KLIKE – Cancelled", "Authentication cancelled.")
        return

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    recognizer   = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(classifier_path)

    cap        = cv2.VideoCapture(0)
    pred       = False
    start_time = time()

    while True:
        ret, frame = cap.read()
        if not ret: break
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            try:
                _, confidence = recognizer.predict(roi_gray)
                confidence = 100 - int(confidence)
            except:
                confidence = 0

            if confidence > 50:
                pred  = True
                text  = f"KLIKE: VERIFIED – {name.upper()}"
                color = (0, 220, 180)
            else:
                text  = "KLIKE: IDENTITY UNKNOWN"
                color = (0, 60, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, text, (x, y - 8), cv2.FONT_HERSHEY_PLAIN, 1.2, color, 1)
            cv2.putText(frame, f"Confidence: {confidence}%", (x, y+h+18),
                        cv2.FONT_HERSHEY_PLAIN, 1, color, 1)

        cv2.putText(frame, "KLIKE Healthcare Auth", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 180, 160), 1)
        cv2.imshow("KLIKE – Face Recognition", frame)

        if cv2.waitKey(20) & 0xFF == ord('q'): break
        if time() - start_time >= timeout:      break

    cap.release()
    cv2.destroyAllWindows()

    if pred:
        messagebox.showinfo("KLIKE – Access Granted ✅",
            f"✅  Identity Verified\n\nWelcome, {name}.\nAccess has been granted.")
    else:
        messagebox.showerror("KLIKE – Access Denied ❌",
            "❌  Identity could not be verified.\n\nPlease try again or contact your administrator.")
