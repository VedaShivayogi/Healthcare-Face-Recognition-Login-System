# 🏥 KLIKE Healthcare Face Recognition Login System

<p align="center">
  <b>A Flask-based healthcare access prototype using PIN authentication and browser-based face recognition.</b>
</p>

<p align="center">
  <a href="https://healthcare-face-recognition-login-system-owew.onrender.com">
    🚀 Live Demo
  </a>
  &nbsp;•&nbsp;
  <a href="https://github.com/VedaShivayogi/Healthcare-Face-Recognition-Login-System">
    💻 GitHub Repository
  </a>
</p>



## 🌐 Live Demo

### 🚀 Try the Application

**Live Demo:**
https://healthcare-face-recognition-login-system-owew.onrender.com

The application is deployed as a Flask web application using Render and Gunicorn.

> **Note:** This is an educational/portfolio prototype. Do not upload real patient or biometric data.



## 📌 Overview

**KLIKE Healthcare Face Recognition Login System** is a healthcare access management prototype designed to provide an additional layer of identity verification using:

* 🔐 PIN-based authentication
* 👤 Face recognition
* 📷 Browser-based webcam capture
* 🏥 Role-based healthcare access
* 📋 Patient and appointment management
* 🚨 Access logs and security alerts
* 📊 Analytics and reports
* 📄 PDF and Excel export

The original project was developed as a desktop-based healthcare application and has been converted into a **Flask web application** so that the system can run through a browser and be deployed on Python hosting platforms.


# ✨ Features

## 🔐 Authentication

* PIN-based authentication
* SHA-256 PIN hashing
* Face verification
* Multi-step authentication workflow
* Session-based login
* Role-based access control

## 👥 User Roles

The system supports different healthcare roles:

* 👑 Admin
* 👨‍⚕️ Doctor
* 👩‍⚕️ Nurse
* 🧑‍🦽 Patient

Each role can access different parts of the application.

## 👤 Face Recognition

The application uses:

* OpenCV
* Haar Cascade face detection
* LBPH (Local Binary Patterns Histograms) face recognition
* Browser webcam access through JavaScript

The browser camera is accessed using:

```javascript
navigator.mediaDevices.getUserMedia()
```

Captured frames are sent to the Flask backend for processing.

## 🏥 Healthcare Management

The prototype provides functionality for:

* Patient records
* Appointment information
* Medical notes
* User management
* Access history
* Security alerts

## 📊 Reports

The system supports generating/exporting:

* Excel reports
* PDF reports
* Access logs
* Security-related information

## 🚨 Security Monitoring

The application includes:

* Access logging
* Failed authentication tracking
* Security alerts
* Role-based permissions
* Hashed PIN storage



# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │       Web Browser       │
                    │                         │
                    │ HTML + CSS + JavaScript │
                    │      Webcam Access      │
                    └────────────┬────────────┘
                                 │
                                 │ HTTP / API
                                 ▼
                    ┌─────────────────────────┐
                    │       Flask App         │
                    │                         │
                    │ Authentication          │
                    │ Role Management         │
                    │ API Routes              │
                    │ Session Management      │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
      ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
      │ Face         │   │ Database     │   │ Reports      │
      │ Recognition  │   │ Services     │   │ Service      │
      │              │   │              │   │              │
      │ OpenCV       │   │ SQLite       │   │ PDF          │
      │ Haar Cascade │   │ Users        │   │ Excel        │
      │ LBPH         │   │ Patients     │   │ Export       │
      └──────────────┘   │ Logs         │   └──────────────┘
                         └──────────────┘
```



# 🛠️ Technology Stack

| Layer             | Technology            |
| ----------------- | --------------------- |
| Frontend          | HTML, CSS, JavaScript |
| Backend           | Python, Flask         |
| Production Server | Gunicorn              |
| Computer Vision   | OpenCV                |
| Face Detection    | Haar Cascade          |
| Face Recognition  | LBPH                  |
| Database          | SQLite                |
| Image Processing  | Pillow                |
| Data Processing   | NumPy                 |
| Excel Reports     | OpenPyXL              |
| PDF Reports       | ReportLab             |
| Deployment        | Render                |
| Version Control   | Git & GitHub          |

--

# 📂 Project Structure

```text
Healthcare-Face-Recognition-Login-System/
│
├── app.py
├── run.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── README.md
├── LICENSE
│
├── services/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── face_recognition.py
│   ├── face_training.py
│   └── reports.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── face_verify.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── doctor.html
│   └── patient.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── camera.js
│       ├── dashboard.js
│       ├── login.js
│       └── register.js
│
├── assets/
│   ├── homepagepic.png
│   └── icon.ico
│
├── config/
│
├── data/
│   └── haarcascade_frontalface_default.xml
│
├── logs/
│
├── modules/
│   └── Legacy desktop modules
│
├── core/
│   └── Legacy desktop application
│
└── docs/
```

---

# 🚀 Run Locally

## 1. Clone the Repository

```bash
git clone https://github.com/VedaShivayogi/Healthcare-Face-Recognition-Login-System.git
```

```bash
cd Healthcare-Face-Recognition-Login-System
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file if required:

```text
SECRET_KEY=your-secret-key
```

Do not commit `.env` to GitHub.

## 5. Start the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000/
```

---

# ☁️ Deployment

The application can be deployed using **Render** or another Python-compatible hosting platform.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn app:app
```

The repository includes:

```text
Procfile
runtime.txt
requirements.txt
```

for deployment configuration.

---

# 🔑 Demo Authentication

The original application contains a default administrative account for development/testing.

```text
Username: Admin
PIN: 0000
```

> For any public deployment, change/remove default credentials and use secure credentials.

---

# 📷 Browser Camera

The web application uses the browser's camera API:

```javascript
navigator.mediaDevices.getUserMedia()
```

The browser will request camera permission before capturing images.

### If the camera does not work:

1. Allow camera permission in the browser.
2. Make sure another application is not using the camera.
3. Use a supported modern browser.
4. Check that the deployment is using HTTPS.
5. Check browser console errors if necessary.

--

# 🤖 Face Recognition Pipeline

The face recognition workflow follows these steps:

```text
Browser Webcam
      │
      ▼
Capture Image
      │
      ▼
Face Detection
(Haar Cascade)
      │
      ▼
Face Region Extraction
      │
      ▼
LBPH Recognition
      │
      ▼
Identity Verification
      │
      ▼
Flask Authentication
      │
      ▼
Role-Based Dashboard
```

---

# 🔐 Security Features

| Feature              | Implementation                              |
| -------------------- | ------------------------------------------- |
| PIN Security         | SHA-256 hashing                             |
| Authentication       | PIN + face verification                     |
| Access Control       | Role-based authorization                    |
| Session Security     | Flask sessions                              |
| Audit Trail          | Access logs                                 |
| Alerts               | Authentication/security alerts              |
| Biometric Protection | Biometric data excluded from source control |
| Environment Secrets  | Environment variables                       |

---

# ⚠️ Privacy & Security Notice

This project handles concepts related to **healthcare information and biometric authentication**.

It is intended strictly as an:

* Educational project
* M.Tech academic project
* Portfolio demonstration
* Software prototype

It is **not a production-ready clinical authentication system**.

Before using a system like this in a real healthcare environment, additional work would be required, including:

* Stronger authentication architecture
* Secure biometric template storage
* Encryption at rest and in transit
* Secure database infrastructure
* Access-control auditing
* Privacy and consent mechanisms
* Data retention policies
* Vulnerability testing
* Regulatory compliance
* Healthcare-specific security controls
* Production-grade monitoring and backup

**Never upload real patient information or personal biometric data to the public demo.**

---

# 🗃️ Data & GitHub Safety

Sensitive biometric and local application data should not be committed to GitHub.

Recommended `.gitignore` entries include:

```text
venv/
.env
__pycache__/
*.pyc

data/faces/
data/Dr.Veda/
data/classifiers/

*.db
logs/*.json
```

This prevents personal face images, local databases, logs, and secrets from being accidentally published.

---

# 📊 Reports

The application supports report generation using:

### Excel

```text
OpenPyXL
```

### PDF

```text
ReportLab
```

Reports can be generated from application data according to the user's role and permissions.

---

# 🐛 Troubleshooting

## Application does not start

Try:

```bash
pip install --upgrade -r requirements.txt
```

Then:

```bash
python app.py
```

Check your Python version:

```bash
python --version
```

---

## OpenCV LBPH Error

If you see:

```text
AttributeError:
module 'cv2' has no attribute 'face'
```

make sure OpenCV Contrib is installed:

```bash
pip uninstall opencv-python -y
pip install opencv-contrib-python
```

For server deployment, use the headless contrib package specified in `requirements.txt`.

Do not install both `opencv-python` and `opencv-contrib-python` together.

---

## Camera Not Working

Check:

* Browser camera permission
* HTTPS connection
* Camera availability
* Browser compatibility
* JavaScript console errors

---

## Face Recognition Accuracy

Recognition performance depends on:

* Lighting
* Camera quality
* Face angle
* Distance from camera
* Training image quality
* Number of training samples
* Recognition threshold

Therefore, a fixed accuracy percentage should not be assumed without a controlled evaluation dataset.

---

# 📈 Future Enhancements

* [ ] PostgreSQL production database
* [ ] Secure biometric template storage
* [ ] Cloud object storage
* [ ] Advanced authentication
* [ ] Multi-factor authentication
* [ ] Mobile application
* [ ] Hospital management system API
* [ ] Advanced analytics dashboard
* [ ] Improved face recognition models
* [ ] Multi-language support
* [ ] Docker deployment
* [ ] Automated testing
* [ ] CI/CD pipeline
* [ ] Security and privacy audit

---

# 🎓 Academic Project

This project was developed as part of an **M.Tech Artificial Intelligence** academic/portfolio project.

### Key AI / Software Concepts Demonstrated

* Computer Vision
* Face Detection
* Face Recognition
* Machine Learning
* Browser-based Camera Processing
* REST/API Development
* Flask Web Development
* Authentication
* Role-Based Access Control
* Database Management
* Report Generation
* Web Deployment

---

# 👩‍💻 Author

**Veda Shivayogi Ramagondanahalli**

M.Tech Artificial Intelligence

### GitHub

https://github.com/VedaShivayogi

### LinkedIn

https://www.linkedin.com/in/vedasram/

---

# 📄 License

This project is licensed under the **MIT License**.

See the [`LICENSE`](./LICENSE) file for details.

---

# ⭐ Support

If you find this project useful for learning or academic purposes, consider giving the repository a ⭐ on GitHub.

---

## 🔗 Project Links

| Resource       | Link                                                                      |
| -------------- | ------------------------------------------------------------------------- |
| 🚀 Live Demo   | https://healthcare-face-recognition-login-system-owew.onrender.com        |
| 💻 GitHub      | https://github.com/VedaShivayogi/Healthcare-Face-Recognition-Login-System |
| 👩‍💻 LinkedIn | https://www.linkedin.com/in/vedasram/                                     |

---

<p align="center">
  <b>🏥 KLIKE Healthcare Face Recognition Login System</b>
  <br>
  Flask • OpenCV • LBPH • SQLite • JavaScript • Render
</p>
