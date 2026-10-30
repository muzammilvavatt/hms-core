from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    
    # Check if admin already exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', password_hash=hashed_pw, role='Admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully! (username: admin, password: admin123)")
    else:
        print("Admin user already exists.")
