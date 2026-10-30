# Hostel Management System (HMS Nexus)

A comprehensive Python-based desktop application developed to manage college and university hostel activities in a structured, automated, and secure manner. Built **100% in Python** using **CustomTkinter** and **SQLite / SQLAlchemy** with **zero HTML, CSS, or JavaScript**.

---

## 🚀 Key Highlights & Tech Stack

- **Frontend / UI**: **CustomTkinter** (Pure Python Desktop GUI)
  - Sleek modern design with dark mode and light mode support
  - Native desktop window with responsive cards, tables, segmented controls, and modal dialogs
  - **Zero HTML, CSS, or JavaScript dependencies** (complies strictly with academic guide restrictions)
- **Backend & Database**: Python, SQLAlchemy, SQLite, Bcrypt password encryption
- **Reporting**: FPDF for PDF report generation

---

## 📋 Core Modules & Features

1. **Role-Based Authentication**:
   - **Administrator Console**: Full administrative oversight and control.
   - **Student Portal**: Student self-service dashboard for allocated room details, fee receipts, leave requests, and maintenance complaints.
2. **Student Directory & Profiles**:
   - Add new students with auto-generated login credentials (initial password = Student ID).
   - Live real-time search by Student ID, Name, or Course.
   - Comprehensive profile modal displaying contact details, room assignment, fee records, attendance, and complaints.
   - Delete student with automatic bed de-allocation and user account removal.
3. **Hostels & Accommodations**:
   - Register hostel blocks (Boys, Girls, Co-ed) with capacity and location.
   - Create rooms with floor and capacity; automatically generates individual atomic Bed records (e.g. `A-101-1`, `A-101-2`).
   - Visual bed status badges (`Available`, `Occupied`).
4. **Room Allocation Pipeline (The Bridge)**:
   - Check-In: Allocate available beds to unallocated students.
   - Automatically recalculates room occupancy (`Available`, `Partially Filled`, `Full`).
   - Automatically generates a default semester fee record (₹15,000, due in 15 days).
   - Check-Out: Marks allocation inactive, logs checkout date, and instantly frees the bed.
5. **Fee Management**:
   - Track invoiced amounts, due dates, and payment dates.
   - Filter by All, Pending, or Paid invoices.
   - Single-click "Mark Paid" operation.
6. **Bulk Daily Attendance**:
   - Bulk roster view with interactive segmented buttons (`Present`, `Absent`, `Leave`) for every student.
   - Single-click "Mark All Present" batch helper.
   - Date picker to view or record past/current attendance.
7. **Maintenance Complaints**:
   - Students submit tickets categorized by issue type (Electrical, Plumbing, Wi-Fi, Furniture, etc.) and priority.
   - Admins review, prioritize, and mark tickets as `Resolved`.
8. **Notice Board & Announcements**:
   - Admins publish campus circulars with category tags.
   - Displayed prominently on student and admin dashboards.
9. **Visitor Security Gate Log**:
   - Security register logging visitor names, contact phone, student visited, date, time-in, and purpose.
10. **Leave Pass Requests**:
    - Students apply for leave with start date, end date, and reason.
    - Admins approve or reject leave passes with live status updates.

---

## 🛠️ Installation & Setup

1. **Activate Virtual Environment:**
   ```powershell
   # Windows PowerShell
   .\venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Desktop Application:**
   ```bash
   python run.py
   ```

*(Optional: If you ever need to run the older Flask web server, run `python run_web.py`)*

---

## 🔑 Default Login Credentials

- **Admin Account**:
  - Username: `admin`
  - Password: `admin123`
- **Sample Student Accounts**:
  - Username: `STU001` (or `STU002`, `STU003`, `STU004`, `STU005`)
  - Password: Same as Student ID (e.g. `STU001`)

---

## 🔄 Resetting / Seeding the Database

To reset the database with fresh sample hostel blocks, rooms, beds, and students:
```bash
python reset_db.py
```
