from app import create_app, db, bcrypt
from app.models import User, Student, Hostel, Room, Bed, Allocation, Fee, Notice
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # 1. Add Hostels
    h1 = Hostel(name="Alpha Block", type="Boys", location="North Campus", capacity=50)
    h2 = Hostel(name="Beta Block", type="Girls", location="South Campus", capacity=50)
    db.session.add_all([h1, h2])
    db.session.commit()

    # 2. Add Rooms & Beds
    for h in [h1, h2]:
        for floor in range(1, 3):
            for r in range(1, 4):
                room_num = f"{h.name[0]}-{floor}0{r}"
                room = Room(hostel_id=h.id, room_number=room_num, floor=floor, capacity=2)
                db.session.add(room)
                db.session.flush()
                # Add 2 beds per room
                b1 = Bed(room_id=room.id, bed_number=f"{room_num}-1")
                b2 = Bed(room_id=room.id, bed_number=f"{room_num}-2")
                db.session.add_all([b1, b2])
    db.session.commit()

    # 3. Add Students
    students_data = [
        ("STU001", "John Doe", "Male", "B.Tech", 1, "1234567890"),
        ("STU002", "Jane Smith", "Female", "B.Sc", 2, "0987654321"),
        ("STU003", "Alice Johnson", "Female", "MBA", 1, "1122334455"),
        ("STU004", "Bob Brown", "Male", "M.Tech", 2, "6677889900"),
    ]
    
    for s_id, name, gender, course, year, phone in students_data:
        # Check if exists
        if not Student.query.filter_by(student_id_str=s_id).first():
            hashed_pw = bcrypt.generate_password_hash(s_id).decode('utf-8')
            user = User(username=s_id, password_hash=hashed_pw, role='Student')
            db.session.add(user)
            db.session.flush()
            
            student = Student(
                user_id=user.id,
                student_id_str=s_id,
                name=name,
                gender=gender,
                course=course,
                year=year,
                phone=phone,
                address="123 Dummy Street, Tech City",
                guardian_name="Guardian of " + name.split()[0]
            )
            db.session.add(student)
    db.session.commit()

    # 4. Add some Notices
    n1 = Notice(title="Welcome to the New Semester", category="General", description="Classes will begin next week. Ensure all fees are paid on time to avoid late fines.", expiry_date=datetime.utcnow() + timedelta(days=30))
    n2 = Notice(title="Maintenance Work", category="Urgent", description="Water supply will be stopped for 2 hours tomorrow afternoon for routine maintenance.", expiry_date=datetime.utcnow() + timedelta(days=1))
    db.session.add_all([n1, n2])
    db.session.commit()

    # 5. Add Fees
    all_students = Student.query.all()
    for s in all_students:
        # Only add fee if none exists
        if not Fee.query.filter_by(student_id=s.id).first():
            fee = Fee(student_id=s.id, amount=15000, due_date=datetime.utcnow().date() + timedelta(days=15))
            db.session.add(fee)
    db.session.commit()

    print("Dummy data successfully populated!")
