from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Student, Hostel, Room, Bed, Allocation, Fee, Attendance, Complaint, Notice, Visitor, LeaveRequest
from app.forms import LoginForm, StudentForm, HostelForm, RoomForm, AllocationForm, FeeForm, AttendanceForm, ComplaintForm, NoticeForm, VisitorForm, LeaveForm, ChangePasswordForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Student':
        return redirect(url_for('main.student_dashboard'))
    
    student_count = Student.query.count()
    room_count = Room.query.count()
    bed_count = Bed.query.count()
    occupied_beds = Bed.query.filter_by(status='Occupied').count()
    available_beds = bed_count - occupied_beds
    complaint_count = Complaint.query.filter_by(status='Pending').count()
    
    return render_template('dashboard.html', title='Admin Dashboard', 
                           student_count=student_count, room_count=room_count, 
                           bed_count=bed_count, occupied_beds=occupied_beds, 
                           available_beds=available_beds, complaint_count=complaint_count)

@main.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'Student':
        return redirect(url_for('main.dashboard'))
    
    student = current_user.student_profile
    allocation = Allocation.query.filter_by(student_id=student.id, status='Active').first() if student else None
    notices = Notice.query.order_by(Notice.publish_date.desc()).limit(5).all()
    leaves = LeaveRequest.query.filter_by(student_id=student.id).order_by(LeaveRequest.start_date.desc()).limit(3).all() if student else []
    
    return render_template('student_dashboard.html', title='Student Dashboard', student=student, allocation=allocation, notices=notices, leaves=leaves)

@main.route('/students')
@login_required
def students():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    all_students = Student.query.all()
    return render_template('students.html', title='Students', students=all_students)

@main.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = StudentForm()
    if form.validate_on_submit():
        existing = Student.query.filter_by(student_id_str=form.student_id_str.data).first()
        if existing:
            flash('Student ID already exists!', 'danger')
        else:
            hashed_pw = bcrypt.generate_password_hash(form.student_id_str.data).decode('utf-8')
            user = User(username=form.student_id_str.data, password_hash=hashed_pw, role='Student')
            db.session.add(user)
            db.session.flush() # Get user id before committing
            
            student = Student(
                user_id=user.id,
                student_id_str=form.student_id_str.data,
                name=form.name.data,
                gender=form.gender.data,
                course=form.course.data,
                year=form.year.data,
                phone=form.phone.data,
                address=form.address.data,
                guardian_name=form.guardian_name.data
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully! Account created with Student ID as password.', 'success')
            return redirect(url_for('main.students'))
            
    return render_template('add_student.html', title='Add Student', form=form)

@main.route('/student/<int:student_id>')
@login_required
def view_student(student_id):
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    student = Student.query.get_or_404(student_id)
    return render_template('view_student.html', title=f"Profile - {student.name}", student=student)

@main.route('/hostels')
@login_required
def hostels():
    if current_user.role != 'Admin':
        return redirect(url_for('main.dashboard'))
    all_hostels = Hostel.query.all()
    return render_template('hostels.html', title='Hostels', hostels=all_hostels)

@main.route('/hostels/add', methods=['GET', 'POST'])
@login_required
def add_hostel():
    if current_user.role != 'Admin':
        return redirect(url_for('main.dashboard'))
    form = HostelForm()
    if form.validate_on_submit():
        hostel = Hostel(
            name=form.name.data,
            type=form.type.data,
            location=form.location.data,
            capacity=form.capacity.data
        )
        db.session.add(hostel)
        db.session.commit()
        flash('Hostel added successfully!', 'success')
        return redirect(url_for('main.hostels'))
    return render_template('add_hostel.html', title='Add Hostel', form=form)

@main.route('/rooms')
@login_required
def rooms():
    if current_user.role != 'Admin':
        return redirect(url_for('main.dashboard'))
    all_rooms = Room.query.all()
    return render_template('rooms.html', title='Rooms', rooms=all_rooms)

@main.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    if current_user.role != 'Admin':
        return redirect(url_for('main.dashboard'))
    form = RoomForm()
    # Populate hostel choices
    form.hostel_id.choices = [(h.id, h.name) for h in Hostel.query.all()]
    
    if form.validate_on_submit():
        room = Room(
            hostel_id=form.hostel_id.data,
            room_number=form.room_number.data,
            floor=form.floor.data,
            capacity=form.capacity.data
        )
        db.session.add(room)
        db.session.flush() # Get room ID for beds
        
        # Auto-create beds based on capacity
        for i in range(1, form.capacity.data + 1):
            bed = Bed(room_id=room.id, bed_number=f"{form.room_number.data}-{i}")
            db.session.add(bed)
            
        db.session.commit()
        flash(f'Room {room.room_number} with {room.capacity} beds added successfully!', 'success')
        return redirect(url_for('main.rooms'))
    return render_template('add_room.html', title='Add Room', form=form)

@main.route('/allocations')
@login_required
def allocations():
    if current_user.role != 'Admin':
        return redirect(url_for('main.dashboard'))
    all_allocations = Allocation.query.all()
    return render_template('allocations.html', title='Room Allocations', allocations=all_allocations)

@main.route('/allocations/add', methods=['GET', 'POST'])
@login_required
def add_allocation():
    if current_user.role != 'Admin':
        return redirect(url_for('main.dashboard'))
    
    form = AllocationForm()
    
    active_allocated_student_ids = [a.student_id for a in Allocation.query.filter_by(status='Active').all()]
    if active_allocated_student_ids:
        available_students = Student.query.filter(~Student.id.in_(active_allocated_student_ids)).all()
    else:
        available_students = Student.query.all()
        
    form.student_id.choices = [(s.id, f"{s.student_id_str} - {s.name}") for s in available_students]
    
    available_beds = Bed.query.filter_by(status='Available').all()
    form.bed_id.choices = [(b.id, f"Bed {b.bed_number} (Room {b.room.room_number}, {b.room.hostel.name})") for b in available_beds]

    if form.validate_on_submit():
        bed = Bed.query.get(form.bed_id.data)
        if not bed or bed.status != 'Available':
            flash('Selected bed is no longer available.', 'danger')
            return redirect(url_for('main.add_allocation'))

        allocation = Allocation(
            student_id=form.student_id.data,
            room_id=bed.room_id,
            bed_id=bed.id,
            check_in_date=form.check_in_date.data
        )
        
        # Auto-generate a default semester fee of ₹15,000 for the new allocation
        from datetime import timedelta
        new_fee = Fee(
            student_id=form.student_id.data,
            amount=15000,
            due_date=form.check_in_date.data + timedelta(days=15)
        )
        db.session.add(new_fee)
        
        bed.status = 'Occupied'
        
        all_beds_in_room = Bed.query.filter_by(room_id=bed.room_id).all()
        if all(b.status == 'Occupied' for b in all_beds_in_room):
            bed.room.status = 'Full'
        else:
            bed.room.status = 'Partially Filled'

        db.session.add(allocation)
        db.session.commit()
        flash('Bed allocated successfully! A default fee of ₹15,000 has been auto-generated.', 'success')
        return redirect(url_for('main.allocations'))
        
    return render_template('add_allocation.html', title='Allocate Bed', form=form)

@main.route('/allocations/checkout/<int:allocation_id>', methods=['POST'])
@login_required
def checkout_allocation(allocation_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    alloc = Allocation.query.get_or_404(allocation_id)
    if alloc.status == 'Active':
        from datetime import datetime
        alloc.status = 'Inactive'
        alloc.check_out_date = datetime.now().date()
        
        bed = Bed.query.get(alloc.bed_id)
        if bed:
            bed.status = 'Available'
            occupied_count = sum(1 for b in bed.room.beds if b.status == 'Occupied' and b.id != bed.id)
            bed.room.status = 'Partially Filled' if occupied_count > 0 else 'Available'
            
        db.session.commit()
        flash('Student successfully checked out! The bed is now available.', 'success')
    return redirect(url_for('main.allocations'))

@main.route('/fees')
@login_required
def fees():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    all_fees = Fee.query.order_by(Fee.due_date.desc()).all()
    return render_template('fees.html', title='Fee Management', fees=all_fees)

@main.route('/fees/add', methods=['GET', 'POST'])
@login_required
def add_fee():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    form = FeeForm()
    form.student_id.choices = [(s.id, f"{s.student_id_str} - {s.name}") for s in Student.query.all()]
    if form.validate_on_submit():
        fee = Fee(student_id=form.student_id.data, amount=form.amount.data, due_date=form.due_date.data)
        db.session.add(fee)
        db.session.commit()
        flash('Fee record added!', 'success')
        return redirect(url_for('main.fees'))
    return render_template('add_fee.html', title='Add Fee', form=form)

@main.route('/fees/pay/<int:fee_id>', methods=['POST'])
@login_required
def pay_fee(fee_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    fee = Fee.query.get_or_404(fee_id)
    fee.payment_status = 'Paid'
    from datetime import datetime
    fee.payment_date = datetime.utcnow().date()
    db.session.commit()
    flash('Fee marked as paid!', 'success')
    return redirect(url_for('main.fees'))

@main.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    
    from datetime import date, datetime
    target_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        parsed_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        parsed_date = date.today()

    students = Student.query.all()
    
    # Fetch existing records for this date
    existing_records = Attendance.query.filter_by(date=parsed_date).all()
    status_map = {record.student_id: record.status for record in existing_records}

    if request.method == 'POST':
        for student in students:
            status = request.form.get(f'status_{student.id}')
            if status:
                if student.id in status_map:
                    record = next((r for r in existing_records if r.student_id == student.id), None)
                    if record and record.status != status:
                        record.status = status
                else:
                    new_att = Attendance(student_id=student.id, date=parsed_date, status=status)
                    db.session.add(new_att)
        
        db.session.commit()
        flash(f'Attendance saved for {parsed_date.strftime("%Y-%m-%d")}!', 'success')
        return redirect(url_for('main.attendance', date=target_date_str))

    return render_template('attendance.html', title='Bulk Attendance', students=students, status_map=status_map, target_date=parsed_date)

@main.route('/complaints')
@login_required
def complaints():
    if current_user.role == 'Admin':
        all_complaints = Complaint.query.order_by(Complaint.date.desc()).all()
    else:
        student = current_user.student_profile
        all_complaints = Complaint.query.filter_by(student_id=student.id).order_by(Complaint.date.desc()).all() if student else []
    return render_template('complaints.html', title='Complaints', complaints=all_complaints)

@main.route('/complaints/add', methods=['GET', 'POST'])
@login_required
def add_complaint():
    if current_user.role != 'Student': return redirect(url_for('main.dashboard'))
    form = ComplaintForm()
    if form.validate_on_submit():
        complaint = Complaint(student_id=current_user.student_profile.id, category=form.category.data, description=form.description.data, priority=form.priority.data)
        db.session.add(complaint)
        db.session.commit()
        flash('Complaint submitted!', 'success')
        return redirect(url_for('main.complaints'))
    return render_template('add_complaint.html', title='Raise Complaint', form=form)

@main.route('/complaints/resolve/<int:complaint_id>', methods=['POST'])
@login_required
def resolve_complaint(complaint_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = 'Resolved'
    db.session.commit()
    flash('Complaint resolved!', 'success')
    return redirect(url_for('main.complaints'))

@main.route('/notices')
@login_required
def notices():
    all_notices = Notice.query.order_by(Notice.publish_date.desc()).all()
    return render_template('notices.html', title='Notices', notices=all_notices)

@main.route('/notices/add', methods=['GET', 'POST'])
@login_required
def add_notice():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    form = NoticeForm()
    if form.validate_on_submit():
        notice = Notice(title=form.title.data, category=form.category.data, description=form.description.data, expiry_date=form.expiry_date.data)
        db.session.add(notice)
        db.session.commit()
        flash('Notice published!', 'success')
        return redirect(url_for('main.notices'))
    return render_template('add_notice.html', title='Publish Notice', form=form)

@main.route('/visitors')
@login_required
def visitors():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    all_visitors = Visitor.query.order_by(Visitor.date.desc()).all()
    return render_template('visitors.html', title='Visitors Log', visitors=all_visitors)

@main.route('/visitors/add', methods=['GET', 'POST'])
@login_required
def add_visitor():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    form = VisitorForm()
    form.student_id.choices = [(s.id, f"{s.student_id_str} - {s.name}") for s in Student.query.all()]
    if form.validate_on_submit():
        from datetime import datetime
        try:
            time_in_obj = datetime.strptime(form.time_in.data, '%H:%M').time()
        except ValueError:
            flash('Invalid time format. Use HH:MM', 'danger')
            return redirect(url_for('main.add_visitor'))
            
        visitor = Visitor(student_id=form.student_id.data, visitor_name=form.visitor_name.data, phone=form.phone.data, date=form.date.data, time_in=time_in_obj, purpose=form.purpose.data)
        db.session.add(visitor)
        db.session.commit()
        flash('Visitor logged successfully!', 'success')
        return redirect(url_for('main.visitors'))
    return render_template('add_visitor.html', title='Log Visitor', form=form)

@main.route('/leaves')
@login_required
def leaves():
    if current_user.role == 'Admin':
        all_leaves = LeaveRequest.query.order_by(LeaveRequest.start_date.desc()).all()
    else:
        student = current_user.student_profile
        all_leaves = LeaveRequest.query.filter_by(student_id=student.id).order_by(LeaveRequest.start_date.desc()).all() if student else []
    return render_template('leaves.html', title='Leave Requests', leaves=all_leaves)

@main.route('/leaves/add', methods=['GET', 'POST'])
@login_required
def add_leave():
    if current_user.role != 'Student': return redirect(url_for('main.dashboard'))
    form = LeaveForm()
    if form.validate_on_submit():
        leave = LeaveRequest(student_id=current_user.student_profile.id, start_date=form.start_date.data, end_date=form.end_date.data, reason=form.reason.data)
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted!', 'success')
        return redirect(url_for('main.leaves'))
    return render_template('add_leave.html', title='Apply for Leave', form=form)

@main.route('/leaves/approve/<int:leave_id>', methods=['POST'])
@login_required
def approve_leave(leave_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    leave = LeaveRequest.query.get_or_404(leave_id)
    leave.status = 'Approved'
    db.session.commit()
    flash('Leave approved!', 'success')
    return redirect(url_for('main.leaves'))

@main.route('/leaves/reject/<int:leave_id>', methods=['POST'])
@login_required
def reject_leave(leave_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    leave = LeaveRequest.query.get_or_404(leave_id)
    leave.status = 'Rejected'
    db.session.commit()
    flash('Leave rejected!', 'success')
    return redirect(url_for('main.leaves'))

@main.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    student = Student.query.get_or_404(student_id)
    
    # Free up the bed if the student is actively allocated
    active_alloc = Allocation.query.filter_by(student_id=student.id, status='Active').first()
    if active_alloc:
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
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('main.students'))

@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password_hash, form.old_password.data):
            flash('Current password is incorrect.', 'danger')
        elif form.new_password.data != form.confirm_password.data:
            flash('New passwords do not match.', 'danger')
        else:
            current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('main.dashboard' if current_user.role == 'Admin' else 'main.student_dashboard'))
    return render_template('change_password.html', title='Change Password', form=form)
