"""
Main entry point for Hostel Management System (HMS).
Launches the 100% Python Desktop GUI (CustomTkinter).
"""
import sys
from app.db_service import init_database
from app.gui import launch_gui

if __name__ == '__main__':
    # Initialize SQLite database tables if not present
    init_database()
    
    print("=" * 60)
    print("  Hostel Management System (HMS Nexus) - Python Desktop GUI")
    print("  Framework: CustomTkinter (100% Pure Python - Zero HTML/CSS/JS)")
    print("=" * 60)
    print("Launching Desktop Application...")
    
    launch_gui()
