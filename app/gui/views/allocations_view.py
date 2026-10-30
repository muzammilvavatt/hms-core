"""
Room & Bed Allocations Management View for HMS Desktop Application.
"""
from datetime import date
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog
from app import db_service

class AllocationsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Header
        self.header = PageHeader(
            self,
            title="Room Allocations",
            subtitle="Manage student bed assignments, check-ins, and check-outs",
            action_text="🛏️ + Allocate Bed",
            action_cmd=self._open_allocate_dialog
        )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Workflow Info Card
        info_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        info_card.pack(fill="x", padx=20, pady=(0, 14))

        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            info_inner,
            text="💡 Allocation Pipeline: Assigning a bed locks it to 'Occupied', updates room occupancy, and automatically generates a standard semester fee of ₹15,000 for the student.",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            wraplength=850,
            justify="left"
        ).pack(anchor="w")

        # Table Container
        table_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Filter bar
        filter_bar = ctk.CTkFrame(table_card, fg_color="transparent")
        filter_bar.pack(fill="x", padx=14, pady=(12, 6))

        self.seg_filter = ctk.CTkSegmentedButton(
            filter_bar,
            values=["All Allocations", "Active Only", "Inactive Only"],
            command=lambda v: self.load_allocations()
        )
        self.seg_filter.set("Active Only")
        self.seg_filter.pack(side="left")

        # Table Header
        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header_row.pack(fill="x", padx=12, pady=(8, 6))
        header_row.pack_propagate(False)

        cols = [
            ("Student", 170),
            ("Hostel", 130),
            ("Room", 90),
            ("Bed", 90),
            ("Check-In", 110),
            ("Check-Out", 110),
            ("Status", 90),
            ("Action", 110)
        ]
        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=8)

        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_allocations()

    def load_allocations(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        allocations = db_service.get_all_allocations()
        filter_val = self.seg_filter.get()

        if filter_val == "Active Only":
            allocations = [a for a in allocations if a["status"] == "Active"]
        elif filter_val == "Inactive Only":
            allocations = [a for a in allocations if a["status"] == "Inactive"]

        if not allocations:
            ctk.CTkLabel(self.table_body, text="No allocation records found.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=30)
            return

        for idx, a in enumerate(allocations):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"{a['student_name']} ({a['student_code']})", font=theme.FONT_BODY_BOLD, width=170, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=a['hostel_name'], font=theme.FONT_BODY, width=130, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"Rm {a['room_number']}", font=theme.FONT_BODY, width=90, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=a['bed_number'], font=theme.FONT_BODY_BOLD, width=90, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=a['check_in_date'], font=theme.FONT_BODY, width=110, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=a['check_out_date'], font=theme.FONT_BODY, width=110, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

            status_frame = ctk.CTkFrame(row, fg_color="transparent", width=90)
            status_frame.pack(side="left", padx=8)
            StatusBadge(status_frame, a['status']).pack(anchor="w")

            action_frame = ctk.CTkFrame(row, fg_color="transparent", width=110)
            action_frame.pack(side="left", padx=8)

            if a["status"] == "Active":
                btn_checkout = ctk.CTkButton(
                    action_frame,
                    text="Check Out",
                    font=theme.FONT_SMALL,
                    width=85,
                    height=28,
                    fg_color=theme.DANGER,
                    hover_color=theme.DANGER_HOVER,
                    command=lambda aid=a["id"], sname=a["student_name"]: self._confirm_checkout(aid, sname)
                )
                btn_checkout.pack(anchor="w")
            else:
                ctk.CTkLabel(action_frame, text="Completed", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED).pack(anchor="w")

    def _confirm_checkout(self, alloc_id, student_name):
        confirm = messagebox.askyesno(
            "Confirm Check-Out",
            f"Check out student '{student_name}'?\n\nThis will mark the allocation inactive, record today's checkout date, and instantly free up the bed for new allocations.",
            parent=self.winfo_toplevel()
        )
        if confirm:
            ok, msg = db_service.checkout_allocation(alloc_id)
            if ok:
                messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
                self.load_allocations()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_allocate_dialog(self):
        students = db_service.get_unallocated_students()
        if not students:
            messagebox.showinfo("All Allocated", "All registered students currently have active bed allocations.", parent=self.winfo_toplevel())
            return

        beds = db_service.get_available_beds_dropdown()
        if not beds:
            messagebox.showwarning("No Beds Available", "There are currently no available beds. Please add rooms or check out existing students.", parent=self.winfo_toplevel())
            return

        dlg = ModalDialog(self.winfo_toplevel(), title="Allocate Bed to Student", width=500, height=480)

        student_displays = [s["display"] for s in students]
        e_student = ctk.CTkOptionMenu(dlg.body, values=student_displays)
        dlg.add_field("Select Unallocated Student *", e_student)

        bed_displays = [b["display"] for b in beds]
        e_bed = ctk.CTkOptionMenu(dlg.body, values=bed_displays)
        dlg.add_field("Select Available Bed *", e_bed)

        e_date = dlg.add_field("Check-In Date (YYYY-MM-DD) *", ctk.CTkEntry(dlg.body, placeholder_text=str(date.today())))
        e_date.insert(0, str(date.today()))

        note_lbl = ctk.CTkLabel(
            dlg.body,
            text="ℹ️ Note: Allocating a bed will automatically generate an initial semester fee invoice of ₹15,000 due in 15 days.",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            wraplength=420,
            justify="left"
        )
        note_lbl.pack(fill="x", pady=(10, 4))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            chosen_stu_text = e_student.get()
            chosen_bed_text = e_bed.get()
            in_date = e_date.get().strip() or str(date.today())

            stu_obj = next((s for s in students if s["display"] == chosen_stu_text), None)
            bed_obj = next((b for b in beds if b["display"] == chosen_bed_text), None)

            if not stu_obj or not bed_obj:
                lbl_msg.configure(text="Please make valid selections.")
                return

            ok, res = db_service.allocate_bed(stu_obj["id"], bed_obj["id"], in_date)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_allocations()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Confirm Allocation", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
