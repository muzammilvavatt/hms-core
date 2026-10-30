"""
Students Management View for HMS Desktop Application.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog
from app import db_service

class StudentsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Header
        self.header = PageHeader(
            self,
            title="Student Directory",
            subtitle="Manage enrolled students, profiles, and allocations",
            action_text="➕ Add Student",
            action_cmd=self._open_add_student_dialog
        )
        self.header.pack(fill="x", padx=20, pady=(16, 14))

        # Search & Filter Bar
        search_card = ctk.CTkFrame(
            self,
            fg_color=theme.BG_CARD,
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        search_card.pack(fill="x", padx=20, pady=(0, 14))

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill="x", padx=16, pady=12)

        self.entry_search = ctk.CTkEntry(
            search_inner,
            placeholder_text="🔍 Search by student name, ID, or course...",
            font=theme.FONT_BODY,
            height=38,
            corner_radius=theme.RADIUS_ENTRY
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_students())

        btn_search = ctk.CTkButton(
            search_inner,
            text="Search",
            width=90,
            height=38,
            font=theme.FONT_BUTTON,
            fg_color=theme.PRIMARY,
            command=self.load_students
        )
        btn_search.pack(side="left", padx=(0, 6))

        btn_reset = ctk.CTkButton(
            search_inner,
            text="Reset",
            width=80,
            height=38,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            hover_color=theme.BG_ROW_HOVER,
            command=self._reset_search
        )
        btn_reset.pack(side="left")

        # Table Container Card
        table_card = ctk.CTkFrame(
            self,
            fg_color=theme.BG_CARD,
            corner_radius=theme.RADIUS_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Table Column Header
        self.header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        self.header_row.pack(fill="x", padx=12, pady=(12, 6))
        self.header_row.pack_propagate(False)

        cols = [
            ("ID", 90),
            ("Name", 170),
            ("Gender", 80),
            ("Course & Year", 130),
            ("Phone", 110),
            ("Allocated Bed", 140),
            ("Actions", 160)
        ]
        for name, width in cols:
            lbl = ctk.CTkLabel(
                self.header_row,
                text=name,
                font=theme.FONT_BODY_BOLD,
                text_color=theme.TEXT_SECONDARY,
                width=width,
                anchor="w"
            )
            lbl.pack(side="left", padx=8)

        # Scrollable table body
        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_students()

    def _reset_search(self):
        self.entry_search.delete(0, "end")
        self.load_students()

    def load_students(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        search_query = self.entry_search.get().strip()
        students = db_service.get_all_students(search_query)

        if not students:
            empty_lbl = ctk.CTkLabel(
                self.table_body,
                text="No students found matching your search.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return

        for idx, s in enumerate(students):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # ID
            lbl_id = ctk.CTkLabel(row, text=s["student_id_str"], font=theme.FONT_BODY_BOLD, width=90, anchor="w", text_color=theme.PRIMARY)
            lbl_id.pack(side="left", padx=8)

            # Name
            lbl_name = ctk.CTkLabel(row, text=s["name"], font=theme.FONT_BODY, width=170, anchor="w", text_color=theme.TEXT_PRIMARY)
            lbl_name.pack(side="left", padx=8)

            # Gender
            lbl_gender = ctk.CTkLabel(row, text=s["gender"], font=theme.FONT_BODY, width=80, anchor="w", text_color=theme.TEXT_SECONDARY)
            lbl_gender.pack(side="left", padx=8)

            # Course & Year
            lbl_course = ctk.CTkLabel(row, text=f"{s['course']} (Yr {s['year']})", font=theme.FONT_BODY, width=130, anchor="w", text_color=theme.TEXT_PRIMARY)
            lbl_course.pack(side="left", padx=8)

            # Phone
            lbl_phone = ctk.CTkLabel(row, text=s["phone"], font=theme.FONT_BODY, width=110, anchor="w", text_color=theme.TEXT_SECONDARY)
            lbl_phone.pack(side="left", padx=8)

            # Allocated Bed / Status
            bed_frame = ctk.CTkFrame(row, fg_color="transparent", width=140)
            bed_frame.pack(side="left", padx=8)
            bed_frame.pack_propagate(False)
            if s["allocated"]:
                badge = StatusBadge(bed_frame, f"Bed {s['bed']}")
                badge.pack(anchor="w")
            else:
                lbl_none = ctk.CTkLabel(bed_frame, text="Not Allocated", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED)
                lbl_none.pack(anchor="w")

            # Actions
            action_frame = ctk.CTkFrame(row, fg_color="transparent", width=160)
            action_frame.pack(side="left", padx=8)

            btn_view = ctk.CTkButton(
                action_frame,
                text="Profile",
                width=68,
                height=28,
                font=theme.FONT_SMALL,
                fg_color=theme.PRIMARY,
                command=lambda sid=s["id"]: self._open_profile_dialog(sid)
            )
            btn_view.pack(side="left", padx=(0, 6))

            btn_del = ctk.CTkButton(
                action_frame,
                text="Delete",
                width=64,
                height=28,
                font=theme.FONT_SMALL,
                fg_color=theme.DANGER,
                hover_color=theme.DANGER_HOVER,
                command=lambda sid=s["id"], sname=s["name"]: self._confirm_delete(sid, sname)
            )
            btn_del.pack(side="left")

    def _confirm_delete(self, student_id, student_name):
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete student '{student_name}'?\n\nThis will remove their profile, free up their bed allocation, and delete their user account.",
            parent=self.winfo_toplevel()
        )
        if confirm:
            ok, msg = db_service.delete_student(student_id)
            if ok:
                messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
                self.load_students()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_add_student_dialog(self):
        dlg = ModalDialog(self.winfo_toplevel(), title="Add New Student", width=500, height=620)

        # Fields
        e_id = dlg.add_field("Student ID / Roll No *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. STU006"))
        e_name = dlg.add_field("Full Name *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Mohammed Rahul"))
        
        # Gender
        e_gender = ctk.CTkOptionMenu(dlg.body, values=["Male", "Female", "Other"])
        dlg.add_field("Gender *", e_gender)

        e_course = dlg.add_field("Course / Branch *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. B.Tech Computer Science"))
        e_year = ctk.CTkOptionMenu(dlg.body, values=["1", "2", "3", "4"])
        dlg.add_field("Academic Year *", e_year)

        e_phone = dlg.add_field("Contact Phone *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. 9876543210"))
        e_address = dlg.add_field("Permanent Address", ctk.CTkEntry(dlg.body, placeholder_text="City, State, PIN"))
        e_guardian = dlg.add_field("Guardian Name *", ctk.CTkEntry(dlg.body, placeholder_text="Parent or Guardian name"))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")

        def submit():
            sid = e_id.get().strip()
            name = e_name.get().strip()
            gender = e_gender.get()
            course = e_course.get().strip()
            year = e_year.get()
            phone = e_phone.get().strip()
            addr = e_address.get().strip() or "N/A"
            guardian = e_guardian.get().strip()

            if not (sid and name and course and phone and guardian):
                lbl_msg.configure(text="Please fill in all required fields marked with *.")
                return

            ok, res = db_service.add_student(sid, name, gender, course, year, phone, addr, guardian)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_students()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        ctk.CTkButton(btn_box, text="Register Student", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")

    def _open_profile_dialog(self, student_id):
        profile = db_service.get_student_details(student_id)
        if not profile:
            messagebox.showerror("Error", "Student profile not found.", parent=self.winfo_toplevel())
            return

        dlg = ModalDialog(self.winfo_toplevel(), title=f"Student Profile - {profile['name']}", width=600, height=660)

        # Overview Card
        card = ctk.CTkFrame(dlg.body, fg_color=theme.BG_CARD_ALT, corner_radius=10)
        card.pack(fill="x", pady=(0, 14), padx=4)

        info_items = [
            ("Student ID", profile["student_id_str"]),
            ("Full Name", profile["name"]),
            ("Gender", profile["gender"]),
            ("Course", f"{profile['course']} (Year {profile['year']})"),
            ("Phone", profile["phone"]),
            ("Guardian", profile["guardian_name"]),
            ("Address", profile["address"]),
        ]
        for label, val in info_items:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(row, text=label, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=theme.FONT_BODY, text_color=theme.TEXT_PRIMARY, anchor="w").pack(side="left")

        # Allocation Status
        alloc_card = ctk.CTkFrame(dlg.body, fg_color=theme.BG_CARD_ALT, corner_radius=10)
        alloc_card.pack(fill="x", pady=(0, 14), padx=4)
        ctk.CTkLabel(alloc_card, text="Hostel Allocation", font=theme.FONT_SECTION_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(10, 6))

        if profile["allocation"]:
            alloc = profile["allocation"]
            a_text = f"🏢 Hostel: {alloc['hostel']}  |  🚪 Room: {alloc['room']}  |  🛏️ Bed: {alloc['bed']}\n📅 Check-In Date: {alloc['check_in']}"
            ctk.CTkLabel(alloc_card, text=a_text, font=theme.FONT_BODY, text_color=theme.SUCCESS, justify="left").pack(anchor="w", padx=16, pady=(0, 12))
        else:
            ctk.CTkLabel(alloc_card, text="⚠️ Currently not allocated to any bed.", font=theme.FONT_BODY, text_color=theme.WARNING).pack(anchor="w", padx=16, pady=(0, 12))

        # Fee Summary
        fee_card = ctk.CTkFrame(dlg.body, fg_color=theme.BG_CARD_ALT, corner_radius=10)
        fee_card.pack(fill="x", pady=(0, 14), padx=4)
        ctk.CTkLabel(fee_card, text="Recent Fees", font=theme.FONT_SECTION_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(10, 6))

        if profile["fees"]:
            for f in profile["fees"][:3]:
                f_row = ctk.CTkFrame(fee_card, fg_color="transparent")
                f_row.pack(fill="x", padx=16, pady=3)
                ctk.CTkLabel(f_row, text=f"₹{f['amount']:,.0f}", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY).pack(side="left")
                ctk.CTkLabel(f_row, text=f"Due: {f['due_date']}", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(side="left", padx=14)
                StatusBadge(f_row, f['status']).pack(side="right")
        else:
            ctk.CTkLabel(fee_card, text="No fee records found.", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 8))

        ctk.CTkButton(dlg.footer, text="Close", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
