import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file, session, redirect

from services.auth import authenticate_user, require_login, require_roles
from services.database import (
    add_alert,
    add_appointment,
    create_patient,
    create_user,
    delete_user,
    get_user_by_name,
    init_db,
    list_alerts,
    list_appointments,
    list_logs,
    list_patients,
    list_users,
    log_access,
    set_user_active,
    set_user_pin,
    unread_alert_count,
)
from services.face_recognition import save_face_sample, verify_user_face
from services.face_training import train_face_model

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = {".png", ".jpg", ".jpeg"}
app.config["UPLOAD_PATH"] = str(DATA_DIR / "faces")

init_db()


def get_session_user():
    user = session.get("user")
    if not user:
        return None
    db_user = get_user_by_name(user)
    if not db_user:
        session.clear()
        return None
    return db_user


@app.get("/")
def index():
    return redirect("/login")


@app.get("/login")
def login_page():
    return render_template("login.html")


@app.get("/register")
def register_page():
    return render_template("register.html")


@app.get("/face-verification")
def face_verification_page():
    user = get_session_user()
    if not user:
        return redirect("/login")
    return render_template("face_verify.html", username=user["username"])


@app.get("/dashboard")
@require_login
def dashboard_page():
    user = get_session_user()
    if not user:
        return redirect("/login")
    role = user.get("role")
    if role == "Admin":
        return redirect("/admin")
    if role == "Doctor":
        return redirect("/doctor")
    if role == "Nurse":
        return redirect("/doctor")
    return redirect("/patient")


@app.get("/admin")
@require_login
@require_roles("Admin")
def admin_page():
    return render_template("admin.html", users=list_users(), patients=list_patients(), logs=list_logs(), alerts=list_alerts())


@app.get("/doctor")
@require_login
@require_roles("Doctor", "Nurse")
def doctor_page():
    return render_template("doctor.html", patients=list_patients(), appointments=list_appointments())


@app.get("/patient")
@require_login
@require_roles("Patient")
def patient_page():
    user = get_session_user()
    patient = get_user_by_name(user["username"]) if user else None
    return render_template("patient.html", patient=patient, appointments=list_appointments(), user=user)


@app.post("/api/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    pin = str(payload.get("pin", "")).strip()

    result = authenticate_user(username, pin)
    if not result["success"]:
        return jsonify({"success": False, "message": result["message"]}), 401

    user = result["user"]
    if not user.get("active", True):
        return jsonify({"success": False, "message": "Account is inactive."}), 403

    session["user"] = user["username"]
    session["role"] = user["role"]
    session["authenticated"] = True
    log_access(username, user.get("role", "Unknown"), "granted", method="pin")
    return jsonify({"success": True, "message": "PIN verified. Proceed to face verification.", "user": user})


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out."})


@app.post("/api/register")
def api_register():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    role = str(payload.get("role", "Patient")).strip() or "Patient"
    pin = str(payload.get("pin", "")).strip()

    if not username or not pin:
        return jsonify({"success": False, "message": "Username and PIN are required."}), 400
    if not pin.isdigit() or not (4 <= len(pin) <= 6):
        return jsonify({"success": False, "message": "PIN must be 4-6 digits."}), 400

    try:
        user = create_user(username, role, pin)
        if role == "Patient":
            create_patient(username, "", "", "", "")
        session["user"] = user["username"]
        session["role"] = user["role"]
        session["authenticated"] = True
        return jsonify({"success": True, "message": "User registered successfully.", "user": user})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/register-face")
def api_register_face():
    user = get_session_user()
    if not user:
        return jsonify({"success": False, "message": "Not authenticated."}), 401

    if "image" not in request.files:
        return jsonify({"success": False, "message": "No face image uploaded."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"success": False, "message": "No file selected."}), 400

    try:
        sample_path = save_face_sample(user["username"], image_file.read(), counter=None)
        try:
            train_face_model(user["username"])
        except Exception as exc:
            return jsonify({"success": False, "message": f"Face saved but model training failed: {exc}"}), 400
        return jsonify({"success": True, "message": "Face sample captured and model trained.", "path": sample_path})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/face/verify")
def api_face_verify():
    user = get_session_user()
    if not user:
        return jsonify({"success": False, "matched": False, "message": "Authentication required."}), 401

    if "image" not in request.files:
        return jsonify({"success": False, "matched": False, "message": "No image uploaded."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"success": False, "matched": False, "message": "No image selected."}), 400

    try:
        result = verify_user_face(user["username"], image_file.read(), threshold=80)
        result["username"] = user["username"]
        result["matched"] = bool(result.get("verified"))
        if result.get("success") and result.get("verified"):
            log_access(user["username"], user.get("role", "Unknown"), "granted", method="face", confidence=result.get("confidence"))
            return jsonify(result)
        add_alert("failed_face_verification", f"Face verification failed for {user['username']}.", user["username"])
        log_access(user["username"], user.get("role", "Unknown"), "denied", method="face", confidence=result.get("confidence"))
        return jsonify(result)
    except Exception as exc:
        return jsonify({"success": False, "matched": False, "username": user["username"], "message": "Face verification failed."}), 500


@app.get("/api/user")
def api_user():
    user = get_session_user()
    if not user:
        return jsonify({"success": False, "message": "Not logged in."}), 401
    return jsonify({"success": True, "user": user})


@app.get("/api/patients")
@require_login
def api_patients():
    return jsonify({"success": True, "patients": list_patients()})


@app.get("/api/appointments")
@require_login
def api_appointments():
    return jsonify({"success": True, "appointments": list_appointments()})


@app.get("/api/logs")
@require_login
@require_roles("Admin", "Doctor", "Nurse")
def api_logs():
    return jsonify({"success": True, "logs": list_logs()})


@app.get("/api/alerts")
@require_login
@require_roles("Admin")
def api_alerts():
    return jsonify({"success": True, "alerts": list_alerts(), "unread": unread_alert_count()})


@app.post("/api/admin/users/<username>/toggle")
@require_login
@require_roles("Admin")
def api_toggle_user(username):
    user = get_user_by_name(username)
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
    set_user_active(username, not bool(user.get("active", True)))
    return jsonify({"success": True, "active": bool(not user.get("active", True)), "username": username})


@app.post("/api/admin/users/<username>/reset-pin")
@require_login
@require_roles("Admin")
def api_reset_pin(username):
    payload = request.get_json(silent=True) or {}
    new_pin = str(payload.get("pin", "")).strip()
    if not new_pin.isdigit() or not (4 <= len(new_pin) <= 6):
        return jsonify({"success": False, "message": "PIN must be 4-6 digits."}), 400
    set_user_pin(username, new_pin)
    return jsonify({"success": True, "message": "PIN reset."})


@app.post("/api/admin/users/<username>/delete")
@require_login
@require_roles("Admin")
def api_delete_user(username):
    delete_user(username)
    return jsonify({"success": True, "message": "User deleted."})


@app.post("/api/patients")
@require_login
@require_roles("Admin", "Doctor", "Nurse")
def api_create_patient():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name:
        return jsonify({"success": False, "message": "Patient name is required."}), 400
    patient = create_patient(name, payload.get("dob", ""), payload.get("blood_type", ""), payload.get("conditions", ""), payload.get("doctor", ""))
    return jsonify({"success": True, "patient": patient})


@app.post("/api/appointments")
@require_login
@require_roles("Admin", "Doctor", "Nurse")
def api_create_appointment():
    payload = request.get_json(silent=True) or {}
    patient_name = str(payload.get("patient_name", "")).strip()
    date_val = str(payload.get("date", "")).strip()
    time_val = str(payload.get("time", "")).strip()
    department = str(payload.get("department", "")).strip()
    doctor = str(payload.get("doctor", "")).strip()
    if not patient_name or not date_val:
        return jsonify({"success": False, "message": "Patient name and appointment date are required."}), 400
    add_appointment(patient_name, date_val, time_val, department, doctor)
    return jsonify({"success": True, "message": "Appointment created."})


@app.get("/api/reports/patients/excel")
@require_login
@require_roles("Admin", "Doctor")
def report_patients_excel():
    import openpyxl
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Patients"
    ws.append(["Name", "DOB", "Blood Type", "Conditions", "Doctor", "Registered"])
    for patient in list_patients():
        ws.append([patient.get("name", ""), patient.get("dob", ""), patient.get("blood_type", ""), patient.get("conditions", ""), patient.get("doctor", ""), patient.get("registered_at", "")])
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(stream, as_attachment=True, download_name="patients.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/api/reports/patients/pdf")
@require_login
@require_roles("Admin", "Doctor")
def report_patients_pdf():
    from io import BytesIO

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=letter)
    pdf.setTitle("Patients Report")
    pdf.drawString(60, 760, "KLIKE Healthcare - Patient Report")
    y = 720
    for patient in list_patients():
        line = f"{patient.get('name', '')} | {patient.get('doctor', '')} | {patient.get('blood_type', '')}"
        pdf.drawString(60, y, line)
        y -= 18
        if y < 60:
            pdf.showPage()
            y = 760
    pdf.save()
    stream.seek(0)
    return send_file(stream, as_attachment=True, download_name="patients.pdf", mimetype="application/pdf")


@app.get("/api/reports/logs/excel")
@require_login
@require_roles("Admin")
def report_logs_excel():
    import openpyxl
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Access Logs"
    ws.append(["Username", "Role", "Status", "Method", "Timestamp", "Confidence", "IP Address"])
    for log in list_logs():
        ws.append([log.get("username", ""), log.get("role", ""), log.get("status", ""), log.get("method", ""), log.get("timestamp", ""), log.get("confidence", ""), log.get("ip_address", "")])
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(stream, as_attachment=True, download_name="access_logs.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/api/reports/logs/pdf")
@require_login
@require_roles("Admin")
def report_logs_pdf():
    from io import BytesIO

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=letter)
    pdf.drawString(60, 760, "KLIKE Healthcare - Access Log Report")
    y = 720
    for log in list_logs():
        line = f"{log.get('username', '')} | {log.get('status', '')} | {log.get('method', '')} | {log.get('timestamp', '')}"
        pdf.drawString(60, y, line)
        y -= 18
        if y < 60:
            pdf.showPage()
            y = 760
    pdf.save()
    stream.seek(0)
    return send_file(stream, as_attachment=True, download_name="access_logs.pdf", mimetype="application/pdf")


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok", "app": "KLIKE Healthcare Flask"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
