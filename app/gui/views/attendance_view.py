"""
Bulk Daily Attendance View for HMS Desktop Application.
"""
from datetime import date
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader
from app import db_service

class AttendanceView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.student_selectors = {} # student_id: CTkSegmentedButton

        # Header
        self.header = PageHeader(
            self,
            title="Daily Attendance Roster",
            subtitle="Perform bulk attendance logging for all enrolled students",
            action_text="💾 Save Attendance",
            action_cmd=self._save_attendance,
            action_color=theme.SUCCESS
        )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Date & Batch Controls Card
        ctrl_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        ctrl_card.pack(fill="x", padx=20, pady=(0, 14))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(ctrl_inner, text="Attendance Date:", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY).pack(side="left", padx=(0, 8))

        self.entry_date = ctk.CTkEntry(ctrl_inner, width=130, height=36, font=theme.FONT_BODY)
        self.entry_date.insert(0, str(date.today()))
        self.entry_date.pack(side="left", padx=(0, 10))

        btn_load = ctk.CTkButton(
            ctrl_inner,
            text="📅 Load Date",
            width=100,
            height=36,
            font=theme.FONT_BUTTON,
            fg_color=theme.PRIMARY,
            command=self.load_attendance
        )
        btn_load.pack(side="left", padx=(0, 16))

        # Quick Batch Actions
        btn_all_present = ctk.CTkButton(
            ctrl_inner,
            text="✓ Mark All Present",
            width=130,
            height=36,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            hover_color=theme.BG_ROW_HOVER,
            command=self._mark_all_present
        )
        btn_all_present.pack(side="left", padx=(0, 8))

        self.lbl_status = ctk.CTkLabel(ctrl_inner, text="", font=theme.FONT_SMALL, text_color=theme.SUCCESS)
        self.lbl_status.pack(side="right")

        # Table Container
        table_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Table Header
        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header_row.pack(fill="x", padx=12, pady=(12, 6))
        header_row.pack_propagate(False)

        cols = [
            ("Student Roll No", 140),
            ("Student Full Name", 240),
            ("Course", 160),
            ("Attendance Status Selector", 260)
        ]
        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=8)

        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_attendance()

    def _mark_all_present(self):
        for btn in self.student_selectors.values():
            btn.set("Present")
        self.lbl_status.configure(text="All marked as Present. Click 'Save Attendance' to persist.", text_color=theme.INFO)

    def load_attendance(self):
        self.lbl_status.configure(text="")
        for w in self.table_body.winfo_children():
            w.destroy()
        self.student_selectors.clear()

        date_str = self.entry_date.get().strip() or str(date.today())
        curr_date, roster = db_service.get_attendance_for_date(date_str)

        if not roster:
            ctk.CTkLabel(self.table_body, text="No students found to mark attendance.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=30)
            return

        for idx, item in enumerate(roster):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=item["student_code"], font=theme.FONT_BODY_BOLD, width=140, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=item["name"], font=theme.FONT_BODY, width=240, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=item["course"], font=theme.FONT_BODY, width=160, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

            # Segmented button for status
            seg = ctk.CTkSegmentedButton(
                row,
                values=["Present", "Absent", "Leave"],
                selected_color=theme.PRIMARY,
                selected_hover_color=theme.PRIMARY_HOVER,
                font=theme.FONT_SMALL,
                height=28
            )
            seg.set(item["status"])
            seg.pack(side="left", padx=8)

            self.student_selectors[item["student_id"]] = seg

    def _save_attendance(self):
        date_str = self.entry_date.get().strip()
        if not self.student_selectors:
            messagebox.showwarning("Empty", "No students loaded.", parent=self.winfo_toplevel())
            return

        status_dict = {s_id: seg.get() for s_id, seg in self.student_selectors.items()}
        ok, msg = db_service.save_bulk_attendance(date_str, status_dict)
        if ok:
            messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
            self.lbl_status.configure(text=f"✓ Saved for {date_str}", text_color=theme.SUCCESS)
        else:
            messagebox.showerror("Error", msg, parent=self.winfo_toplevel())
