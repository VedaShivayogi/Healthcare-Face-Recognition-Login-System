import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
LOG_DIR = ROOT / "logs"
DB_PATH = DATA_DIR / "klike.db"
USERS_JSON_PATH = CONFIG_DIR / "users.json"
PATIENTS_JSON_PATH = CONFIG_DIR / "patients.json"


def ensure_directories():
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "faces").mkdir(exist_ok=True)
    (DATA_DIR / "classifiers").mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)


def get_connection():
    ensure_directories()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def _hash_password(pin):
    return generate_password_hash(str(pin), method="pbkdf2:sha256")


def _normalize_name(name):
    return (name or "").strip()


def _legacy_pin_matches(stored_hash, pin):
    if not stored_hash:
        return False
    if isinstance(stored_hash, str) and stored_hash.startswith("pbkdf2"):
        from werkzeug.security import check_password_hash

        return check_password_hash(stored_hash, str(pin))
    if isinstance(stored_hash, str) and len(stored_hash) == 64:
        import hashlib

        return hashlib.sha256(str(pin).encode("utf-8")).hexdigest() == stored_hash
    return False


def _migrate_legacy_json_data():
    if not USERS_JSON_PATH.exists() and not PATIENTS_JSON_PATH.exists():
        return

    conn = get_connection()
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if users_count == 0 and USERS_JSON_PATH.exists():
        users_data = _load_json(USERS_JSON_PATH)
        for username, data in users_data.items():
            username = _normalize_name(username)
            if not username:
                continue
            pin_hash = data.get("pin_hash") or data.get("pin")
            if pin_hash and not str(pin_hash).startswith("pbkdf2"):
                if isinstance(pin_hash, str) and len(pin_hash) == 64:
                    migrated_hash = _hash_password(str(data.get("pin", "0000")))
                else:
                    migrated_hash = _hash_password(str(pin_hash))
            else:
                migrated_hash = _hash_password(str(data.get("pin", "0000"))) if data.get("pin") else pin_hash or _hash_password("0000")
            conn.execute(
                """
                INSERT OR REPLACE INTO users (username, role, pin_hash, active, failed_attempts, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    data.get("role", "Patient"),
                    migrated_hash,
                    bool(data.get("active", True)),
                    int(data.get("failed_attempts", 0)),
                    data.get("created") or now_iso(),
                ),
            )
    conn.commit()

    patient_count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    if patient_count == 0 and PATIENTS_JSON_PATH.exists():
        patients_data = _load_json(PATIENTS_JSON_PATH)
        for patient_name, data in patients_data.items():
            patient_name = _normalize_name(patient_name)
            if not patient_name:
                continue
            conn.execute(
                """
                INSERT OR REPLACE INTO patients (name, dob, blood_type, conditions, doctor, registered_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_name,
                    data.get("dob", ""),
                    data.get("blood_type", ""),
                    data.get("conditions", ""),
                    data.get("doctor", ""),
                    data.get("registered") or now_iso(),
                ),
            )
    conn.commit()
    conn.close()


def init_db():
    ensure_directories()
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            failed_attempts INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            dob TEXT,
            blood_type TEXT,
            conditions TEXT,
            doctor TEXT,
            registered_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            appointment_date TEXT,
            appointment_time TEXT,
            department TEXT,
            doctor TEXT,
            status TEXT DEFAULT 'Scheduled'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            note_text TEXT,
            author TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT,
            status TEXT,
            method TEXT,
            timestamp TEXT NOT NULL,
            confidence REAL,
            ip_address TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT,
            message TEXT,
            username TEXT,
            timestamp TEXT NOT NULL,
            read INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()
    _migrate_legacy_json_data()


def get_user_by_name(username):
    username = _normalize_name(username)
    if not username:
        return None
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def create_user(username, role, pin):
    username = _normalize_name(username)
    role = (role or "Patient").strip()
    if not username:
        raise ValueError("Username is required.")
    conn = get_connection()
    existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        raise ValueError(f"User '{username}' already exists.")
    conn.execute(
        "INSERT INTO users (username, role, pin_hash, active, failed_attempts, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, role, _hash_password(pin), 1, 0, now_iso()),
    )
    conn.commit()
    conn.close()
    return get_user_by_name(username)


def set_user_pin(username, new_pin):
    username = _normalize_name(username)
    if not username:
        raise ValueError("Username is required.")
    conn = get_connection()
    conn.execute("UPDATE users SET pin_hash = ? WHERE username = ?", (_hash_password(str(new_pin)), username))
    conn.commit()
    conn.close()
    return get_user_by_name(username)


def delete_user(username):
    username = _normalize_name(username)
    if not username:
        raise ValueError("Username is required.")
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True


def verify_pin(username, pin):
    user = get_user_by_name(username)
    if not user:
        return False
    stored_hash = user.get("pin_hash") or ""
    if not stored_hash:
        return False
    if str(stored_hash).startswith("pbkdf2"):
        from werkzeug.security import check_password_hash

        return check_password_hash(stored_hash, str(pin))
    if len(str(stored_hash)) == 64:
        import hashlib

        if hashlib.sha256(str(pin).encode("utf-8")).hexdigest() == str(stored_hash):
            update_user_password_hash(username, _hash_password(str(pin)))
            return True
    return False


def update_user_password_hash(username, new_hash):
    conn = get_connection()
    conn.execute("UPDATE users SET pin_hash = ? WHERE username = ?", (new_hash, username))
    conn.commit()
    conn.close()


def set_user_active(username, active):
    conn = get_connection()
    conn.execute("UPDATE users SET active = ? WHERE username = ?", (1 if active else 0, username))
    conn.commit()
    conn.close()


def increment_failed_attempts(username):
    user = get_user_by_name(username)
    if not user:
        return 0
    attempts = int(user.get("failed_attempts", 0)) + 1
    conn = get_connection()
    conn.execute("UPDATE users SET failed_attempts = ? WHERE username = ?", (attempts, username))
    conn.commit()
    conn.close()
    return attempts


def reset_failed_attempts(username):
    conn = get_connection()
    conn.execute("UPDATE users SET failed_attempts = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY username").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_patients():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_patient(name, dob="", blood_type="", conditions="", doctor=""):
    name = _normalize_name(name)
    if not name:
        raise ValueError("Patient name is required.")
    conn = get_connection()
    existing = conn.execute("SELECT 1 FROM patients WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.close()
        return get_patient_by_name(name)
    conn.execute(
        "INSERT INTO patients (name, dob, blood_type, conditions, doctor, registered_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, dob, blood_type, conditions, doctor, now_iso()),
    )
    conn.commit()
    conn.close()
    return get_patient_by_name(name)


def get_patient_by_name(name):
    name = _normalize_name(name)
    if not name:
        return None
    conn = get_connection()
    row = conn.execute("SELECT * FROM patients WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_appointment(patient_name, appointment_date, appointment_time, department, doctor, status="Scheduled"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO appointments (patient_name, appointment_date, appointment_time, department, doctor, status) VALUES (?, ?, ?, ?, ?, ?)",
        (patient_name, appointment_date, appointment_time, department, doctor, status),
    )
    conn.commit()
    conn.close()


def list_appointments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM appointments ORDER BY appointment_date, appointment_time").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_note(patient_name, note_text, author):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notes (patient_name, note_text, author, created_at) VALUES (?, ?, ?, ?)",
        (patient_name, note_text, author, now_iso()),
    )
    conn.commit()
    conn.close()


def list_notes(patient_name):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notes WHERE patient_name = ? ORDER BY created_at DESC", (patient_name,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def log_access(username, role, status, method="face", confidence=None, ip_address=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO access_logs (username, role, status, method, timestamp, confidence, ip_address) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, role, status, method, now_iso(), confidence, ip_address),
    )
    conn.commit()
    conn.close()


def list_logs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM access_logs ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_alert(alert_type, message, username="Unknown"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO alerts (alert_type, message, username, timestamp, read) VALUES (?, ?, ?, ?, 0)",
        (alert_type, message, username, now_iso()),
    )
    conn.commit()
    conn.close()


def list_alerts():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def unread_alert_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM alerts WHERE read = 0").fetchone()[0]
    conn.close()
    return count


def mark_alerts_read():
    conn = get_connection()
    conn.execute("UPDATE alerts SET read = 1 WHERE read = 0")
    conn.commit()
    conn.close()
