"""
Visitors Management View for HMS Desktop Application.
"""
from datetime import date, datetime
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, ModalDialog
from app import db_service

class VisitorsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Header
        self.header = PageHeader(
            self,
            title="Visitor Logs",
            subtitle="Security gate register for guests and parents visiting students",
            action_text="🚪 + Log Visitor",
            action_cmd=self._open_add_visitor_dialog
        )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Table Container
        table_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Table Header
        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header_row.pack(fill="x", padx=12, pady=(12, 6))
        header_row.pack_propagate(False)

        cols = [
            ("Visitor Name", 160),
            ("Phone", 120),
            ("Student Visited", 180),
            ("Date", 100),
            ("Time In", 90),
            ("Purpose", 240)
        ]
        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=8)

        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_visitors()

    def load_visitors(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        visitors = db_service.get_all_visitors()
        if not visitors:
            ctk.CTkLabel(self.table_body, text="No visitor entries logged yet.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=40)
            return

        for idx, v in enumerate(visitors):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=v['visitor_name'], font=theme.FONT_BODY_BOLD, width=160, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=v['phone'], font=theme.FONT_BODY, width=120, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"{v['student_name']} ({v['student_code']})", font=theme.FONT_BODY, width=180, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=v['date'], font=theme.FONT_BODY, width=100, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=v['time_in'], font=theme.FONT_BODY, width=90, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=v['purpose'], font=theme.FONT_BODY, width=240, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

    def _open_add_visitor_dialog(self):
        students = db_service.get_all_students()
        if not students:
            messagebox.showwarning("No Students", "Please register students first.", parent=self.winfo_toplevel())
            return

        dlg = ModalDialog(self.winfo_toplevel(), title="Log New Visitor", width=480, height=520)

        student_displays = [f"{s['student_id_str']} - {s['name']}" for s in students]
        e_student = ctk.CTkOptionMenu(dlg.body, values=student_displays)
        dlg.add_field("Select Student Visited *", e_student)

        e_name = dlg.add_field("Visitor Full Name *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Robert Smith"))
        e_phone = dlg.add_field("Contact Phone *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. 9876543210"))
        
        e_date = dlg.add_field("Date (YYYY-MM-DD) *", ctk.CTkEntry(dlg.body, placeholder_text=str(date.today())))
        e_date.insert(0, str(date.today()))

        curr_time = datetime.now().strftime("%H:%M")
        e_time = dlg.add_field("Time In (HH:MM) *", ctk.CTkEntry(dlg.body, placeholder_text=curr_time))
        e_time.insert(0, curr_time)

        e_purpose = dlg.add_field("Purpose of Visit *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Family visit / Book delivery"))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            chosen_stu = e_student.get()
            name = e_name.get().strip()
            phone = e_phone.get().strip()
            v_date = e_date.get().strip()
            v_time = e_time.get().strip()
            purpose = e_purpose.get().strip()

            stu_code = chosen_stu.split(" - ")[0]
            stu_obj = next((s for s in students if s["student_id_str"] == stu_code), None)

            if not (stu_obj and name and phone and purpose):
                lbl_msg.configure(text="Please fill in all visitor details.")
                return

            ok, res = db_service.add_visitor(stu_obj["id"], name, phone, v_date, v_time, purpose)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_visitors()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Save Entry", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
