"""
Centralized Database Service for Hostel Management System (HMS).
Executes all queries and business operations using SQLAlchemy models within the Flask app context.
"""
from datetime import datetime, date, timedelta
from app import create_app, db, bcrypt
from app.models import (
    User, Student, Hostel, Room, Bed, Allocation,
    Fee, Attendance, Complaint, Notice, Visitor, LeaveRequest
)

_flask_app = None

def get_app():
    global _flask_app
    if _flask_app is None:
        _flask_app = create_app()
    return _flask_app

def init_database():
    """Ensure all database tables exist and default admin account is created."""
    app = get_app()
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password_hash=hashed_pw, role='Admin')
            db.session.add(admin)
            db.session.commit()

# ==========================================
# AUTHENTICATION & USERS
# ==========================================
def authenticate_user(username, password):
    """
    Validates user credentials.
    Returns (success: bool, user_data: dict or error_msg: str)
    """
    app = get_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, "User not found."
        
        if not bcrypt.check_password_hash(user.password_hash, password):
            return False, "Incorrect password."
        
        student_id = None
        student_name = None
        if user.role == 'Student' and user.student_profile:
            student_id = user.student_profile.id
            student_name = user.student_profile.name
            
        user_info = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "status": user.status,
            "student_id": student_id,
            "student_name": student_name
        }
        return True, user_info

def change_user_password(user_id, old_password, new_password):
    """Changes password for a user."""
    app = get_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."
        
        if not bcrypt.check_password_hash(user.password_hash, old_password):
            return False, "Current password is incorrect."
        
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        return True, "Password updated successfully."

# ==========================================
# DASHBOARD STATS
# ==========================================
def get_admin_dashboard_stats():
    """Returns overview metrics for Admin dashboard."""
    app = get_app()
    with app.app_context():
        student_count = Student.query.count()
        room_count = Room.query.count()
        bed_count = Bed.query.count()
        occupied_beds = Bed.query.filter_by(status='Occupied').count()
        available_beds = bed_count - occupied_beds
        pending_complaints = Complaint.query.filter_by(status='Pending').count()
        pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
        pending_fees = Fee.query.filter_by(payment_status='Pending').count()
        
        # Recent notices
        recent_notices = [
            {
                "id": n.id,
                "title": n.title,
                "category": n.category,
                "date": n.publish_date.strftime("%Y-%m-%d")
            }
            for n in Notice.query.order_by(Notice.publish_date.desc()).limit(5).all()
        ]
        
        return {
            "total_students": student_count,
            "total_rooms": room_count,
            "total_beds": bed_count,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "pending_complaints": pending_complaints,
            "pending_leaves": pending_leaves,
            "pending_fees": pending_fees,
            "recent_notices": recent_notices
        }

def get_student_dashboard_stats(student_id):
    """Returns stats and details for a specific student."""
    app = get_app()
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            return None
        
        active_alloc = Allocation.query.filter_by(student_id=student.id, status='Active').first()
        room_info = "Not Allocated"
        bed_info = "None"
        hostel_info = "None"
        if active_alloc and active_alloc.bed:
            bed_info = active_alloc.bed.bed_number
            room_info = f"Room {active_alloc.bed.room.room_number}"
            hostel_info = active_alloc.bed.room.hostel.name
            
        pending_fees = Fee.query.filter_by(student_id=student.id, payment_status='Pending').all()
        total_pending_amount = sum(f.amount for f in pending_fees)
        
        my_complaints = Complaint.query.filter_by(student_id=student.id).count()
        my_leaves = LeaveRequest.query.filter_by(student_id=student.id).count()
        
        # Attendance percentage
        att_records = Attendance.query.filter_by(student_id=student.id).all()
        total_days = len(att_records)
        present_days = sum(1 for a in att_records if a.status == 'Present')
        att_pct = round((present_days / total_days * 100), 1) if total_days > 0 else 100.0
        
        notices = [
            {
                "id": n.id,
                "title": n.title,
                "category": n.category,
                "description": n.description,
                "date": n.publish_date.strftime("%Y-%m-%d")
            }
            for n in Notice.query.order_by(Notice.publish_date.desc()).limit(5).all()
        ]
        
        return {
            "student_name": student.name,
            "student_id_str": student.student_id_str,
            "course": student.course,
            "year": student.year,
            "hostel": hostel_info,
            "room": room_info,
            "bed": bed_info,
            "has_allocation": active_alloc is not None,
            "pending_fee_count": len(pending_fees),
            "pending_fee_amount": total_pending_amount,
            "complaint_count": my_complaints,
            "leave_count": my_leaves,
            "attendance_percentage": att_pct,
            "notices": notices
        }

# ==========================================
# STUDENTS MODULE
# ==========================================
def get_all_students(search_term=""):
    """Returns list of all students with allocation details."""
    app = get_app()
    with app.app_context():
        query = Student.query
        students = query.all()
        result = []
        for s in students:
            active_alloc = Allocation.query.filter_by(student_id=s.id, status='Active').first()
            bed_str = "None"
            room_str = "None"
            hostel_str = "None"
            if active_alloc and active_alloc.bed:
                bed_str = active_alloc.bed.bed_number
                room_str = active_alloc.bed.room.room_number
                hostel_str = active_alloc.bed.room.hostel.name
                
            item = {
                "id": s.id,
                "student_id_str": s.student_id_str,
                "name": s.name,
                "gender": s.gender,
                "course": s.course,
                "year": s.year,
                "phone": s.phone,
                "address": s.address,
                "guardian_name": s.guardian_name,
                "hostel": hostel_str,
                "room": room_str,
                "bed": bed_str,
                "allocated": active_alloc is not None
            }
            if search_term:
                term = search_term.lower()
                if (term in s.student_id_str.lower() or
                    term in s.name.lower() or
                    term in s.course.lower() or
                    term in s.phone.lower()):
                    result.append(item)
            else:
                result.append(item)
        return result

def get_student_details(student_id):
    """Returns full student profile with fees, attendance, complaints, leaves."""
    app = get_app()
    with app.app_context():
        s = Student.query.get(student_id)
        if not s:
            return None
        
        active_alloc = Allocation.query.filter_by(student_id=s.id, status='Active').first()
        alloc_data = None
        if active_alloc and active_alloc.bed:
            alloc_data = {
                "hostel": active_alloc.bed.room.hostel.name,
                "room": active_alloc.bed.room.room_number,
                "bed": active_alloc.bed.bed_number,
                "check_in": active_alloc.check_in_date.strftime("%Y-%m-%d")
            }
            
        fees = [
            {
                "id": f.id,
                "amount": f.amount,
                "due_date": f.due_date.strftime("%Y-%m-%d"),
                "status": f.payment_status,
                "payment_date": f.payment_date.strftime("%Y-%m-%d") if f.payment_date else "N/A"
            }
            for f in s.fees
        ]
        
        complaints = [
            {
                "id": c.id,
                "category": c.category,
                "description": c.description,
                "priority": c.priority,
                "status": c.status,
                "date": c.date.strftime("%Y-%m-%d")
            }
            for c in s.complaints
        ]
        
        leaves = [
            {
                "id": l.id,
                "start_date": l.start_date.strftime("%Y-%m-%d"),
                "end_date": l.end_date.strftime("%Y-%m-%d"),
                "reason": l.reason,
                "status": l.status
            }
            for l in s.leave_requests
        ]
        
        return {
            "id": s.id,
            "student_id_str": s.student_id_str,
            "name": s.name,
            "gender": s.gender,
            "course": s.course,
            "year": s.year,
            "phone": s.phone,
            "address": s.address,
            "guardian_name": s.guardian_name,
            "allocation": alloc_data,
            "fees": fees,
            "complaints": complaints,
            "leaves": leaves
        }

def add_student(student_id_str, name, gender, course, year, phone, address, guardian_name):
    """Creates student account and profile."""
    app = get_app()
    with app.app_context():
        if Student.query.filter_by(student_id_str=student_id_str).first():
            return False, f"Student ID '{student_id_str}' already exists."
        
        if User.query.filter_by(username=student_id_str).first():
            return False, f"User with username '{student_id_str}' already exists."
        
        hashed_pw = bcrypt.generate_password_hash(student_id_str).decode('utf-8')
        user = User(username=student_id_str, password_hash=hashed_pw, role='Student')
        db.session.add(user)
        db.session.flush()
        
        student = Student(
            user_id=user.id,
            student_id_str=student_id_str,
            name=name,
            gender=gender,
            course=course,
            year=int(year),
            phone=phone,
            address=address,
            guardian_name=guardian_name
        )
        db.session.add(student)
        db.session.commit()
        return True, "Student registered successfully! Password is set to Student ID."

def delete_student(student_id):
    """Deletes student, frees up any active bed, and removes login account."""
    app = get_app()
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            return False, "Student not found."
        
        # Free bed if active allocation exists
        active_alloc = Allocation.query.filter_by(student_id=student.id, status='Active').first()
        if active_alloc and active_alloc.bed:
            bed = Bed.query.get(active_alloc.bed_id)
            if bed:
                bed.status = 'Available'
                occupied_count = sum(1 for b in bed.room.beds if b.status == 'Occupied' and b.id != bed.id)
                bed.room.status = 'Partially Filled' if occupied_count > 0 else 'Available'
                
        user = User.query.get(student.user_id)
        db.session.delete(student)
        if user:
            db.session.delete(user)
        db.session.commit()
        return True, "Student deleted successfully."

# ==========================================
# HOSTELS & ROOMS MODULE
# ==========================================
def get_all_hostels():
    """Returns list of hostels with room and bed counts."""
    app = get_app()
    with app.app_context():
        hostels = Hostel.query.all()
        result = []
        for h in hostels:
            room_count = len(h.rooms)
            total_beds = sum(len(r.beds) for r in h.rooms)
            occupied_beds = sum(sum(1 for b in r.beds if b.status == 'Occupied') for r in h.rooms)
            result.append({
                "id": h.id,
                "name": h.name,
                "type": h.type,
                "location": h.location,
                "capacity": h.capacity,
                "room_count": room_count,
                "total_beds": total_beds,
                "occupied_beds": occupied_beds,
                "available_beds": total_beds - occupied_beds,
                "status": h.status
            })
        return result

def add_hostel(name, hostel_type, location, capacity):
    """Adds a new hostel building block."""
    app = get_app()
    with app.app_context():
        hostel = Hostel(
            name=name,
            type=hostel_type,
            location=location,
            capacity=int(capacity)
        )
        db.session.add(hostel)
        db.session.commit()
        return True, "Hostel added successfully."

def get_all_rooms(hostel_id=None):
    """Returns list of rooms with hostel info and bed status."""
    app = get_app()
    with app.app_context():
        query = Room.query
        if hostel_id:
            query = query.filter_by(hostel_id=hostel_id)
        rooms = query.all()
        result = []
        for r in rooms:
            occupied = sum(1 for b in r.beds if b.status == 'Occupied')
            result.append({
                "id": r.id,
                "room_number": r.room_number,
                "hostel_name": r.hostel.name if r.hostel else "N/A",
                "floor": r.floor,
                "capacity": r.capacity,
                "occupied_beds": occupied,
                "available_beds": r.capacity - occupied,
                "status": r.status,
                "beds": [{"id": b.id, "number": b.bed_number, "status": b.status} for b in r.beds]
            })
        return result

def add_room(hostel_id, room_number, floor, capacity):
    """Creates a new room and automatically generates beds based on capacity."""
    app = get_app()
    with app.app_context():
        # Check duplicate room number in this hostel
        existing = Room.query.filter_by(hostel_id=hostel_id, room_number=room_number).first()
        if existing:
            return False, f"Room '{room_number}' already exists in this hostel."
        
        cap = int(capacity)
        room = Room(
            hostel_id=int(hostel_id),
            room_number=room_number,
            floor=int(floor),
            capacity=cap
        )
        db.session.add(room)
        db.session.flush()
        
        # Auto-create beds
        for i in range(1, cap + 1):
            bed = Bed(room_id=room.id, bed_number=f"{room_number}-{i}")
            db.session.add(bed)
            
        db.session.commit()
        return True, f"Room {room_number} created with {cap} beds generated."

# ==========================================
# ALLOCATIONS MODULE
# ==========================================
def get_all_allocations():
    """Returns list of all allocation records."""
    app = get_app()
    with app.app_context():
        allocations = Allocation.query.order_by(Allocation.id.desc()).all()
        result = []
        for a in allocations:
            student_name = a.student.name if a.student else "Unknown"
            student_code = a.student.student_id_str if a.student else "N/A"
            room_num = a.bed.room.room_number if a.bed and a.bed.room else "N/A"
            hostel_name = a.bed.room.hostel.name if a.bed and a.bed.room and a.bed.room.hostel else "N/A"
            bed_num = a.bed.bed_number if a.bed else "N/A"
            
            result.append({
                "id": a.id,
                "student_id": a.student_id,
                "student_name": student_name,
                "student_code": student_code,
                "hostel_name": hostel_name,
                "room_number": room_num,
                "bed_number": bed_num,
                "check_in_date": a.check_in_date.strftime("%Y-%m-%d"),
                "check_out_date": a.check_out_date.strftime("%Y-%m-%d") if a.check_out_date else "-",
                "status": a.status
            })
        return result

def get_unallocated_students():
    """Returns list of students who do NOT have an active allocation."""
    app = get_app()
    with app.app_context():
        active_student_ids = [a.student_id for a in Allocation.query.filter_by(status='Active').all()]
        students = Student.query.filter(~Student.id.in_(active_student_ids)).all() if active_student_ids else Student.query.all()
        return [{"id": s.id, "display": f"{s.student_id_str} - {s.name}"} for s in students]

def get_available_beds_dropdown():
    """Returns available beds with room and hostel details."""
    app = get_app()
    with app.app_context():
        beds = Bed.query.filter_by(status='Available').all()
        result = []
        for b in beds:
            hostel_name = b.room.hostel.name if b.room and b.room.hostel else "Hostel"
            room_num = b.room.room_number if b.room else "Room"
            result.append({
                "id": b.id,
                "display": f"Bed {b.bed_number} ({hostel_name}, Room {room_num})"
            })
        return result

def allocate_bed(student_id, bed_id, check_in_date_str):
    """
    Allocates a bed to a student:
    - Sets bed to Occupied
    - Recalculates room status
    - Auto-generates standard semester fee (₹15,000, due in 15 days)
    """
    app = get_app()
    with app.app_context():
        bed = Bed.query.get(bed_id)
        if not bed or bed.status != 'Available':
            return False, "Selected bed is no longer available."
        
        try:
            check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d").date()
        except ValueError:
            check_in_date = date.today()
            
        allocation = Allocation(
            student_id=int(student_id),
            room_id=bed.room_id,
            bed_id=bed.id,
            check_in_date=check_in_date,
            status='Active'
        )
        db.session.add(allocation)
        
        # Auto-generate ₹15,000 semester fee
        new_fee = Fee(
            student_id=int(student_id),
            amount=15000.0,
            due_date=check_in_date + timedelta(days=15),
            payment_status='Pending'
        )
        db.session.add(new_fee)
        
        bed.status = 'Occupied'
        all_beds = Bed.query.filter_by(room_id=bed.room_id).all()
        if all(b.status == 'Occupied' for b in all_beds):
            bed.room.status = 'Full'
        else:
            bed.room.status = 'Partially Filled'
            
        db.session.commit()
        return True, "Bed allocated successfully! Auto-generated semester fee of ₹15,000."

def checkout_allocation(allocation_id):
    """
    Checks out an allocation:
    - Marks allocation Inactive with today's checkout date
    - Frees the bed (Available)
    - Updates room occupancy status
    """
    app = get_app()
    with app.app_context():
        alloc = Allocation.query.get(allocation_id)
        if not alloc:
            return False, "Allocation not found."
        
        if alloc.status == 'Active':
            alloc.status = 'Inactive'
            alloc.check_out_date = date.today()
            
            bed = Bed.query.get(alloc.bed_id)
            if bed:
                bed.status = 'Available'
                occupied_count = sum(1 for b in bed.room.beds if b.status == 'Occupied' and b.id != bed.id)
                bed.room.status = 'Partially Filled' if occupied_count > 0 else 'Available'
                
            db.session.commit()
            return True, "Student checked out successfully. Bed is now available."
        return False, "Allocation is already inactive."

# ==========================================
# FEES MODULE
# ==========================================
def get_all_fees(status_filter=None):
    """Returns fee records, optionally filtered by status."""
    app = get_app()
    with app.app_context():
        query = Fee.query.order_by(Fee.due_date.desc())
        if status_filter and status_filter != 'All':
            query = query.filter_by(payment_status=status_filter)
        fees = query.all()
        result = []
        for f in fees:
            result.append({
                "id": f.id,
                "student_id": f.student_id,
                "student_name": f.student.name if f.student else "Unknown",
                "student_code": f.student.student_id_str if f.student else "N/A",
                "amount": f.amount,
                "due_date": f.due_date.strftime("%Y-%m-%d"),
                "payment_date": f.payment_date.strftime("%Y-%m-%d") if f.payment_date else "-",
                "status": f.payment_status
            })
        return result

def get_student_fees(student_id):
    """Returns fees for a specific student."""
    app = get_app()
    with app.app_context():
        fees = Fee.query.filter_by(student_id=student_id).order_by(Fee.due_date.desc()).all()
        return [
            {
                "id": f.id,
                "amount": f.amount,
                "due_date": f.due_date.strftime("%Y-%m-%d"),
                "payment_date": f.payment_date.strftime("%Y-%m-%d") if f.payment_date else "-",
                "status": f.payment_status
            }
            for f in fees
        ]

def add_fee(student_id, amount, due_date_str):
    """Creates a new fee record."""
    app = get_app()
    with app.app_context():
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            due_date = date.today() + timedelta(days=15)
            
        fee = Fee(
            student_id=int(student_id),
            amount=float(amount),
            due_date=due_date,
            payment_status='Pending'
        )
        db.session.add(fee)
        db.session.commit()
        return True, "Fee record created successfully."

def mark_fee_paid(fee_id):
    """Marks a fee as Paid with today's date."""
    app = get_app()
    with app.app_context():
        fee = Fee.query.get(fee_id)
        if not fee:
            return False, "Fee record not found."
        fee.payment_status = 'Paid'
        fee.payment_date = date.today()
        db.session.commit()
        return True, "Fee marked as Paid."

# ==========================================
# ATTENDANCE MODULE
# ==========================================
def get_attendance_for_date(target_date_str=None):
    """Returns all students and their attendance status for target date."""
    app = get_app()
    with app.app_context():
        if not target_date_str:
            target_date = date.today()
        else:
            try:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            except ValueError:
                target_date = date.today()
                
        students = Student.query.all()
        records = Attendance.query.filter_by(date=target_date).all()
        status_map = {r.student_id: r.status for r in records}
        
        result = []
        for s in students:
            result.append({
                "student_id": s.id,
                "student_code": s.student_id_str,
                "name": s.name,
                "course": s.course,
                "status": status_map.get(s.id, "Present") # Default to Present
            })
        return target_date.strftime("%Y-%m-%d"), result

def save_bulk_attendance(target_date_str, status_dict):
    """
    Saves bulk attendance records for date.
    status_dict: {student_id: 'Present' | 'Absent' | 'Leave'}
    """
    app = get_app()
    with app.app_context():
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today()
            
        existing_records = Attendance.query.filter_by(date=target_date).all()
        existing_map = {r.student_id: r for r in existing_records}
        
        for s_id, status in status_dict.items():
            student_id = int(s_id)
            if student_id in existing_map:
                existing_map[student_id].status = status
            else:
                new_att = Attendance(student_id=student_id, date=target_date, status=status)
                db.session.add(new_att)
                
        db.session.commit()
        return True, f"Attendance saved successfully for {target_date.strftime('%Y-%m-%d')}."

def get_student_attendance(student_id):
    """Returns attendance records and percentages for a student."""
    app = get_app()
    with app.app_context():
        records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
        total_days = len(records)
        present = sum(1 for r in records if r.status == 'Present')
        absent = sum(1 for r in records if r.status == 'Absent')
        leave = sum(1 for r in records if r.status == 'Leave')
        pct = round((present / total_days * 100), 1) if total_days > 0 else 100.0
        
        items = [
            {"date": r.date.strftime("%Y-%m-%d"), "status": r.status}
            for r in records
        ]
        return {
            "total_days": total_days,
            "present_days": present,
            "absent_days": absent,
            "leave_days": leave,
            "percentage": pct,
            "records": items
        }

# ==========================================
# COMPLAINTS MODULE
# ==========================================
def get_all_complaints():
    """Returns all complaints for admin."""
    app = get_app()
    with app.app_context():
        complaints = Complaint.query.order_by(Complaint.date.desc()).all()
        return [
            {
                "id": c.id,
                "student_id": c.student_id,
                "student_name": c.student.name if c.student else "Unknown",
                "student_code": c.student.student_id_str if c.student else "N/A",
                "category": c.category,
                "description": c.description,
                "priority": c.priority,
                "status": c.status,
                "date": c.date.strftime("%Y-%m-%d %H:%M")
            }
            for c in complaints
        ]

def get_student_complaints(student_id):
    """Returns complaints filed by a specific student."""
    app = get_app()
    with app.app_context():
        complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.date.desc()).all()
        return [
            {
                "id": c.id,
                "category": c.category,
                "description": c.description,
                "priority": c.priority,
                "status": c.status,
                "date": c.date.strftime("%Y-%m-%d %H:%M")
            }
            for c in complaints
        ]

def add_complaint(student_id, category, description, priority='Normal'):
    """Submits a new student complaint."""
    app = get_app()
    with app.app_context():
        complaint = Complaint(
            student_id=int(student_id),
            category=category,
            description=description,
            priority=priority,
            status='Pending'
        )
        db.session.add(complaint)
        db.session.commit()
        return True, "Complaint submitted successfully."

def resolve_complaint(complaint_id):
    """Marks a complaint as Resolved."""
    app = get_app()
    with app.app_context():
        c = Complaint.query.get(complaint_id)
        if not c:
            return False, "Complaint not found."
        c.status = 'Resolved'
        db.session.commit()
        return True, "Complaint resolved."

# ==========================================
# NOTICES MODULE
# ==========================================
def get_all_notices():
    """Returns all notice announcements."""
    app = get_app()
    with app.app_context():
        notices = Notice.query.order_by(Notice.publish_date.desc()).all()
        return [
            {
                "id": n.id,
                "title": n.title,
                "category": n.category,
                "description": n.description,
                "date": n.publish_date.strftime("%Y-%m-%d"),
                "expiry": n.expiry_date.strftime("%Y-%m-%d") if n.expiry_date else "None"
            }
            for n in notices
        ]

def add_notice(title, category, description, expiry_date_str=None):
    """Publishes a new notice."""
    app = get_app()
    with app.app_context():
        expiry = None
        if expiry_date_str:
            try:
                expiry = datetime.strptime(expiry_date_str, "%Y-%m-%d")
            except ValueError:
                expiry = None
                
        notice = Notice(
            title=title,
            category=category,
            description=description,
            expiry_date=expiry
        )
        db.session.add(notice)
        db.session.commit()
        return True, "Notice published successfully."

# ==========================================
# VISITORS MODULE
# ==========================================
def get_all_visitors():
    """Returns visitor logs."""
    app = get_app()
    with app.app_context():
        visitors = Visitor.query.order_by(Visitor.date.desc(), Visitor.time_in.desc()).all()
        return [
            {
                "id": v.id,
                "visitor_name": v.visitor_name,
                "phone": v.phone,
                "student_name": v.student.name if v.student else "Unknown",
                "student_code": v.student.student_id_str if v.student else "N/A",
                "date": v.date.strftime("%Y-%m-%d"),
                "time_in": v.time_in.strftime("%H:%M"),
                "time_out": v.time_out.strftime("%H:%M") if v.time_out else "-",
                "purpose": v.purpose
            }
            for v in visitors
        ]

def add_visitor(student_id, visitor_name, phone, date_str, time_in_str, purpose):
    """Logs a new visitor."""
    app = get_app()
    with app.app_context():
        try:
            v_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            v_date = date.today()
            
        try:
            v_time = datetime.strptime(time_in_str, "%H:%M").time()
        except ValueError:
            v_time = datetime.now().time()
            
        visitor = Visitor(
            student_id=int(student_id),
            visitor_name=visitor_name,
            phone=phone,
            date=v_date,
            time_in=v_time,
            purpose=purpose
        )
        db.session.add(visitor)
        db.session.commit()
        return True, "Visitor logged successfully."

# ==========================================
# LEAVE REQUESTS MODULE
# ==========================================
def get_all_leaves():
    """Returns all leave requests for admin."""
    app = get_app()
    with app.app_context():
        leaves = LeaveRequest.query.order_by(LeaveRequest.start_date.desc()).all()
        return [
            {
                "id": l.id,
                "student_id": l.student_id,
                "student_name": l.student.name if l.student else "Unknown",
                "student_code": l.student.student_id_str if l.student else "N/A",
                "start_date": l.start_date.strftime("%Y-%m-%d"),
                "end_date": l.end_date.strftime("%Y-%m-%d"),
                "reason": l.reason,
                "status": l.status
            }
            for l in leaves
        ]

def get_student_leaves(student_id):
    """Returns leave requests for a student."""
    app = get_app()
    with app.app_context():
        leaves = LeaveRequest.query.filter_by(student_id=student_id).order_by(LeaveRequest.start_date.desc()).all()
        return [
            {
                "id": l.id,
                "start_date": l.start_date.strftime("%Y-%m-%d"),
                "end_date": l.end_date.strftime("%Y-%m-%d"),
                "reason": l.reason,
                "status": l.status
            }
            for l in leaves
        ]

def add_leave_request(student_id, start_date_str, end_date_str, reason):
    """Submits a new student leave request."""
    app = get_app()
    with app.app_context():
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."
            
        leave = LeaveRequest(
            student_id=int(student_id),
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='Pending'
        )
        db.session.add(leave)
        db.session.commit()
        return True, "Leave request submitted successfully."

def update_leave_status(leave_id, new_status):
    """Updates status to Approved or Rejected."""
    app = get_app()
    with app.app_context():
        leave = LeaveRequest.query.get(leave_id)
        if not leave:
            return False, "Leave request not found."
        leave.status = new_status
        db.session.commit()
        return True, f"Leave request marked as {new_status}."
