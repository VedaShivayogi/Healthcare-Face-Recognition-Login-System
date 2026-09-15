"""
KLIKE v4 – Theme engine. Call T() anywhere to get current palette.
Supports dark (default) and light modes.
"""

from modules.db import get_theme

DARK = {
    "BG_DARK":     "#0A1628",
    "BG_CARD":     "#0F2040",
    "BG_INPUT":    "#0D1F38",
    "BORDER":      "#1A3A5C",
    "TEAL":        "#00D4C8",
    "TEAL_DIM":    "#00897B",
    "WHITE":       "#FFFFFF",
    "WHITE_DIM":   "#B0C4D8",
    "RED":         "#FF4C6A",
    "GREEN":       "#00E5A0",
    "ORANGE":      "#FFA040",
    "PURPLE":      "#A78BFA",
    "TEXT":        "#FFFFFF",
    "TEXT_DIM":    "#B0C4D8",
}

LIGHT = {
    "BG_DARK":     "#EEF4FB",
    "BG_CARD":     "#FFFFFF",
    "BG_INPUT":    "#F0F6FF",
    "BORDER":      "#C5D8F0",
    "TEAL":        "#0097A7",
    "TEAL_DIM":    "#00796B",
    "WHITE":       "#1A2A3A",
    "WHITE_DIM":   "#4A6080",
    "RED":         "#D32F2F",
    "GREEN":       "#2E7D32",
    "ORANGE":      "#E65100",
    "PURPLE":      "#6A1B9A",
    "TEXT":        "#1A2A3A",
    "TEXT_DIM":    "#4A6080",
}

_current = None

def reload():
    global _current
    _current = LIGHT if get_theme() == "light" else DARK

def T():
    if _current is None:
        reload()
    return _current

# Role badge colours (theme-independent)
ROLE_COLORS = {
    "Admin":   "#FF4C6A",
    "Doctor":  "#00D4C8",
    "Nurse":   "#A78BFA",
    "Patient": "#00E5A0",
}

def role_color(role):
    return ROLE_COLORS.get(role, "#B0C4D8")
