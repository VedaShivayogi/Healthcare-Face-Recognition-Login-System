"""
KLIKE v4 – Shared UI building blocks.
Import: from modules.widgets import *
"""

import tkinter as tk
from tkinter import ttk
from modules.theme import T
import math


# ── Animated ECG header strip ─────────────────────────────────────────────────

class PulsingCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._phase = 0
        self._animate()

    def _ecg_y(self, x, phase, width, height):
        t = ((x + phase) % max(width, 1)) / max(width, 1)
        if 0.38 < t < 0.42:
            return height / 2 - 24
        elif 0.42 < t < 0.46:
            return height / 2 + 12
        elif 0.46 < t < 0.50:
            return height / 2 - 5
        else:
            return height / 2 + math.sin(t * 4 * math.pi) * 3

    def _animate(self):
        self.delete("ecg")
        w = self.winfo_reqwidth() or 900
        h = self.winfo_reqheight() or 44
        pts = []
        for x in range(0, w, 3):
            pts.extend([x, self._ecg_y(x, self._phase, w, h)])
        if len(pts) >= 4:
            self.create_line(pts, fill=T()["TEAL"], width=2,
                             smooth=True, tags="ecg")
        self._phase = (self._phase + 4) % w
        self.after(40, self._animate)


# ── Header ────────────────────────────────────────────────────────────────────

def make_header(parent, subtitle="Healthcare Face Authentication", back_cmd=None, controller=None):
    c = T()
    hdr = tk.Frame(parent, bg=c["BG_CARD"])
    hdr.pack(fill="x")
    PulsingCanvas(hdr, bg=c["BG_CARD"], height=40, highlightthickness=0).pack(fill="x")
    row = tk.Frame(hdr, bg=c["BG_CARD"])
    row.pack(fill="x", padx=24, pady=(0, 10))

    if back_cmd:
        tk.Button(row, text="←", command=back_cmd, bg=c["BG_CARD"],
                  fg=c["TEAL"], font=("Segoe UI", 14), relief="flat",
                  bd=0, cursor="hand2").pack(side="left", padx=(0, 8))

    cross = tk.Frame(row, bg=c["TEAL"], width=32, height=32)
    cross.pack_propagate(False)
    cross.pack(side="left", padx=(0, 8))
    tk.Label(cross, text="✚", font=("Segoe UI", 16, "bold"),
             bg=c["TEAL"], fg=c["BG_DARK"]).place(relx=.5, rely=.5, anchor="center")

    col = tk.Frame(row, bg=c["BG_CARD"])
    col.pack(side="left")
    tk.Label(col, text="KLIKE", font=("Segoe UI", 22, "bold"),
             bg=c["BG_CARD"], fg=c["TEAL"]).pack(anchor="w")
    tk.Label(col, text=subtitle, font=("Segoe UI", 8),
             bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(anchor="w")

    # Theme toggle on right
    if controller:
        def _toggle():
            from modules.db import get_theme, set_theme
            from modules import theme as th
            new = "light" if get_theme() == "dark" else "dark"
            set_theme(new)
            th.reload()
            messagebox.showinfo("KLIKE – Theme",
                f"Switched to {'☀ Light' if new=='light' else '🌙 Dark'} mode.\nRestart the app to apply fully.")
        tk.Button(row, text="☀/🌙", command=_toggle,
                  bg=c["BG_CARD"], fg=c["TEXT_DIM"], font=("Segoe UI", 9),
                  relief="flat", bd=0, cursor="hand2").pack(side="right")

    tk.Frame(hdr, bg=c["TEAL"], height=2).pack(fill="x")
    return hdr


# ── Status bar ────────────────────────────────────────────────────────────────

def make_status(parent, text="System Ready  •  All Services Operational", alert_count=0):
    c = T()
    bar = tk.Frame(parent, bg=c["BG_CARD"])
    bar.pack(fill="x", side="bottom")
    tk.Frame(bar, bg=c["TEAL"], height=1).pack(fill="x")
    row = tk.Frame(bar, bg=c["BG_CARD"])
    row.pack(fill="x", padx=12, pady=4)
    tk.Label(row, text="●", font=("Segoe UI", 7),
             bg=c["BG_CARD"], fg=c["GREEN"]).pack(side="left")
    tk.Label(row, text=f"  {text}", font=("Segoe UI", 8),
             bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(side="left")
    if alert_count > 0:
        tk.Label(row, text=f"  🔔 {alert_count} alert{'s' if alert_count>1 else ''}",
                 font=("Segoe UI", 8, "bold"),
                 bg=c["BG_CARD"], fg=c["RED"]).pack(side="left")
    tk.Label(row, text="KLIKE v4.0", font=("Segoe UI", 8),
             bg=c["BG_CARD"], fg=c["TEXT_DIM"]).pack(side="right")


# ── Buttons ───────────────────────────────────────────────────────────────────

def styled_btn(parent, text, command, bg=None, fg=None, pad_x=20, pad_y=9, font_size=10):
    c = T()
    bg  = bg or c["TEAL"]
    fg  = fg or c["BG_DARK"]
    dim = c["TEAL_DIM"] if bg == c["TEAL"] else "#1A3A5C"
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                    font=("Segoe UI", font_size, "bold"), relief="flat",
                    bd=0, cursor="hand2", padx=pad_x, pady=pad_y,
                    activebackground=dim, activeforeground=c["WHITE"])
    btn.bind("<Enter>", lambda e: btn.config(bg=dim))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def ghost_btn(parent, text, command, color=None):
    c = T()
    col = color or c["TEXT_DIM"]
    btn = tk.Button(parent, text=text, command=command,
                    bg=c["BG_DARK"], fg=col, font=("Segoe UI", 9),
                    relief="flat", bd=0, cursor="hand2", padx=14, pady=7,
                    activebackground=c["BORDER"], activeforeground=c["WHITE"])
    btn.bind("<Enter>", lambda e: btn.config(bg=c["BORDER"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=c["BG_DARK"]))
    return btn

def danger_btn(parent, text, command):
    c = T()
    return styled_btn(parent, text, command, bg=c["RED"], fg="#FFFFFF")

def success_btn(parent, text, command):
    c = T()
    return styled_btn(parent, text, command, bg=c["GREEN"], fg=c["BG_DARK"])


# ── Separator ─────────────────────────────────────────────────────────────────

def sep(parent):
    tk.Frame(parent, bg=T()["BORDER"], height=1).pack(fill="x", pady=6)


# ── Input field ───────────────────────────────────────────────────────────────

def make_input(parent, placeholder="", show=""):
    c = T()
    frame = tk.Frame(parent, bg=c["BG_INPUT"], highlightthickness=1,
                     highlightbackground=c["BORDER"], highlightcolor=c["TEAL"])
    kw = dict(show=show) if show else {}
    entry = tk.Entry(frame, bg=c["BG_INPUT"], fg=c["WHITE"],
                     font=("Segoe UI", 10), relief="flat", bd=6,
                     insertbackground=c["TEAL"], **kw)
    entry.pack(fill="x")
    entry.insert(0, placeholder)
    entry.config(fg=c["TEXT_DIM"])

    def fi(e):
        if entry.get() == placeholder:
            entry.delete(0, "end"); entry.config(fg=c["TEXT"])
        frame.config(highlightbackground=c["TEAL"])
    def fo(e):
        if not entry.get():
            entry.insert(0, placeholder); entry.config(fg=c["TEXT_DIM"])
        frame.config(highlightbackground=c["BORDER"])
    entry.bind("<FocusIn>", fi)
    entry.bind("<FocusOut>", fo)
    return frame, entry


# ── Card container ────────────────────────────────────────────────────────────

def make_card(parent, padx=30, pady=18):
    c = T()
    outer = tk.Frame(parent, bg=c["BG_DARK"])
    outer.pack(expand=True, fill="both", padx=padx, pady=pady)
    card = tk.Frame(outer, bg=c["BG_CARD"], highlightthickness=1,
                    highlightbackground=c["BORDER"])
    card.pack(expand=True, fill="both")
    inner = tk.Frame(card, bg=c["BG_CARD"])
    inner.pack(expand=True)
    return inner


# ── Role badge label ──────────────────────────────────────────────────────────

def role_badge(parent, role):
    from modules.theme import role_color
    c = T()
    color = role_color(role)
    f = tk.Frame(parent, bg=color, padx=8, pady=2)
    tk.Label(f, text=role, font=("Segoe UI", 8, "bold"),
             bg=color, fg=c["BG_DARK"]).pack()
    return f


# ── Scrollable frame ──────────────────────────────────────────────────────────

class ScrollFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        c = T()
        super().__init__(parent, bg=c["BG_DARK"], **kwargs)
        canvas = tk.Canvas(self, bg=c["BG_DARK"], highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(canvas, bg=c["BG_DARK"])
        win = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=canvas.winfo_width())
        self.inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        self.inner.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))


# ── Simple data table ─────────────────────────────────────────────────────────

def make_table(parent, headers, rows, col_widths=None):
    c = T()
    frame = tk.Frame(parent, bg=c["BG_DARK"])

    # Header row
    hrow = tk.Frame(frame, bg=c["TEAL"])
    hrow.pack(fill="x")
    for i, h in enumerate(headers):
        w = col_widths[i] if col_widths else 12
        tk.Label(hrow, text=h, font=("Segoe UI", 9, "bold"),
                 bg=c["TEAL"], fg=c["BG_DARK"], width=w,
                 anchor="w", padx=6, pady=4).pack(side="left")

    # Data rows
    for ri, row in enumerate(rows):
        bg = c["BG_CARD"] if ri % 2 == 0 else c["BG_INPUT"]
        drow = tk.Frame(frame, bg=bg)
        drow.pack(fill="x")
        for ci, cell in enumerate(row):
            w = col_widths[ci] if col_widths else 12
            tk.Label(drow, text=str(cell), font=("Segoe UI", 8),
                     bg=bg, fg=c["TEXT"], width=w,
                     anchor="w", padx=6, pady=3).pack(side="left")

    return frame
