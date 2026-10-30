"""
Leave Requests Management View for HMS Desktop Application.
"""
from datetime import date, timedelta
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog
from app import db_service

class LeavesView(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        is_admin = current_user["role"] == "Admin"

        action_text = "📝 + Apply for Leave" if not is_admin else None
        action_cmd = self._open_apply_leave_dialog if not is_admin else None

        # Header
        self.header = PageHeader(
            self,
            title="Leave Requests",
            subtitle="Hostel leave passes, gate exit permissions, and approval records",
            action_text=action_text,
            action_cmd=action_cmd,
            action_color=theme.PRIMARY
        )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Filter bar
        filter_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        filter_card.pack(fill="x", padx=20, pady=(0, 14))

        filter_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_inner.pack(fill="x", padx=16, pady=12)

        self.seg_filter = ctk.CTkSegmentedButton(
            filter_inner,
            values=["All Requests", "Pending", "Approved", "Rejected"],
            command=lambda v: self.load_leaves()
        )
        self.seg_filter.set("All Requests")
        self.seg_filter.pack(side="left")

        btn_refresh = ctk.CTkButton(
            filter_inner,
            text="🔄 Refresh",
            width=80,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=self.load_leaves
        )
        btn_refresh.pack(side="left", padx=10)

        # Table Container
        table_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Table Header
        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header_row.pack(fill="x", padx=12, pady=(12, 6))
        header_row.pack_propagate(False)

        cols = [
            ("Student", 180),
            ("Start Date", 100),
            ("End Date", 100),
            ("Reason", 260),
            ("Status", 100),
            ("Actions", 160)
        ]
        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=8)

        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_leaves()

    def load_leaves(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        if self.current_user["role"] == "Admin":
            leaves = db_service.get_all_leaves()
        else:
            leaves = db_service.get_student_leaves(self.current_user["student_id"])

        filter_val = self.seg_filter.get()
        if filter_val == "Pending":
            leaves = [l for l in leaves if l["status"] == "Pending"]
        elif filter_val == "Approved":
            leaves = [l for l in leaves if l["status"] == "Approved"]
        elif filter_val == "Rejected":
            leaves = [l for l in leaves if l["status"] == "Rejected"]

        if not leaves:
            ctk.CTkLabel(self.table_body, text="No leave requests found.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=40)
            return

        for idx, l in enumerate(leaves):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            stu_text = f"{l.get('student_name', 'Student')} ({l.get('student_code', '')})" if 'student_name' in l else "My Request"
            ctk.CTkLabel(row, text=stu_text, font=theme.FONT_BODY_BOLD, width=180, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=l['start_date'], font=theme.FONT_BODY, width=100, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=l['end_date'], font=theme.FONT_BODY, width=100, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=l['reason'], font=theme.FONT_BODY, width=260, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

            status_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
            status_frame.pack(side="left", padx=8)
            StatusBadge(status_frame, l['status']).pack(anchor="w")

            action_frame = ctk.CTkFrame(row, fg_color="transparent", width=160)
            action_frame.pack(side="left", padx=8)

            if self.current_user["role"] == "Admin" and l["status"] == "Pending":
                btn_appr = ctk.CTkButton(
                    action_frame,
                    text="Approve",
                    font=theme.FONT_SMALL,
                    width=68,
                    height=28,
                    fg_color=theme.SUCCESS,
                    hover_color=theme.SUCCESS_HOVER,
                    command=lambda lid=l["id"]: self._update_status(lid, "Approved")
                )
                btn_appr.pack(side="left", padx=(0, 6))

                btn_rej = ctk.CTkButton(
                    action_frame,
                    text="Reject",
                    font=theme.FONT_SMALL,
                    width=68,
                    height=28,
                    fg_color=theme.DANGER,
                    hover_color=theme.DANGER_HOVER,
                    command=lambda lid=l["id"]: self._update_status(lid, "Rejected")
                )
                btn_rej.pack(side="left")
            else:
                ctk.CTkLabel(action_frame, text="Processed", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED).pack(anchor="w")

    def _update_status(self, leave_id, status):
        ok, msg = db_service.update_leave_status(leave_id, status)
        if ok:
            messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
            self.load_leaves()
        else:
            messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_apply_leave_dialog(self):
        dlg = ModalDialog(self.winfo_toplevel(), title="Apply for Leave", width=460, height=480)

        today_str = str(date.today())
        next_day_str = str(date.today() + timedelta(days=2))

        e_start = dlg.add_field("Start Date (YYYY-MM-DD) *", ctk.CTkEntry(dlg.body, placeholder_text=today_str))
        e_start.insert(0, today_str)

        e_end = dlg.add_field("End Date (YYYY-MM-DD) *", ctk.CTkEntry(dlg.body, placeholder_text=next_day_str))
        e_end.insert(0, next_day_str)

        lbl = ctk.CTkLabel(dlg.body, text="Reason for Leave *", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY, anchor="w")
        lbl.pack(fill="x", pady=(8, 4))
        e_reason = ctk.CTkTextbox(dlg.body, height=100, font=theme.FONT_BODY)
        e_reason.pack(fill="x", pady=(0, 6))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            s_date = e_start.get().strip()
            e_date = e_end.get().strip()
            reason = e_reason.get("1.0", "end").strip()

            if not (s_date and e_date and reason):
                lbl_msg.configure(text="Please fill in all leave request fields.")
                return

            ok, res = db_service.add_leave_request(self.current_user["student_id"], s_date, e_date, reason)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_leaves()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Submit Request", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
