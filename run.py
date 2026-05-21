"""
KLIKE v4 Healthcare Face Recognition System
========================================
Run:  python run.py
"""
import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "core"))
sys.path.insert(0, os.path.join(ROOT, "modules"))

from core.app import KlikeApp
import tkinter as tk

if __name__ == "__main__":
    app = KlikeApp()
    try:
        icon = os.path.join(ROOT, "assets", "icon.ico")
        app.iconphoto(True, tk.PhotoImage(file=icon))
    except Exception:
        pass
    app.mainloop()

