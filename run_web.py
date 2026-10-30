"""
Optional Web Runner for Hostel Management System (Flask Web Interface).
Run this if you ever need to access the web version.
"""
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Running Flask Web Application at http://127.0.0.1:5000")
    app.run(debug=True)
