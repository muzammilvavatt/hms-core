from app import create_app, db, bcrypt
from app.models import User, Student, Hostel, Room, Bed, Allocation, Fee, Attendance, Complaint, Notice, Visitor, LeaveRequest
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # 1. Reset Database
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()

    # 2. Add Admin User
    admin_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin_user = User(username='admin', password_hash=admin_pw, role='Admin')
    db.session.add(admin_user)
    db.session.commit()

    # 3. Add Hostels, Rooms, and Beds
    h1 = Hostel(name="Alpha Block", type="Boys", location="North Campus", capacity=50)
    h2 = Hostel(name="Beta Block", type="Girls", location="South Campus", capacity=50)
    db.session.add_all([h1, h2])
    db.session.commit()

    for h in [h1, h2]:
        for floor in range(1, 3):
            for r in range(1, 4):
                room_num = f"{h.name[0]}-{floor}0{r}"
                room = Room(hostel_id=h.id, room_number=room_num, floor=floor, capacity=2)
                db.session.add(room)
                db.session.flush()
                b1 = Bed(room_id=room.id, bed_number=f"{room_num}-1")
                b2 = Bed(room_id=room.id, bed_number=f"{room_num}-2")
                db.session.add_all([b1, b2])
    db.session.commit()

    # 4. Add Students
    students_data = [
        ("STU001", "John Doe", "Male", "B.Tech", 1, "1234567890"),
        ("STU002", "Jane Smith", "Female", "B.Sc", 2, "0987654321"),
        ("STU003", "Alice Johnson", "Female", "MBA", 1, "1122334455"),
        ("STU004", "Bob Brown", "Male", "M.Tech", 2, "6677889900"),
    ]
    
    student_objs = []
    for s_id, name, gender, course, year, phone in students_data:
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
        student_objs.append(student)
    db.session.commit()

    # 5. Add Allocations (Allocate bed for STU001, STU002, STU003)
    bed1 = Bed.query.filter(Bed.bed_number.like('A%')).first()
    bed1.status = 'Occupied'
    alloc1 = Allocation(student_id=student_objs[0].id, room_id=bed1.room_id, bed_id=bed1.id, check_in_date=datetime.now().date())
    
    bed2 = Bed.query.filter(Bed.bed_number.like('B%')).offset(0).first()
    bed3 = Bed.query.filter(Bed.bed_number.like('B%')).offset(1).first()
    bed2.status = 'Occupied'
    bed3.status = 'Occupied'
    alloc2 = Allocation(student_id=student_objs[1].id, room_id=bed2.room_id, bed_id=bed2.id, check_in_date=datetime.now().date())
    alloc3 = Allocation(student_id=student_objs[2].id, room_id=bed3.room_id, bed_id=bed3.id, check_in_date=datetime.now().date())
    
    db.session.add_all([alloc1, alloc2, alloc3])
    db.session.commit()

    # Update Room statuses
    for room in Room.query.all():
        occupied = sum(1 for b in room.beds if b.status == 'Occupied')
        if occupied == room.capacity:
            room.status = 'Full'
        elif occupied > 0:
            room.status = 'Partially Filled'
    db.session.commit()

    # 6. Add Fees
    fee1 = Fee(student_id=student_objs[0].id, amount=15000, due_date=datetime.now().date() + timedelta(days=15))
    fee2 = Fee(student_id=student_objs[1].id, amount=15000, due_date=datetime.now().date() - timedelta(days=5), payment_status='Paid', payment_date=datetime.now().date())
    fee3 = Fee(student_id=student_objs[2].id, amount=18000, due_date=datetime.now().date() + timedelta(days=10))
    fee4 = Fee(student_id=student_objs[3].id, amount=20000, due_date=datetime.now().date() + timedelta(days=30))
    db.session.add_all([fee1, fee2, fee3, fee4])
    db.session.commit()

    # 7. Add Attendance
    att1 = Attendance(student_id=student_objs[0].id, date=datetime.now().date(), status='Present')
    att2 = Attendance(student_id=student_objs[1].id, date=datetime.now().date(), status='Present')
    att3 = Attendance(student_id=student_objs[2].id, date=datetime.now().date(), status='Absent')
    db.session.add_all([att1, att2, att3])
    db.session.commit()

    # 8. Add Visitors
    vis1 = Visitor(student_id=student_objs[0].id, visitor_name="Mark Doe", phone="11223344", date=datetime.now().date(), time_in=datetime.now().time(), purpose="Family Visit")
    db.session.add(vis1)
    db.session.commit()

    # 9. Add Leave Requests
    leave1 = LeaveRequest(student_id=student_objs[1].id, start_date=datetime.now().date() + timedelta(days=2), end_date=datetime.now().date() + timedelta(days=5), reason="Going home for festival", status='Pending')
    leave2 = LeaveRequest(student_id=student_objs[2].id, start_date=datetime.now().date() - timedelta(days=5), end_date=datetime.now().date() - timedelta(days=2), reason="Medical Leave", status='Approved')
    db.session.add_all([leave1, leave2])
    db.session.commit()

    # 10. Add Complaints
    comp1 = Complaint(student_id=student_objs[0].id, category="Electrical", description="Fan is making too much noise in room A-101", priority="Normal", status="Pending")
    comp2 = Complaint(student_id=student_objs[1].id, category="Plumbing", description="Leaking tap in bathroom on 1st floor", priority="High", status="Resolved")
    db.session.add_all([comp1, comp2])
    db.session.commit()

    # 11. Add Notices
    n1 = Notice(title="Welcome to the New Semester", category="General", description="Classes will begin next week. Ensure all fees are paid on time to avoid late fines.", expiry_date=datetime.now().date() + timedelta(days=30))
    n2 = Notice(title="Maintenance Work", category="Urgent", description="Water supply will be stopped for 2 hours tomorrow afternoon for routine maintenance.", expiry_date=datetime.now().date() + timedelta(days=1))
    db.session.add_all([n1, n2])
    db.session.commit()

    print("Complete mock database generated successfully!")
