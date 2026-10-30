"""
GUI Module for Hostel Management System (HMS).
Pure Python Desktop User Interface using CustomTkinter.
"""
from app.gui.main_window import HMSApp

def launch_gui():
    """Launch the CustomTkinter GUI application."""
    app = HMSApp()
    app.mainloop()
