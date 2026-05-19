"""
KLIKE v4 – Healthcare Face Recognition Login System
Full-featured: MFA, Roles, Dashboard, Admin, Logs, Alerts, Analytics, Export.

Run: python run.py
"""

import sys, os, json, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "modules"))
sys.path.insert(0, ROOT)

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import math, threading
from datetime import datetime

from modules.db      import *
from modules.theme   import T, role_color
from modules.widgets import (PulsingCanvas, make_header, make_status, styled_btn,
                              ghost_btn, danger_btn, success_btn, sep,
                              make_input, make_card, role_badge, ScrollFrame, make_table)

ASSETS_DIR  = os.path.join(ROOT, "assets")
DATA_DIR    = os.path.join(ROOT, "data")


# ═══════════════════════════════════════════════════════════════════════════════
#  BASE PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        c = T()
        tk.Frame.__init__(self, parent, bg=c["BG_DARK"])
        self.controller = controller

    def go(self, page):
        self.controller.show_frame(page)

    def current_user(self):
        return self.controller.active_name

    def current_role(self):
        return self.controller.active_role


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGIN / SPLASH
# ═══════════════════════════════════════════════════════════════════════════════

class StartPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = T()
        make_header(self, controller=controller)

        body = tk.Frame(self, bg=c["BG_DARK"])
        body.pack(expand=True, fill="both", padx=36, pady=16)
        card = tk.Frame(body, bg=c["BG_CARD"], highlightthickness=1,
                        highlightbackground=c["BORDER"])
        card.pack(expand=True, fill="both")
        inner = tk.Frame(card, bg=c["BG_CARD"])
        inner.pack(expand=True)

        tk.Label(inner, text="Patient & Staff Portal",
                 font=("Segoe UI", 16, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(pady=(26,4))
        tk.Label(inner, text="Secure biometric access with multi-factor authentication",
                 font=("Segoe UI", 9), bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack()
        sep(inner)

        pills = tk.Frame(inner, bg=c["BG_CARD"]); pills.pack(pady=(4,16))
        for icon, txt in [("🔒","MFA Secured"),("👤","Role-Based"),("🏥","HIPAA Ready"),("📊","Analytics")]:
            p = tk.Frame(pills, bg=c["BG_INPUT"], highlightthickness=1,
                         highlightbackground=c["BORDER"])
            p.pack(side="left", padx=5, ipadx=8, ipady=4)
            tk.Label(p, text=f"{icon} {txt}", font=("Segoe UI", 8),
                     bg=c["BG_INPUT"], fg=c["TEXT_DIM"]).pack()
        sep(inner)

        btn_row = tk.Frame(inner, bg=c["BG_CARD"]); btn_row.pack(pady=16)
        styled_btn(btn_row, "  ＋  Register New User",
                   lambda: controller.show_frame("RegisterPage"),
                   pad_x=24, pad_y=11).grid(row=0, column=0, padx=8)
        styled_btn(btn_row, "  🔓  Login / Authenticate",
                   lambda: controller.show_frame("LoginPage"),
                   bg=c["BG_CARD"], fg=c["TEAL"],
                   pad_x=20, pad_y=10).grid(row=0, column=1, padx=8)

        ghost_btn(inner, "⚙  Admin Login",
                  lambda: controller.show_frame("AdminLoginPage")).pack(pady=(0,4))
        ghost_btn(inner, "✕  Exit System", self._exit).pack(pady=(0,16))
        make_status(self, alert_count=unread_alert_count())

    def _exit(self):
        if messagebox.askokcancel("Exit KLIKE", "Securely exit the system?"):
            self.controller.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  REGISTER
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = T()
        make_header(self, "New User Registration",
                    back_cmd=lambda: self.go("StartPage"), controller=controller)
        inner = make_card(self)

        # Step indicator
        self._steps(inner, 0)
        tk.Label(inner, text="Create Healthcare Profile",
                 font=("Segoe UI", 13, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(pady=(14,4))
        sep(inner)

        form = tk.Frame(inner, bg=c["BG_CARD"]); form.pack(pady=10)

        tk.Label(form, text="Full Name", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.nf, self.name_e = make_input(form, "e.g. Dr. Jane Smith")
        self.nf.pack(fill="x", ipady=2, pady=(2,8), ipadx=130)

        tk.Label(form, text="Role", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.role_var = tk.StringVar(value="Patient")
        role_row = tk.Frame(form, bg=c["BG_CARD"]); role_row.pack(anchor="w", pady=(2,8))
        for role in ["Admin","Doctor","Nurse","Patient"]:
            col = role_color(role)
            rb = tk.Radiobutton(role_row, text=role, variable=self.role_var, value=role,
                                bg=c["BG_CARD"], fg=col, selectcolor=c["BG_INPUT"],
                                activebackground=c["BG_CARD"], font=("Segoe UI", 9, "bold"),
                                cursor="hand2")
            rb.pack(side="left", padx=6)

        tk.Label(form, text="Security PIN (4–6 digits)", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.pf, self.pin_e = make_input(form, "Enter PIN", show="●")
        self.pf.pack(fill="x", ipady=2, pady=(2,8), ipadx=130)

        tk.Label(form, text="Confirm PIN", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.cpf, self.cpin_e = make_input(form, "Re-enter PIN", show="●")
        self.cpf.pack(fill="x", ipady=2, pady=(2,0), ipadx=130)

        sep(inner)
        btn_row = tk.Frame(inner, bg=c["BG_CARD"]); btn_row.pack(pady=12)
        ghost_btn(btn_row, "← Back", lambda: self.go("StartPage")).pack(side="left", padx=6)
        styled_btn(btn_row, "Next: Capture Face  →", self._next,
                   pad_x=22, pad_y=10).pack(side="left", padx=6)
        make_status(self)

    def _steps(self, parent, active):
        c = T()
        labels = ["Profile","Capture","Train","Done"]
        row = tk.Frame(parent, bg=c["BG_CARD"]); row.pack(pady=(18,4))
        for i, lbl in enumerate(labels):
            bg = c["TEAL"] if i == active else c["BG_INPUT"]
            fg = c["BG_DARK"] if i == active else c["TEXT_DIM"]
            sf = tk.Frame(row, bg=c["BG_CARD"]); sf.pack(side="left", padx=5)
            ci = tk.Frame(sf, bg=bg, width=24, height=24); ci.pack_propagate(False); ci.pack()
            tk.Label(ci, text=str(i+1), font=("Segoe UI", 9, "bold"),
                     bg=bg, fg=fg).place(relx=.5, rely=.5, anchor="center")
            tk.Label(sf, text=lbl, font=("Segoe UI", 7),
                     bg=c["BG_CARD"], fg=c["TEAL"] if i==active else c["BORDER"]).pack()
            if i < len(labels)-1:
                tk.Label(row, text="──", font=("Segoe UI", 7),
                         bg=c["BG_CARD"], fg=c["BORDER"]).pack(side="left")

    def _next(self):
        name = self.name_e.get().strip()
        role = self.role_var.get()
        pin  = self.pin_e.get().strip()
        cpin = self.cpin_e.get().strip()

        if not name or name == "e.g. Dr. Jane Smith":
            messagebox.showerror("KLIKE", "Please enter a full name."); return
        if name in load_users():
            messagebox.showerror("KLIKE", f'User "{name}" already exists.'); return
        if not pin.isdigit() or not (4 <= len(pin) <= 6):
            messagebox.showerror("KLIKE", "PIN must be 4–6 digits."); return
        if pin != cpin:
            messagebox.showerror("KLIKE", "PINs do not match."); return

        add_user(name, role, pin)
        # Add basic patient record if Patient role
        if role == "Patient":
            patients = load_patients()
            if name not in patients:
                add_patient(name, "—", "—", "—", "—")

        self.controller.active_name = name
        self.controller.active_role = role
        self.controller.show_frame("CapturePage")


# ═══════════════════════════════════════════════════════════════════════════════
#  CAPTURE PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class CapturePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = T()
        make_header(self, "Biometric Data Capture", controller=controller)
        inner = make_card(self)

        tk.Label(inner, text="📷  Facial Data Enrollment",
                 font=("Segoe UI", 14, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(pady=(22,4))
        sep(inner)

        prog = tk.Frame(inner, bg=c["BG_INPUT"], highlightthickness=1,
                        highlightbackground=c["BORDER"])
        prog.pack(padx=40, fill="x", pady=8)
        self.status_lbl = tk.Label(prog, text="  ⏳  Images captured:  0 / 300",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=c["BG_INPUT"], fg=c["TEAL"], pady=10)
        self.status_lbl.pack()

        inst = tk.Frame(inner, bg=c["BG_DARK"], highlightthickness=1,
                        highlightbackground=c["BORDER"])
        inst.pack(padx=40, fill="x", pady=6)
        for line in ["👤  Look directly at the camera",
                     "💡  Good lighting improves accuracy",
                     "🔄  Slowly turn head left and right",
                     "✅  System auto-stops at 300 images"]:
            tk.Label(inst, text=line, font=("Segoe UI", 8),
                     bg=c["BG_DARK"], fg=c["TEXT_DIM"],
                     anchor="w", padx=12, pady=3).pack(fill="x")
        sep(inner)

        btn_row = tk.Frame(inner, bg=c["BG_CARD"]); btn_row.pack(pady=12)
        styled_btn(btn_row, "📸  Capture Face Data", self._capture,
                   pad_x=20, pad_y=9).pack(side="left", padx=8)
        success_btn(btn_row, "🧠  Train AI Model", self._train).pack(side="left", padx=8)
        make_status(self, "Enrollment Mode  •  Camera Ready")

    def _capture(self):
        from modules.create_dataset import start_capture
        name = self.controller.active_name
        self.status_lbl.config(text="  🔴  Capturing … please wait", fg=T()["RED"])
        self.update()
        x = start_capture(name)
        self.controller.num_images = x
        c = T()
        self.status_lbl.config(
            text=f"  ✅  Images captured:  {x} / 300",
            fg=c["GREEN"] if x >= 300 else c["TEAL"])

    def _train(self):
        from modules.create_classifier import train_classifer
        if self.controller.num_images < 100:
            messagebox.showerror("KLIKE", "Capture at least 100 face images first."); return
        self.status_lbl.config(text="  🧠  Training model … please wait", fg=T()["TEAL"])
        self.update()
        train_classifer(self.controller.active_name)
        messagebox.showinfo("KLIKE – Success",
                            "✅  Biometric model trained!\nProfile is now active.")
        self.controller.show_frame("StartPage")


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGIN – FACE + PIN (MFA)
# ═══════════════════════════════════════════════════════════════════════════════

class LoginPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = T()
        make_header(self, "Biometric Authentication",
                    back_cmd=lambda: self.go("StartPage"), controller=controller)
        inner = make_card(self)

        tk.Label(inner, text="🔍  Multi-Factor Identity Verification",
                 font=("Segoe UI", 14, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(pady=(22,4))
        tk.Label(inner, text="Step 1: Enter name & PIN  •  Step 2: Face scan",
                 font=("Segoe UI", 8), bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack()
        sep(inner)

        form = tk.Frame(inner, bg=c["BG_CARD"]); form.pack(pady=8)

        tk.Label(form, text="Registered Name", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.nf, self.name_e = make_input(form, "Your registered name")
        self.nf.pack(fill="x", ipady=2, pady=(2,8), ipadx=120)

        tk.Label(form, text="Security PIN", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.pf, self.pin_e = make_input(form, "Enter your PIN", show="●")
        self.pf.pack(fill="x", ipady=2, pady=(2,0), ipadx=120)

        # Numpad
        sep(inner)
        np_frame = tk.Frame(inner, bg=c["BG_CARD"]); np_frame.pack(pady=6)
        for i, row_digits in enumerate([["1","2","3"],["4","5","6"],["7","8","9"],["⌫","0","✓"]]):
            for j, d in enumerate(row_digits):
                cmd = (lambda x=d: self._numpad(x))
                bg = c["TEAL"] if d == "✓" else (c["RED"] if d == "⌫" else c["BG_INPUT"])
                fg = c["BG_DARK"] if d in ("✓",) else c["WHITE"]
                btn = tk.Button(np_frame, text=d, width=4, height=2,
                                bg=bg, fg=fg, font=("Segoe UI", 11, "bold"),
                                relief="flat", bd=0, cursor="hand2",
                                command=cmd)
                btn.grid(row=i, column=j, padx=3, pady=3)

        sep(inner)
        btn_row = tk.Frame(inner, bg=c["BG_CARD"]); btn_row.pack(pady=10)
        styled_btn(btn_row, "📸  Verify PIN then Face Scan", self._login,
                   pad_x=22, pad_y=10).pack(side="left", padx=8)
        make_status(self, "MFA Authentication  •  Secure Session")

    def _numpad(self, d):
        if d == "⌫":
            v = self.pin_e.get()
            self.pin_e.delete(0, "end")
            self.pin_e.insert(0, v[:-1])
        elif d == "✓":
            self._login()
        else:
            self.pin_e.insert("end", d)

    def _login(self):
        name = self.name_e.get().strip()
        pin  = self.pin_e.get().strip()

        if not name or name == "Your registered name":
            messagebox.showerror("KLIKE", "Please enter your registered name."); return

        user = get_user(name)
        if not user:
            add_alert("failed_login", f"Unknown user attempted login: {name}", name)
            messagebox.showerror("KLIKE – Access Denied",
                                 f'No profile found for "{name}".\nPlease register first.'); return

        if not user.get("active", True):
            messagebox.showerror("KLIKE – Account Locked",
                                 "This account has been deactivated.\nContact your administrator."); return

        failed = user.get("failed_attempts", 0)
        if failed >= 5:
            add_alert("locked", f"Account locked after 5 failed attempts: {name}", name)
            messagebox.showerror("KLIKE – Locked",
                                 "Account locked (5 failed attempts).\nContact administrator."); return

        if not verify_pin(name, pin):
            increment_failed(name)
            remaining = 4 - failed
            add_alert("failed_login", f"Wrong PIN for {name} (attempt {failed+1})", name)
            messagebox.showerror("KLIKE – Wrong PIN",
                                 f"Incorrect PIN.\n{remaining} attempts remaining before lockout.")
            return

        # PIN OK → face scan
        messagebox.showinfo("KLIKE – PIN Verified ✅",
                            "PIN accepted!\nLaunching face recognition now…")
        self._run_face(name, user.get("role","Patient"))

    def _run_face(self, name, role):
        from modules.detector import main_app
        main_app(name)
        # After webcam closes, ask result
        granted = messagebox.askyesno("KLIKE – Face Scan Result",
                                      "Was your face successfully recognised?\n\n"
                                      "(Tap Yes if the camera showed VERIFIED)")
        if granted:
            reset_failed(name)
            log_access(name, role, "granted", "face+pin")
            self.controller.active_name = name
            self.controller.active_role = role
            messagebox.showinfo("KLIKE – Welcome ✅", f"✅ Access Granted\n\nWelcome, {name}!")
            dest = "AdminDashboard" if role == "Admin" else "PatientDashboard"
            self.controller.show_frame(dest)
        else:
            increment_failed(name)
            log_access(name, role, "denied", "face")
            add_alert("intruder", f"Face not recognised for {name}", name)
            messagebox.showerror("KLIKE – Denied ❌",
                                 "❌ Face not recognised.\nPlease try again or contact support.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PATIENT DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class PatientDashboard(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        for w in self.winfo_children(): w.destroy()
        c = T()
        name = self.current_user() or "Patient"
        role = self.current_role() or "Patient"
        make_header(self, f"Patient Dashboard  •  {name}", controller=self.controller)

        # Tab bar
        tab_bar = tk.Frame(self, bg=c["BG_CARD"])
        tab_bar.pack(fill="x")
        self._tab_frame = tk.Frame(self, bg=c["BG_DARK"])
        self._tab_frame.pack(fill="both", expand=True)

        self._tabs = {}
        for label in ["Overview", "Appointments", "Records", "Notes"]:
            btn = tk.Button(tab_bar, text=label,
                            bg=c["BG_CARD"], fg=c["TEXT_DIM"],
                            font=("Segoe UI", 9), relief="flat",
                            bd=0, cursor="hand2", padx=16, pady=8,
                            command=lambda l=label: self._switch_tab(l))
            btn.pack(side="left")
            self._tabs[label] = btn

        self._active_tab = None
        self._switch_tab("Overview")
        make_status(self, f"Logged in as {role}  •  {name}",
                    alert_count=unread_alert_count())

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self._build()

    def _switch_tab(self, label):
        c = T()
        for lbl, btn in self._tabs.items():
            btn.config(bg=c["TEAL"] if lbl==label else c["BG_CARD"],
                       fg=c["BG_DARK"] if lbl==label else c["TEXT_DIM"],
                       font=("Segoe UI", 9, "bold") if lbl==label else ("Segoe UI", 9))
        for w in self._tab_frame.winfo_children(): w.destroy()
        self._active_tab = label
        {"Overview": self._tab_overview,
         "Appointments": self._tab_appointments,
         "Records": self._tab_records,
         "Notes": self._tab_notes}[label]()

    def _tab_overview(self):
        c  = T()
        name = self.current_user() or ""
        user = get_user(name) or {}
        info = get_patient(name) or {}
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        # Welcome card
        wcard = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                         highlightbackground=c["BORDER"])
        wcard.pack(fill="x", padx=24, pady=12)
        crow = tk.Frame(wcard, bg=c["BG_CARD"]); crow.pack(fill="x", padx=16, pady=10)
        rb = role_badge(crow, user.get("role","Patient")); rb.pack(side="left", padx=(0,12))
        tk.Label(crow, text=f"Welcome back, {name}",
                 font=("Segoe UI", 14, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(side="left")

        # Stat cards
        stats_row = tk.Frame(p, bg=c["BG_DARK"]); stats_row.pack(fill="x", padx=24, pady=4)
        appts = info.get("appointments", [])
        notes = info.get("notes", [])
        logs  = [l for l in load_logs() if l.get("name") == name]
        for icon, lbl, val, col in [
            ("📅", "Appointments", len(appts), c["TEAL"]),
            ("📋", "Clinical Notes", len(notes), c["PURPLE"]),
            ("🔐", "Login Sessions", len(logs), c["GREEN"]),
            ("⚠️", "Alerts", unread_alert_count(), c["RED"]),
        ]:
            card = tk.Frame(stats_row, bg=c["BG_CARD"], highlightthickness=1,
                            highlightbackground=c["BORDER"])
            card.pack(side="left", expand=True, fill="both", padx=6, ipadx=10, ipady=10)
            tk.Label(card, text=icon, font=("Segoe UI", 20), bg=c["BG_CARD"]).pack(pady=(10,2))
            tk.Label(card, text=str(val), font=("Segoe UI", 18, "bold"),
                     bg=c["BG_CARD"], fg=col).pack()
            tk.Label(card, text=lbl, font=("Segoe UI", 8),
                     bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(pady=(0,10))

        # Medical info
        if info:
            mcard = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                             highlightbackground=c["BORDER"])
            mcard.pack(fill="x", padx=24, pady=10)
            tk.Label(mcard, text="🏥  Medical Information",
                     font=("Segoe UI", 11, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(
                         anchor="w", padx=16, pady=(10,4))
            tk.Frame(mcard, bg=c["BORDER"], height=1).pack(fill="x")
            grid = tk.Frame(mcard, bg=c["BG_CARD"]); grid.pack(fill="x", padx=16, pady=10)
            for i, (lbl, key) in enumerate([("Date of Birth","dob"),("Blood Type","blood_type"),
                                             ("Conditions","conditions"),("Doctor","doctor")]):
                tk.Label(grid, text=lbl+":", font=("Segoe UI", 9, "bold"),
                         bg=c["BG_CARD"], fg=c["TEAL"]).grid(row=i, column=0, sticky="w", padx=6, pady=2)
                tk.Label(grid, text=info.get(key,"—"), font=("Segoe UI", 9),
                         bg=c["BG_CARD"], fg=c["TEXT"]).grid(row=i, column=1, sticky="w", padx=6)

        # Quick actions
        qa = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                      highlightbackground=c["BORDER"])
        qa.pack(fill="x", padx=24, pady=10)
        tk.Label(qa, text="Quick Actions", font=("Segoe UI", 11, "bold"),
                 bg=c["BG_CARD"], fg=c["WHITE"]).pack(anchor="w", padx=16, pady=(10,6))
        qrow = tk.Frame(qa, bg=c["BG_CARD"]); qrow.pack(anchor="w", padx=16, pady=(0,12))
        styled_btn(qrow, "📅 Add Appointment", lambda: self._switch_tab("Appointments"),
                   pad_x=14, pad_y=8).pack(side="left", padx=6)
        styled_btn(qrow, "📤 Export My Report", self._export_my_report,
                   bg=c["PURPLE"], fg=c["WHITE"], pad_x=14, pad_y=8).pack(side="left", padx=6)
        ghost_btn(qrow, "🚪 Logout", lambda: self.go("StartPage")).pack(side="left", padx=6)

    def _tab_appointments(self):
        c = T(); name = self.current_user() or ""
        info = get_patient(name) or {}
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        hdr = tk.Frame(p, bg=c["BG_DARK"]); hdr.pack(fill="x", padx=24, pady=(16,6))
        tk.Label(hdr, text="📅  Appointments", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(side="left")
        styled_btn(hdr, "＋ New Appointment", lambda: self._new_appointment(name),
                   pad_x=14, pad_y=7).pack(side="right")

        appts = info.get("appointments", [])
        if not appts:
            tk.Label(p, text="No appointments scheduled yet.",
                     font=("Segoe UI", 10), bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(pady=30)
        else:
            rows = [[a.get("date",""), a.get("time",""), a.get("dept",""),
                     a.get("doctor",""), a.get("status","")] for a in appts]
            tbl = make_table(p, ["Date","Time","Department","Doctor","Status"],
                             rows, [14,10,18,18,14])
            tbl.pack(fill="x", padx=24, pady=8)

    def _new_appointment(self, name):
        win = tk.Toplevel(self); win.title("New Appointment"); win.geometry("400x340")
        c = T(); win.configure(bg=c["BG_DARK"])
        tk.Label(win, text="Schedule Appointment", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(pady=16)
        fields = {}
        for lbl, ph in [("Date (YYYY-MM-DD)","2025-01-15"),("Time","09:00 AM"),
                         ("Department","Cardiology"),("Doctor","Dr. Smith")]:
            tk.Label(win, text=lbl, font=("Segoe UI", 9, "bold"),
                     bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(anchor="w", padx=24)
            fr, en = make_input(win, ph)
            fr.pack(fill="x", padx=24, ipady=2, pady=(2,8))
            fields[lbl] = en
        def _save():
            add_appointment(name,
                fields["Date (YYYY-MM-DD)"].get(),
                fields["Time"].get(),
                fields["Department"].get(),
                fields["Doctor"].get())
            messagebox.showinfo("KLIKE","Appointment saved!")
            win.destroy(); self._switch_tab("Appointments")
        styled_btn(win, "Save Appointment", _save, pad_x=20, pad_y=8).pack(pady=8)

    def _tab_records(self):
        c = T(); name = self.current_user() or ""
        info = get_patient(name) or {}
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner
        tk.Label(p, text="📋  Medical Records", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(anchor="w", padx=24, pady=(16,6))

        for lbl, key in [("Full Name", None), ("Date of Birth","dob"),
                          ("Blood Type","blood_type"),("Conditions","conditions"),("Doctor","doctor")]:
            val = name if key is None else info.get(key,"—")
            row = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                           highlightbackground=c["BORDER"])
            row.pack(fill="x", padx=24, pady=3)
            tk.Label(row, text=f"  {lbl}:", font=("Segoe UI", 9, "bold"),
                     bg=c["BG_CARD"], fg=c["TEAL"], width=18, anchor="w").pack(side="left", pady=8)
            tk.Label(row, text=val, font=("Segoe UI", 9),
                     bg=c["BG_CARD"], fg=c["TEXT"]).pack(side="left", pady=8)

        if name in load_patients():
            btn_row = tk.Frame(p, bg=c["BG_DARK"]); btn_row.pack(anchor="w", padx=24, pady=12)
            styled_btn(btn_row, "✏️ Edit Medical Info", lambda: self._edit_record(name),
                       pad_x=14, pad_y=8).pack(side="left", padx=6)
            styled_btn(btn_row, "📤 Export PDF Report", self._export_my_report,
                       bg=c["PURPLE"], fg=c["WHITE"], pad_x=14, pad_y=8).pack(side="left", padx=6)

    def _edit_record(self, name):
        info = get_patient(name) or {}
        win = tk.Toplevel(self); win.title("Edit Record"); win.geometry("400x360")
        c = T(); win.configure(bg=c["BG_DARK"])
        tk.Label(win, text="Edit Medical Information", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(pady=14)
        fields = {}
        for lbl, key in [("Date of Birth","dob"),("Blood Type","blood_type"),
                          ("Conditions","conditions"),("Primary Doctor","doctor")]:
            tk.Label(win, text=lbl, font=("Segoe UI", 9, "bold"),
                     bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(anchor="w", padx=24)
            fr, en = make_input(win, info.get(key,"—"))
            fr.pack(fill="x", padx=24, ipady=2, pady=(2,8))
            fields[key] = en
        def _save():
            patients = load_patients()
            if name in patients:
                for k, e in fields.items():
                    patients[name][k] = e.get()
                save_patients(patients)
            messagebox.showinfo("KLIKE","Record updated!"); win.destroy()
            self._switch_tab("Records")
        styled_btn(win, "Save Changes", _save, pad_x=20, pad_y=8).pack(pady=8)

    def _tab_notes(self):
        c = T(); name = self.current_user() or ""
        info = get_patient(name) or {}
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        hdr = tk.Frame(p, bg=c["BG_DARK"]); hdr.pack(fill="x", padx=24, pady=(16,6))
        tk.Label(hdr, text="📝  Clinical Notes", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(side="left")

        notes = info.get("notes",[])
        if not notes:
            tk.Label(p, text="No clinical notes yet.", font=("Segoe UI", 10),
                     bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(pady=30)
        else:
            for n in reversed(notes):
                nc = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                              highlightbackground=c["BORDER"])
                nc.pack(fill="x", padx=24, pady=4)
                tk.Label(nc, text=f"  {n.get('date','')}  —  {n.get('author','')}",
                         font=("Segoe UI", 8, "bold"), bg=c["BG_CARD"],
                         fg=c["TEAL"]).pack(anchor="w", padx=8, pady=(6,2))
                tk.Label(nc, text=f"  {n.get('text','')}",
                         font=("Segoe UI", 9), bg=c["BG_CARD"],
                         fg=c["TEXT"], wraplength=600, justify="left").pack(
                             anchor="w", padx=8, pady=(0,8))

    def _export_my_report(self):
        name = self.current_user() or ""
        info = get_patient(name)
        if not info:
            messagebox.showerror("KLIKE","No patient record found."); return
        from modules.exporter import export_patient_pdf
        path, err = export_patient_pdf(name, info)
        if err:
            messagebox.showerror("KLIKE – Export Error", err)
        else:
            messagebox.showinfo("KLIKE – Exported ✅", f"PDF saved to:\n{path}")
            try: os.startfile(path)
            except: pass


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

class AdminLoginPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = T()
        make_header(self, "Admin Authentication",
                    back_cmd=lambda: self.go("StartPage"), controller=controller)
        inner = make_card(self)

        tk.Label(inner, text="🔐  Admin Access Portal",
                 font=("Segoe UI", 14, "bold"), bg=c["BG_CARD"], fg=c["WHITE"]).pack(pady=(22,4))
        tk.Label(inner, text="Administrator credentials required",
                 font=("Segoe UI", 8), bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack()
        sep(inner)

        form = tk.Frame(inner, bg=c["BG_CARD"]); form.pack(pady=10)
        tk.Label(form, text="Admin Username", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.nf, self.name_e = make_input(form, "Admin username")
        self.nf.pack(fill="x", ipady=2, pady=(2,8), ipadx=120)

        tk.Label(form, text="Admin PIN", font=("Segoe UI", 9, "bold"),
                 bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
        self.pf, self.pin_e = make_input(form, "Admin PIN", show="●")
        self.pf.pack(fill="x", ipady=2, pady=(2,0), ipadx=120)

        sep(inner)
        tk.Label(inner, text="💡  Default admin: username = Admin, PIN = 0000",
                 font=("Segoe UI", 8), bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(pady=4)
        btn_row = tk.Frame(inner, bg=c["BG_CARD"]); btn_row.pack(pady=10)
        ghost_btn(btn_row, "← Back", lambda: self.go("StartPage")).pack(side="left", padx=6)
        danger_btn(btn_row, "🔐 Enter Admin Panel", self._admin_login).pack(side="left", padx=6)
        make_status(self, "Admin Authentication")

    def _admin_login(self):
        name = self.name_e.get().strip()
        pin  = self.pin_e.get().strip()
        users = load_users()

        # Auto-create default admin if none exists
        if "Admin" not in users:
            add_user("Admin", "Admin", "0000")

        if not verify_pin(name, pin):
            messagebox.showerror("KLIKE – Denied", "Invalid admin credentials."); return
        u = get_user(name)
        if not u or u.get("role") != "Admin":
            messagebox.showerror("KLIKE – Denied", "This account does not have Admin role."); return

        self.controller.active_name = name
        self.controller.active_role = "Admin"
        log_access(name, "Admin", "granted", "pin")
        self.controller.show_frame("AdminDashboard")


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class AdminDashboard(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self._build()

    def _build(self):
        for w in self.winfo_children(): w.destroy()
        c = T()
        make_header(self, "Admin Dashboard  •  Control Panel", controller=self.controller)

        tab_bar = tk.Frame(self, bg=c["BG_CARD"]); tab_bar.pack(fill="x")
        self._tab_frame = tk.Frame(self, bg=c["BG_DARK"])
        self._tab_frame.pack(fill="both", expand=True)

        self._tabs = {}
        for lbl in ["Overview","Users","Access Logs","Alerts","Analytics","Reports"]:
            btn = tk.Button(tab_bar, text=lbl, bg=c["BG_CARD"], fg=c["TEXT_DIM"],
                            font=("Segoe UI", 9), relief="flat", bd=0,
                            cursor="hand2", padx=12, pady=8,
                            command=lambda l=lbl: self._switch(l))
            btn.pack(side="left")
            self._tabs[lbl] = btn

        self._switch("Overview")
        make_status(self, f"Admin Session  •  {self.current_user()}",
                    alert_count=unread_alert_count())

    def _switch(self, lbl):
        c = T()
        for l, b in self._tabs.items():
            b.config(bg=c["TEAL"] if l==lbl else c["BG_CARD"],
                     fg=c["BG_DARK"] if l==lbl else c["TEXT_DIM"],
                     font=("Segoe UI", 9, "bold") if l==lbl else ("Segoe UI", 9))
        for w in self._tab_frame.winfo_children(): w.destroy()
        {"Overview": self._overview, "Users": self._users,
         "Access Logs": self._logs, "Alerts": self._alerts,
         "Analytics": self._analytics, "Reports": self._reports}[lbl]()

    # ── Overview ──────────────────────────────────────────────────────────────
    def _overview(self):
        c = T()
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        users    = load_users()
        logs     = load_logs()
        alerts   = load_alerts()
        patients = load_patients()
        today_logs = [l for l in logs if l.get("date") == today()]
        granted    = [l for l in logs if l.get("status") == "granted"]
        denied     = [l for l in logs if l.get("status") == "denied"]

        tk.Label(p, text="System Overview", font=("Segoe UI", 14, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(anchor="w", padx=24, pady=(16,8))

        stat_row = tk.Frame(p, bg=c["BG_DARK"]); stat_row.pack(fill="x", padx=24, pady=4)
        for icon, lbl, val, col in [
            ("👥","Total Users",    len(users),   c["TEAL"]),
            ("🏥","Patients",       len(patients),c["GREEN"]),
            ("✅","Logins Granted", len(granted), c["GREEN"]),
            ("❌","Logins Denied",  len(denied),  c["RED"]),
            ("📅","Today's Logins", len(today_logs), c["TEAL"]),
            ("🔔","Unread Alerts",  unread_alert_count(), c["ORANGE"]),
        ]:
            card = tk.Frame(stat_row, bg=c["BG_CARD"], highlightthickness=1,
                            highlightbackground=c["BORDER"])
            card.pack(side="left", expand=True, fill="both",
                      padx=5, ipadx=8, ipady=8)
            tk.Label(card, text=icon, font=("Segoe UI", 18),
                     bg=c["BG_CARD"]).pack(pady=(8,2))
            tk.Label(card, text=str(val), font=("Segoe UI", 16, "bold"),
                     bg=c["BG_CARD"], fg=col).pack()
            tk.Label(card, text=lbl, font=("Segoe UI", 7),
                     bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(pady=(0,8))

        # Recent logins
        tk.Label(p, text="Recent Access Log", font=("Segoe UI", 11, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(anchor="w", padx=24, pady=(16,4))
        recent = list(reversed(logs[-8:])) if logs else []
        if recent:
            rows = [[l.get("timestamp",""),l.get("name",""),
                     l.get("role",""),l.get("status",""),l.get("method","")] for l in recent]
            tbl = make_table(p, ["Timestamp","Name","Role","Status","Method"],
                             rows, [20,16,10,10,10])
            tbl.pack(fill="x", padx=24, pady=4)

        # Quick actions
        qa = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                      highlightbackground=c["BORDER"])
        qa.pack(fill="x", padx=24, pady=12)
        tk.Label(qa, text="Quick Actions", font=("Segoe UI", 11, "bold"),
                 bg=c["BG_CARD"], fg=c["WHITE"]).pack(anchor="w", padx=16, pady=(10,6))
        qrow = tk.Frame(qa, bg=c["BG_CARD"]); qrow.pack(anchor="w", padx=16, pady=(0,12))
        styled_btn(qrow, "👥 Manage Users", lambda: self._switch("Users"),
                   pad_x=12, pad_y=7).pack(side="left", padx=5)
        styled_btn(qrow, "📊 View Analytics", lambda: self._switch("Analytics"),
                   bg=c["PURPLE"], fg=c["WHITE"], pad_x=12, pad_y=7).pack(side="left", padx=5)
        styled_btn(qrow, "📤 Export Reports", lambda: self._switch("Reports"),
                   bg=c["GREEN"], fg=c["BG_DARK"], pad_x=12, pad_y=7).pack(side="left", padx=5)
        ghost_btn(qrow, "🚪 Logout", lambda: self.go("StartPage")).pack(side="left", padx=5)

    # ── Users ─────────────────────────────────────────────────────────────────
    def _users(self):
        c = T()
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        hdr = tk.Frame(p, bg=c["BG_DARK"]); hdr.pack(fill="x", padx=24, pady=(16,6))
        tk.Label(hdr, text="👥  User Management", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(side="left")
        styled_btn(hdr, "＋ Add User", lambda: self.go("RegisterPage"),
                   pad_x=12, pad_y=6).pack(side="right")

        # Search
        sf2 = tk.Frame(p, bg=c["BG_DARK"]); sf2.pack(fill="x", padx=24, pady=4)
        tk.Label(sf2, text="🔍 Search:", font=("Segoe UI", 9),
                 bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(side="left")
        sf_f, self.search_e = make_input(sf2, "Filter by name or role")
        sf_f.pack(side="left", ipadx=80, ipady=2, padx=8)
        styled_btn(sf2, "Search", lambda: self._refresh_users(p), pad_x=10, pad_y=5).pack(side="left")

        self._user_list_frame = tk.Frame(p, bg=c["BG_DARK"])
        self._user_list_frame.pack(fill="x", padx=24)
        self._refresh_users(p)

    def _refresh_users(self, p=None):
        c = T()
        for w in self._user_list_frame.winfo_children(): w.destroy()
        query = ""
        try: query = self.search_e.get().strip().lower()
        except: pass
        users = load_users()

        for name, info in users.items():
            if query and query not in name.lower() and query not in info.get("role","").lower():
                continue
            row = tk.Frame(self._user_list_frame, bg=c["BG_CARD"],
                           highlightthickness=1, highlightbackground=c["BORDER"])
            row.pack(fill="x", pady=3)

            rb = role_badge(row, info.get("role","Patient")); rb.pack(side="left", padx=12, pady=8)
            tk.Label(row, text=name, font=("Segoe UI", 10, "bold"),
                     bg=c["BG_CARD"], fg=c["WHITE"]).pack(side="left", padx=4)
            status_col = c["GREEN"] if info.get("active", True) else c["RED"]
            status_txt = "Active" if info.get("active", True) else "Disabled"
            tk.Label(row, text=f"  {status_txt}  ",
                     font=("Segoe UI", 8), bg=c["BG_CARD"], fg=status_col).pack(side="left")
            tk.Label(row, text=f"  Failed: {info.get('failed_attempts',0)}",
                     font=("Segoe UI", 8), bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(side="left")

            btn_row = tk.Frame(row, bg=c["BG_CARD"]); btn_row.pack(side="right", padx=12)
            cur_active = info.get("active", True)
            toggle_txt = "🔴 Disable" if cur_active else "🟢 Enable"
            tk.Button(btn_row, text=toggle_txt, font=("Segoe UI", 8),
                      bg=c["BG_INPUT"], fg=c["TEXT"], relief="flat",
                      cursor="hand2", padx=8, pady=4,
                      command=lambda n=name, a=cur_active: self._toggle_user(n, a)
                      ).pack(side="left", padx=4)
            tk.Button(btn_row, text="🔄 Reset PIN",
                      font=("Segoe UI", 8), bg=c["BG_INPUT"], fg=c["TEXT"],
                      relief="flat", cursor="hand2", padx=8, pady=4,
                      command=lambda n=name: self._reset_pin(n)).pack(side="left", padx=4)
            tk.Button(btn_row, text="🗑 Delete",
                      font=("Segoe UI", 8), bg=c["RED"], fg=c["WHITE"],
                      relief="flat", cursor="hand2", padx=8, pady=4,
                      command=lambda n=name: self._del_user(n)).pack(side="left", padx=4)

    def _toggle_user(self, name, cur_active):
        set_user_active(name, not cur_active)
        self._switch("Users")

    def _reset_pin(self, name):
        new_pin = simpledialog.askstring("Reset PIN", f"New PIN for {name} (4-6 digits):", show="*")
        if new_pin and new_pin.isdigit() and 4 <= len(new_pin) <= 6:
            users = load_users()
            import hashlib
            users[name]["pin_hash"] = hashlib.sha256(new_pin.encode()).hexdigest()
            users[name]["failed_attempts"] = 0
            save_users(users)
            messagebox.showinfo("KLIKE", f"PIN reset for {name}.")
        elif new_pin:
            messagebox.showerror("KLIKE","Invalid PIN.")

    def _del_user(self, name):
        if messagebox.askyesno("KLIKE","Delete this user permanently?"):
            delete_user(name)
            self._switch("Users")

    # ── Access Logs ───────────────────────────────────────────────────────────
    def _logs(self):
        c = T()
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        hdr = tk.Frame(p, bg=c["BG_DARK"]); hdr.pack(fill="x", padx=24, pady=(16,6))
        tk.Label(hdr, text="📋  Access Logs", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(side="left")

        # Filter row
        fr = tk.Frame(p, bg=c["BG_DARK"]); fr.pack(fill="x", padx=24, pady=4)
        tk.Label(fr, text="Filter:", font=("Segoe UI", 9),
                 bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(side="left")
        self.log_filter = tk.StringVar(value="All")
        for val in ["All","granted","denied"]:
            tk.Radiobutton(fr, text=val.capitalize(), variable=self.log_filter, value=val,
                           bg=c["BG_DARK"], fg=c["TEXT_DIM"], selectcolor=c["BG_INPUT"],
                           activebackground=c["BG_DARK"], cursor="hand2",
                           command=lambda: self._refresh_logs(p)).pack(side="left", padx=8)

        self._log_frame = tk.Frame(p, bg=c["BG_DARK"])
        self._log_frame.pack(fill="x", padx=24)
        self._refresh_logs(p)

    def _refresh_logs(self, p=None):
        for w in self._log_frame.winfo_children(): w.destroy()
        c = T()
        logs = load_logs()
        filt = self.log_filter.get()
        if filt != "All":
            logs = [l for l in logs if l.get("status") == filt]
        logs = list(reversed(logs))

        if not logs:
            tk.Label(self._log_frame, text="No logs found.",
                     font=("Segoe UI", 10), bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(pady=20)
            return

        rows = [[l.get("timestamp",""), l.get("name",""), l.get("role",""),
                 l.get("status",""), l.get("method","")] for l in logs]
        tbl = make_table(self._log_frame,
                         ["Timestamp","Name","Role","Status","Method"],
                         rows, [20,16,12,10,10])
        tbl.pack(fill="x")

    # ── Alerts ────────────────────────────────────────────────────────────────
    def _alerts(self):
        c = T()
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner

        hdr = tk.Frame(p, bg=c["BG_DARK"]); hdr.pack(fill="x", padx=24, pady=(16,6))
        tk.Label(hdr, text="🔔  Security Alerts", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(side="left")
        styled_btn(hdr, "✓ Mark All Read", lambda: (mark_alerts_read(), self._switch("Alerts")),
                   pad_x=12, pad_y=6).pack(side="right")

        alerts = list(reversed(load_alerts()))
        if not alerts:
            tk.Label(p, text="No alerts.", font=("Segoe UI", 10),
                     bg=c["BG_DARK"], fg=c["TEXT_DIM"]).pack(pady=30)
            return

        type_icons = {"failed_login": "🔑", "intruder": "👁", "locked": "🔒"}
        type_cols  = {"failed_login": c["ORANGE"], "intruder": c["RED"], "locked": c["PURPLE"]}
        for a in alerts:
            atype = a.get("type","")
            is_unread = not a.get("read", False)
            bg = c["BG_CARD"] if not is_unread else c["BG_INPUT"]
            card = tk.Frame(p, bg=bg, highlightthickness=1,
                            highlightbackground=type_cols.get(atype, c["BORDER"]))
            card.pack(fill="x", padx=24, pady=4)
            row = tk.Frame(card, bg=bg); row.pack(fill="x", padx=12, pady=8)
            icon = type_icons.get(atype, "⚠️")
            tk.Label(row, text=icon, font=("Segoe UI", 16), bg=bg).pack(side="left", padx=(0,8))
            col = tk.Frame(row, bg=bg); col.pack(side="left", fill="x", expand=True)
            tk.Label(col, text=a.get("detail",""),
                     font=("Segoe UI", 9, "bold" if is_unread else "normal"),
                     bg=bg, fg=c["WHITE"]).pack(anchor="w")
            tk.Label(col, text=f"{a.get('timestamp','')}  •  User: {a.get('name','')}",
                     font=("Segoe UI", 8), bg=bg, fg=c["TEXT_DIM"]).pack(anchor="w")
            if is_unread:
                tk.Label(row, text="NEW", font=("Segoe UI", 7, "bold"),
                         bg=c["RED"], fg=c["WHITE"], padx=4, pady=2).pack(side="right")

    # ── Analytics ─────────────────────────────────────────────────────────────
    def _analytics(self):
        c = T()
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner
        tk.Label(p, text="📊  Analytics Dashboard", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(anchor="w", padx=24, pady=(16,8))

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self._draw_charts(p, plt, FigureCanvasTkAgg, c)
        except ImportError:
            tk.Label(p,
                     text="📦  matplotlib not installed.\nRun:  pip install matplotlib",
                     font=("Segoe UI", 11), bg=c["BG_DARK"], fg=c["TEXT_DIM"],
                     justify="center").pack(pady=40)

    def _draw_charts(self, parent, plt, FigureCanvasTkAgg, c):
        logs  = load_logs()
        users = load_users()

        # ── Chart 1: Logins per day (bar) ─────────────────────────────────────
        from collections import Counter
        dates  = Counter(l.get("date","") for l in logs)
        sorted_dates = sorted(dates.keys())[-10:]  # last 10 days
        counts = [dates[d] for d in sorted_dates]

        fig1, ax1 = plt.subplots(figsize=(7, 2.8))
        fig1.patch.set_facecolor("#0F2040")
        ax1.set_facecolor("#0A1628")
        bars = ax1.bar(range(len(sorted_dates)), counts, color="#00D4C8", alpha=0.85)
        ax1.set_xticks(range(len(sorted_dates)))
        ax1.set_xticklabels([d[-5:] for d in sorted_dates],
                            rotation=30, ha="right", color="#B0C4D8", fontsize=7)
        ax1.tick_params(colors="#B0C4D8")
        ax1.set_title("Logins per Day (Last 10 Days)",
                      color="#FFFFFF", fontsize=9, fontweight="bold")
        for spine in ax1.spines.values(): spine.set_color("#1A3A5C")
        ax1.yaxis.label.set_color("#B0C4D8")
        fig1.tight_layout()
        cv1 = FigureCanvasTkAgg(fig1, parent)
        cv1.get_tk_widget().pack(padx=24, pady=8, fill="x")
        cv1.draw()
        plt.close(fig1)

        # ── Chart 2: Role distribution (pie) ──────────────────────────────────
        roles  = Counter(v.get("role","") for v in users.values())
        labels = list(roles.keys())
        sizes  = list(roles.values())
        pie_colors = ["#00D4C8","#FF4C6A","#A78BFA","#00E5A0"]

        if labels:
            fig2, ax2 = plt.subplots(figsize=(4, 2.8))
            fig2.patch.set_facecolor("#0F2040")
            ax2.set_facecolor("#0F2040")
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=labels, autopct="%1.0f%%",
                colors=pie_colors[:len(labels)],
                textprops={"color":"#B0C4D8","fontsize":8})
            for at in autotexts: at.set_color("#0A1628"); at.set_fontsize(8)
            ax2.set_title("Users by Role", color="#FFFFFF",
                          fontsize=9, fontweight="bold")
            fig2.tight_layout()
            cv2 = FigureCanvasTkAgg(fig2, parent)
            cv2.get_tk_widget().pack(padx=24, pady=8, fill="x")
            cv2.draw()
            plt.close(fig2)

        # ── Chart 3: Granted vs Denied (h-bar) ────────────────────────────────
        granted = sum(1 for l in logs if l.get("status")=="granted")
        denied  = sum(1 for l in logs if l.get("status")=="denied")
        fig3, ax3 = plt.subplots(figsize=(7, 1.6))
        fig3.patch.set_facecolor("#0F2040")
        ax3.set_facecolor("#0A1628")
        ax3.barh(["Granted","Denied"], [granted, denied],
                 color=["#00E5A0","#FF4C6A"], height=0.5)
        ax3.tick_params(colors="#B0C4D8")
        ax3.set_title("Granted vs Denied Access", color="#FFFFFF",
                      fontsize=9, fontweight="bold")
        for spine in ax3.spines.values(): spine.set_color("#1A3A5C")
        fig3.tight_layout()
        cv3 = FigureCanvasTkAgg(fig3, parent)
        cv3.get_tk_widget().pack(padx=24, pady=8, fill="x")
        cv3.draw()
        plt.close(fig3)

    # ── Reports ───────────────────────────────────────────────────────────────
    def _reports(self):
        c = T()
        sf = ScrollFrame(self._tab_frame); sf.pack(fill="both", expand=True)
        p  = sf.inner
        tk.Label(p, text="📤  Export Reports", font=("Segoe UI", 13, "bold"),
                 bg=c["BG_DARK"], fg=c["WHITE"]).pack(anchor="w", padx=24, pady=(16,8))

        for icon, title, desc, cmd in [
            ("📊","Access Log – Excel",
             "Full access log with timestamps, roles, statuses",
             self._exp_log_xl),
            ("📄","Access Log – PDF",
             "Formatted PDF report ready for printing",
             self._exp_log_pdf),
            ("🏥","Patient List – Excel",
             "All registered patients, records, appointment counts",
             self._exp_patients_xl),
            ("👤","Individual Patient PDF",
             "Full report for a selected patient",
             self._exp_patient_pdf),
        ]:
            card = tk.Frame(p, bg=c["BG_CARD"], highlightthickness=1,
                            highlightbackground=c["BORDER"])
            card.pack(fill="x", padx=24, pady=6)
            row = tk.Frame(card, bg=c["BG_CARD"]); row.pack(fill="x", padx=16, pady=12)
            tk.Label(row, text=icon, font=("Segoe UI", 22), bg=c["BG_CARD"]).pack(side="left", padx=(0,12))
            col = tk.Frame(row, bg=c["BG_CARD"]); col.pack(side="left", fill="x", expand=True)
            tk.Label(col, text=title, font=("Segoe UI", 11, "bold"),
                     bg=c["BG_CARD"], fg=c["WHITE"]).pack(anchor="w")
            tk.Label(col, text=desc, font=("Segoe UI", 8),
                     bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")
            styled_btn(row, "Export", cmd, pad_x=16, pad_y=8).pack(side="right")

    def _exp_log_xl(self):
        from modules.exporter import export_logs_excel
        path, err = export_logs_excel(load_logs())
        if err: messagebox.showerror("KLIKE", err)
        else:
            messagebox.showinfo("KLIKE – Exported ✅", f"Excel saved:\n{path}")
            try: os.startfile(path)
            except: pass

    def _exp_log_pdf(self):
        from modules.exporter import export_logs_pdf
        path, err = export_logs_pdf(load_logs())
        if err: messagebox.showerror("KLIKE", err)
        else:
            messagebox.showinfo("KLIKE – Exported ✅", f"PDF saved:\n{path}")
            try: os.startfile(path)
            except: pass

    def _exp_patients_xl(self):
        from modules.exporter import export_patients_excel
        path, err = export_patients_excel(load_patients())
        if err: messagebox.showerror("KLIKE", err)
        else:
            messagebox.showinfo("KLIKE – Exported ✅", f"Excel saved:\n{path}")
            try: os.startfile(path)
            except: pass

    def _exp_patient_pdf(self):
        patients = load_patients()
        if not patients:
            messagebox.showerror("KLIKE","No patients registered."); return
        name = simpledialog.askstring("KLIKE – Patient Report",
                                      "Enter patient name:\n\nAvailable:\n" +
                                      "\n".join(patients.keys()))
        if not name: return
        info = get_patient(name)
        if not info:
            messagebox.showerror("KLIKE", f'No record for "{name}".'); return
        from modules.exporter import export_patient_pdf
        path, err = export_patient_pdf(name, info)
        if err: messagebox.showerror("KLIKE", err)
        else:
            messagebox.showinfo("KLIKE – Exported ✅", f"PDF saved:\n{path}")
            try: os.startfile(path)
            except: pass


# ═══════════════════════════════════════════════════════════════════════════════
#  APP CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════

class KlikeApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("KLIKE v4 – Healthcare Face Recognition System")
        self.geometry("900x640")
        self.resizable(True, True)
        self.minsize(800, 580)
        self.configure(bg=T()["BG_DARK"])
        self.protocol("WM_DELETE_WINDOW", self._quit)

        # Ensure default Admin exists
        if "Admin" not in load_users():
            add_user("Admin", "Admin", "0000")

        self.active_name = None
        self.active_role = None
        self.num_images  = 0

        container = tk.Frame(self, bg=T()["BG_DARK"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in [StartPage, RegisterPage, CapturePage, LoginPage,
                          AdminLoginPage, AdminDashboard, PatientDashboard]:
            f = PageClass(parent=container, controller=self)
            self.frames[PageClass.__name__] = f
            f.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, name):
        self.frames[name].tkraise()

    def _quit(self):
        if messagebox.askokcancel("Exit KLIKE", "Securely exit the system?"):
            self.destroy()
