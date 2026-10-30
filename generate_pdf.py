from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Nexus Hostel Management System - Workflow Documentation', border=False, ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Text content
    text = """
1. SYSTEM ARCHITECTURE & CORE ENTITIES
--------------------------------------------------
Nexus uses a relational database model to track all hostel operations automatically. The core physical entities are Hostels, Rooms, and Beds.
- Hostels: High-level container (e.g. "Boys Hostel A").
- Rooms: Belongs to a Hostel. When a Room with capacity N is created, N "Bed" records are automatically generated.
- Beds: The atomic physical unit. Has a status of 'Available' or 'Occupied'.


2. THE ALLOCATION PIPELINE (The Bridge)
--------------------------------------------------
The Allocation module is the bridge that links a Student to a specific Bed.
- Check-In: When an Admin allocates a bed to a student, the Bed's status locks to "Occupied". The Room status is automatically recalculated (e.g., from "Available" to "Partially Filled"). 
- Automated Billing: UPON successful allocation, the system intercepts this action and automatically generates a standard Semester Fee record (Rs. 15,000) for the student, due in 15 days. (This resolves the previous disconnected-fee flaw).
- Check-Out: When a student leaves, the Admin triggers "Check Out". The Allocation is marked "Inactive", the checkout date is logged, and the Bed is instantly marked "Available" for the next student.


3. DAILY OPERATIONS: ATTENDANCE
--------------------------------------------------
Attendance is an Admin-only, high-speed Bulk Operation.
- Default Assumption: When loading the Attendance page for today, all students are assumed "Present" unless already marked otherwise.
- Flow: The Admin simply toggles the dropdown for missing students to "Absent" and clicks Save. The database instantly creates or updates the attendance log for that specific date for the entire roster.


4. COMPLAINTS & MAINTENANCE WORKFLOW
--------------------------------------------------
- Raising: Students log in to their personal dashboard to raise Maintenance Complaints (e.g., "Fan broken"), tagged by category and priority.
- Resolving: Admins see a live count of Pending Complaints on their dashboard. Clicking "View Details" opens a modal displaying the full text. Upon fixing the issue, the Admin clicks "Resolve", moving the ticket to the Resolved history log.
    """
    
    for line in text.split('\n'):
        pdf.multi_cell(0, 7, txt=line)
        
    pdf.output("Nexus_Workflow.pdf")

if __name__ == "__main__":
    create_pdf()
