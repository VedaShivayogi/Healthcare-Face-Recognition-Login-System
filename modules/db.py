"""
KLIKE v4 – Central data manager (JSON-based, no external DB needed).
Handles users, access logs, alerts, patient records, appointments.
"""

import json
import os
import hashlib
from datetime import datetime

ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_DIR  = os.path.join(ROOT, "config")
LOG_DIR  = os.path.join(ROOT, "logs")

USERS_FILE   = os.path.join(CFG_DIR, "users.json")
ACCESS_FILE  = os.path.join(LOG_DIR, "access_log.json")
ALERT_FILE   = os.path.join(LOG_DIR, "alert_log.json")
PATIENTS_FILE = os.path.join(CFG_DIR, "patients.json")
THEME_FILE   = os.path.join(CFG_DIR, "theme.txt")

# ── helpers ──────────────────────────────────────────────────────────────────

def _load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _hash(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today():
    return datetime.now().strftime("%Y-%m-%d")

# ── THEME ────────────────────────────────────────────────────────────────────

def get_theme():
    try:
        with open(THEME_FILE) as f:
            return f.read().strip()
    except Exception:
        return "dark"

def set_theme(mode):
    with open(THEME_FILE, "w") as f:
        f.write(mode)

# ── USERS ────────────────────────────────────────────────────────────────────

def load_users():
    return _load(USERS_FILE, {})

def save_users(users):
    _save(USERS_FILE, users)

def add_user(name, role, pin):
    users = load_users()
    users[name] = {
        "role": role,
        "pin_hash": _hash(pin),
        "created": now(),
        "active": True,
        "failed_attempts": 0
    }
    save_users(users)

def verify_pin(name, pin):
    users = load_users()
    u = users.get(name)
    if not u:
        return False
    return u.get("pin_hash") == _hash(pin)

def get_user(name):
    return load_users().get(name)

def set_user_active(name, active):
    users = load_users()
    if name in users:
        users[name]["active"] = active
        save_users(users)

def increment_failed(name):
    users = load_users()
    if name in users:
        users[name]["failed_attempts"] = users[name].get("failed_attempts", 0) + 1
        save_users(users)

def reset_failed(name):
    users = load_users()
    if name in users:
        users[name]["failed_attempts"] = 0
        save_users(users)

def delete_user(name):
    users = load_users()
    if name in users:
        del users[name]
        save_users(users)

# ── ACCESS LOGS ──────────────────────────────────────────────────────────────

def load_logs():
    return _load(ACCESS_FILE, [])

def log_access(name, role, status, method="face"):
    logs = load_logs()
    logs.append({
        "timestamp": now(),
        "date": today(),
        "name": name,
        "role": role,
        "status": status,   # "granted" | "denied"
        "method": method
    })
    _save(ACCESS_FILE, logs)

# ── ALERTS ───────────────────────────────────────────────────────────────────

def load_alerts():
    return _load(ALERT_FILE, [])

def add_alert(alert_type, detail, name="Unknown"):
    alerts = load_alerts()
    alerts.append({
        "timestamp": now(),
        "type": alert_type,   # "failed_login" | "intruder" | "locked"
        "name": name,
        "detail": detail,
        "read": False
    })
    _save(ALERT_FILE, alerts)

def mark_alerts_read():
    alerts = load_alerts()
    for a in alerts:
        a["read"] = True
    _save(ALERT_FILE, alerts)

def unread_alert_count():
    return sum(1 for a in load_alerts() if not a.get("read"))

# ── PATIENTS ─────────────────────────────────────────────────────────────────

def load_patients():
    return _load(PATIENTS_FILE, {})

def save_patients(patients):
    _save(PATIENTS_FILE, patients)

def add_patient(name, dob, blood_type, conditions, doctor):
    patients = load_patients()
    if name not in patients:
        patients[name] = {
            "dob": dob,
            "blood_type": blood_type,
            "conditions": conditions,
            "doctor": doctor,
            "appointments": [],
            "notes": [],
            "registered": today()
        }
    save_patients(patients)

def get_patient(name):
    return load_patients().get(name)

def add_appointment(name, date, time_val, dept, doctor):
    patients = load_patients()
    if name in patients:
        patients[name]["appointments"].append({
            "date": date, "time": time_val,
            "dept": dept, "doctor": doctor,
            "status": "Scheduled"
        })
        save_patients(patients)

def add_note(name, note_text, author):
    patients = load_patients()
    if name in patients:
        patients[name]["notes"].append({
            "date": now(), "text": note_text, "author": author
        })
        save_patients(patients)
