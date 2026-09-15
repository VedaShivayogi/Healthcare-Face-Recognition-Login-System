from io import BytesIO

import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from services.database import list_logs, list_patients


def build_patients_excel():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Patients"
    sheet.append(["Name", "DOB", "Blood Type", "Conditions", "Doctor", "Registered"])
    for patient in list_patients():
        sheet.append([
            patient.get("name", ""),
            patient.get("dob", ""),
            patient.get("blood_type", ""),
            patient.get("conditions", ""),
            patient.get("doctor", ""),
            patient.get("registered_at", ""),
        ])
    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return stream


def build_patients_pdf():
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
    return stream


def build_logs_excel():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Access Logs"
    sheet.append(["Username", "Role", "Status", "Method", "Timestamp", "Confidence", "IP Address"])
    for log in list_logs():
        sheet.append([
            log.get("username", ""),
            log.get("role", ""),
            log.get("status", ""),
            log.get("method", ""),
            log.get("timestamp", ""),
            log.get("confidence", ""),
            log.get("ip_address", ""),
        ])
    stream = BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return stream


def build_logs_pdf():
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
    return stream
