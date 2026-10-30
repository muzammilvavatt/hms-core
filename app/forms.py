from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class StudentForm(FlaskForm):
    student_id_str = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    guardian_name = StringField('Guardian Name', validators=[DataRequired()])
    submit = SubmitField('Save Student')

class HostelForm(FlaskForm):
    name = StringField('Hostel Name', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Boys', 'Boys'), ('Girls', 'Girls')], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    submit = SubmitField('Save Hostel')

class RoomForm(FlaskForm):
    hostel_id = SelectField('Hostel', coerce=int, validators=[DataRequired()])
    room_number = StringField('Room Number', validators=[DataRequired()])
    floor = IntegerField('Floor', validators=[DataRequired()])
    capacity = IntegerField('Capacity (Beds)', validators=[DataRequired()])
    submit = SubmitField('Save Room')

class AllocationForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    bed_id = SelectField('Available Bed', coerce=int, validators=[DataRequired()])
    check_in_date = DateField('Check-in Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Allocate Bed')

class FeeForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    amount = IntegerField('Amount (Rs.)', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add Fee Record')

class AttendanceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave')], validators=[DataRequired()])
    submit = SubmitField('Mark Attendance')

class ComplaintForm(FlaskForm):
    category = SelectField('Category', choices=[('Electrical', 'Electrical'), ('Plumbing', 'Plumbing'), ('Cleaning', 'Cleaning'), ('Food', 'Food'), ('Other', 'Other')], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Normal', 'Normal'), ('High', 'High')], validators=[DataRequired()])
    submit = SubmitField('Submit Complaint')

class NoticeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Category', choices=[('General', 'General'), ('Event', 'Event'), ('Rules', 'Rules'), ('Urgent', 'Urgent')], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Publish Notice')

class VisitorForm(FlaskForm):
    student_id = SelectField('Visiting Student', coerce=int, validators=[DataRequired()])
    visitor_name = StringField('Visitor Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time_in = StringField('Time In (HH:MM)', validators=[DataRequired()])
    purpose = StringField('Purpose', validators=[DataRequired()])
    submit = SubmitField('Log Visitor')

class LeaveForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Apply for Leave')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Update Password')
