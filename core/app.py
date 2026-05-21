```python
"""
KLIKE v4 – Healthcare Face Recognition Login System
Fixed Version for Render Deployment
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# =========================
# PATH SETUP
# =========================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "modules"))

# =========================
# IMPORT DATABASE FUNCTIONS
# =========================
try:
    from modules.db import (
        load_users,
        add_user,
        load_logs,
        load_alerts,
        unread_alert_count
    )
except Exception as e:
    print("Database import error:", e)

    # fallback dummy functions
    def load_users():
        return {}

    def add_user(name, role, pin):
        pass

    def load_logs():
        return []

    def load_alerts():
        return []

    def unread_alert_count():
        return 0

# =========================
# THEME COLORS
# =========================
THEME = {
    "BG": "#0A1628",
    "CARD": "#10233F",
    "TEXT": "#FFFFFF",
    "BTN": "#00D4C8",
    "RED": "#FF4C6A"
}

# =========================
# BASE PAGE
# =========================
class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["BG"])
        self.controller = controller

    def go(self, page):
        self.controller.show_frame(page)

# =========================
# START PAGE
# =========================
class StartPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(
            self,
            text="KLIKE v4",
            font=("Arial", 28, "bold"),
            bg=THEME["BG"],
            fg=THEME["TEXT"]
        ).pack(pady=30)

        tk.Label(
            self,
            text="Healthcare Face Recognition System",
            font=("Arial", 14),
            bg=THEME["BG"],
            fg=THEME["TEXT"]
        ).pack(pady=5)

        tk.Button(
            self,
            text="Register",
            font=("Arial", 12, "bold"),
            bg=THEME["BTN"],
            fg="black",
            width=20,
            command=lambda: controller.show_frame("RegisterPage")
        ).pack(pady=20)

        tk.Button(
            self,
            text="Login",
            font=("Arial", 12, "bold"),
            bg=THEME["BTN"],
            fg="black",
            width=20,
            command=lambda: controller.show_frame("LoginPage")
        ).pack(pady=10)

        tk.Button(
            self,
            text="Exit",
            font=("Arial", 12, "bold"),
            bg=THEME["RED"],
            fg="white",
            width=20,
            command=controller.destroy
        ).pack(pady=30)

# =========================
# REGISTER PAGE
# =========================
class RegisterPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(
            self,
            text="User Registration",
            font=("Arial", 22, "bold"),
            bg=THEME["BG"],
            fg=THEME["TEXT"]
        ).pack(pady=20)

        tk.Label(self, text="Full Name", bg=THEME["BG"], fg="white").pack()
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.pack(pady=5)

        tk.Label(self, text="PIN", bg=THEME["BG"], fg="white").pack()
        self.pin_entry = tk.Entry(self, width=30, show="*")
        self.pin_entry.pack(pady=5)

        tk.Button(
            self,
            text="Register",
            bg=THEME["BTN"],
            fg="black",
            width=20,
            command=self.register_user
        ).pack(pady=20)

        tk.Button(
            self,
            text="Back",
            bg="gray",
            fg="white",
            width=20,
            command=lambda: controller.show_frame("StartPage")
        ).pack()

    def register_user(self):
        name = self.name_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Enter name")
            return

        if not pin:
            messagebox.showerror("Error", "Enter PIN")
            return

        users = load_users()

        if name in users:
            messagebox.showerror("Error", "User already exists")
            return

        add_user(name, "Patient", pin)

        messagebox.showinfo("Success", "Registration completed")

        self.controller.show_frame("StartPage")

# =========================
# LOGIN PAGE
# =========================
class LoginPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(
            self,
            text="User Login",
            font=("Arial", 22, "bold"),
            bg=THEME["BG"],
            fg=THEME["TEXT"]
        ).pack(pady=20)

        tk.Label(self, text="Name", bg=THEME["BG"], fg="white").pack()
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.pack(pady=5)

        tk.Label(self, text="PIN", bg=THEME["BG"], fg="white").pack()
        self.pin_entry = tk.Entry(self, width=30, show="*")
        self.pin_entry.pack(pady=5)

        tk.Button(
            self,
            text="Login",
            bg=THEME["BTN"],
            fg="black",
            width=20,
            command=self.login
        ).pack(pady=20)

        tk.Button(
            self,
            text="Back",
            bg="gray",
            fg="white",
            width=20,
            command=lambda: controller.show_frame("StartPage")
        ).pack()

    def login(self):
        name = self.name_entry.get().strip()
        pin = self.pin_entry.get().strip()

        users = load_users()

        if name not in users:
            messagebox.showerror("Error", "User not found")
            return

        messagebox.showinfo("Success", f"Welcome {name}")

# =========================
# MAIN APPLICATION
# =========================
class KlikeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("KLIKE v4")
        self.geometry("900x600")
        self.configure(bg=THEME["BG"])

        # CREATE DEFAULT ADMIN
        try:
            users = load_users()

            if "Admin" not in users:
                add_user("Admin", "Admin", "0000")

        except Exception as e:
            print("Admin creation error:", e)

        container = tk.Frame(self, bg=THEME["BG"])
        container.pack(fill="both", expand=True)

        self.frames = {}

        for Page in [StartPage, RegisterPage, LoginPage]:
            page_name = Page.__name__

            frame = Page(container, self)

            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
```
