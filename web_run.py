"""
KLIKE v4 Healthcare System - Web Edition
Run on cloud platforms: python web_run.py
"""
import sys, os
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "modules"))

# Import only non-GUI modules
from modules.db import DatabaseManager
from modules.detector import FaceRecognizer

# Flask web server
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CORS(app)

# Initialize modules (without GUI)
db = DatabaseManager()
face_recognizer = FaceRecognizer()

# Simple HTML template as string (or create templates folder)
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>KLIKE v4 Healthcare Login</title>
    <style>
        body { font-family: Arial; margin: 50px; }
        .container { max-width: 500px; margin: auto; padding: 20px; border: 1px solid #ccc; }
        input, button { margin: 10px 0; padding: 8px; width: 100%; }
        video { width: 100%; max-width: 400px; border: 1px solid #ddd; }
        button { background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🏥 KLIKE v4 Healthcare Login</h2>
        <input type="text" id="username" placeholder="Username" />
        <input type="password" id="pin" placeholder="PIN" maxlength="4" />
        <video id="video" autoplay></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <button onclick="captureAndLogin()">Login with Face</button>
        <div id="result"></div>
    </div>
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');
        
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => { video.srcObject = stream; });
        
        async function captureAndLogin() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/jpeg');
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.getElementById('username').value,
                    pin: document.getElementById('pin').value,
                    face_image: imageData
                })
            });
            const result = await response.json();
            document.getElementById('result').innerHTML = 
                '<p>' + (result.message || 'Login ' + (result.success ? 'successful' : 'failed')) + '</p>';
            if (result.success && result.role) {
                window.location.href = '/dashboard/' + result.role;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return LOGIN_HTML

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        username = data.get('username')
        pin = data.get('pin')
        face_image_data = data.get('face_image')
        
        # Verify PIN
        user = db.verify_pin(username, pin)  # You'll need to implement this in db.py
        if not user:
            return jsonify({'success': False, 'message': 'Invalid username or PIN'})
        
        # Decode face image
        if face_image_data and ',' in face_image_data:
            image_base64 = face_image_data.split(',')[1]
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Recognize face
            recognized_user = face_recognizer.recognize(image_cv)
            if recognized_user != username:
                return jsonify({'success': False, 'message': 'Face does not match username'})
        
        # Log access
        db.log_access(username, 'web_login', 'success')
        
        return jsonify({'success': True, 'role': user.get('role', 'patient'), 'message': 'Login successful'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/dashboard/<role>')
def dashboard(role):
    return f'<h1>{role.upper()} Dashboard</h1><p>Welcome to KLIKE v4 Healthcare System</p><a href="/">Logout</a>'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
