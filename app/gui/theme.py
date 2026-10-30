"""
Design tokens, color schemes, and styling constants for HMS GUI.
Supports seamless switching between Dark and Light mode.
"""

# Color Palette Tuples: (Light Mode, Dark Mode)
BG_MAIN = ("#F1F5F9", "#0F172A")          # Main screen background
BG_SIDEBAR = ("#FFFFFF", "#1E293B")       # Sidebar surface
BG_CARD = ("#FFFFFF", "#1E293B")          # Card / Surface background
BG_CARD_ALT = ("#F8FAFC", "#0F172A")      # Card inner alt background
BG_ROW_HOVER = ("#E2E8F0", "#334155")     # Row hover/active state
BORDER_COLOR = ("#E2E8F0", "#334155")     # Borders and dividers

# Brand and Status Colors
PRIMARY = ("#2563EB", "#3B82F6")          # Vibrant Royal Blue
PRIMARY_HOVER = ("#1D4ED8", "#2563EB")
SUCCESS = ("#10B981", "#10B981")          # Emerald Green
SUCCESS_HOVER = ("#059669", "#059669")
DANGER = ("#EF4444", "#EF4444")           # Rose Red
DANGER_HOVER = ("#DC2626", "#DC2626")
WARNING = ("#F59E0B", "#F59E0B")          # Amber Yellow
WARNING_HOVER = ("#D97706", "#D97706")
INFO = ("#06B6D4", "#06B6D4")             # Cyan / Sky
SECONDARY = ("#64748B", "#64748B")        # Slate Muted
SECONDARY_HOVER = ("#475569", "#475569")

# Text Colors
TEXT_PRIMARY = ("#0F172A", "#F8FAFC")     # High contrast primary text
TEXT_SECONDARY = ("#64748B", "#94A3B8")   # Subdued text
TEXT_MUTED = ("#94A3B8", "#64748B")       # Disabled / hint text
TEXT_WHITE = "#FFFFFF"

# Fonts
FONT_APP_TITLE = ("Segoe UI", 18, "bold")
FONT_TITLE_LARGE = ("Segoe UI", 22, "bold")
FONT_SECTION_TITLE = ("Segoe UI", 16, "bold")
FONT_CARD_VALUE = ("Segoe UI", 24, "bold")
FONT_CARD_LABEL = ("Segoe UI", 11, "normal")
FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 12, "normal")
FONT_SMALL = ("Segoe UI", 10, "normal")
FONT_BUTTON = ("Segoe UI", 12, "bold")

# Dimensions & Radius
RADIUS_CARD = 12
RADIUS_BUTTON = 8
RADIUS_ENTRY = 8
RADIUS_BADGE = 6
