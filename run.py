"""
KLIKE v4 Healthcare Face Recognition System
Flask Render Deployment Version
"""

import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "core"))
sys.path.insert(0, os.path.join(ROOT, "modules"))

from core.app import KlikeApp

# Create Flask App
app_instance = KlikeApp()

# Render/Gunicorn app object
app = app_instance.app

if __name__ == "__main__":
    app_instance.run()
