"""
Fee Management View for HMS Desktop Application.
Supports role-based views:
- Admin: Full oversight, add fees, mark paid, inspect all students.
- Student: Read-only access to their own fees, payment receipts, and dues.
"""
from datetime import date, timedelta
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog, StatCard
from app import db_service

class FeesView(ctk.CTkFrame):
    def __init__(self, master, current_user=None):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user or {}
        self.is_admin = self.current_user.get("role") == "Admin"
        self.student_id = self.current_user.get("student_id")

        # Header
        if self.is_admin:
            self.header = PageHeader(
                self,
                title="Fee Management",
                subtitle="Track semester invoices, pending dues, and payment records",
                action_text="💰 + Add Fee",
                action_cmd=self._open_add_fee_dialog
            )
        else:
            self.header = PageHeader(
                self,
                title="My Fee Invoices",
                subtitle="View your semester fee invoices, payment receipts, and clearance status"
            )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Metrics Row
        self.metrics_row = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_row.pack(fill="x", padx=20, pady=(0, 14))
        for col in range(3):
            self.metrics_row.grid_columnconfigure(col, weight=1, uniform="fee_metric")

        title_invoiced = "Total Invoiced" if self.is_admin else "My Total Fees"
        title_collected = "Total Collected" if self.is_admin else "My Total Paid"
        title_pending = "Total Outstanding" if self.is_admin else "Pending Balance"

        self.card_total = StatCard(self.metrics_row, title_invoiced, "₹0", "📄", theme.PRIMARY)
        self.card_total.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_collected = StatCard(self.metrics_row, title_collected, "₹0", "✅", theme.SUCCESS)
        self.card_collected.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_pending = StatCard(self.metrics_row, title_pending, "₹0", "⏳", theme.WARNING)
        self.card_pending.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # Table Container
        table_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        table_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Filter bar
        filter_bar = ctk.CTkFrame(table_card, fg_color="transparent")
        filter_bar.pack(fill="x", padx=14, pady=(12, 6))

        self.seg_filter = ctk.CTkSegmentedButton(
            filter_bar,
            values=["All Fees", "Pending", "Paid"],
            command=lambda v: self.load_fees()
        )
        self.seg_filter.set("All Fees")
        self.seg_filter.pack(side="left")

        # Table Header
        header_row = ctk.CTkFrame(table_card, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header_row.pack(fill="x", padx=12, pady=(8, 6))
        header_row.pack_propagate(False)

        if self.is_admin:
            cols = [
                ("Student", 200),
                ("Amount", 120),
                ("Due Date", 120),
                ("Payment Date", 120),
                ("Status", 100),
                ("Action", 120)
            ]
        else:
            cols = [
                ("Fee Reference", 160),
                ("Amount", 130),
                ("Due Date", 130),
                ("Payment Date", 140),
                ("Status", 110),
                ("Clearance Status", 150)
            ]

        for name, width in cols:
            ctk.CTkLabel(header_row, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=8)

        self.table_body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_fees()

    def load_fees(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        filter_val = self.seg_filter.get()

        if self.is_admin:
            all_fees = db_service.get_all_fees(None)
        else:
            all_fees = db_service.get_student_fees(self.student_id) if self.student_id else []

        # Update metrics
        total_amt = sum(f["amount"] for f in all_fees)
        collected_amt = sum(f["amount"] for f in all_fees if f["status"] == "Paid")
        pending_amt = sum(f["amount"] for f in all_fees if f["status"] == "Pending")

        self.card_total.update_value(f"₹{total_amt:,.0f}")
        self.card_collected.update_value(f"₹{collected_amt:,.0f}")
        self.card_pending.update_value(f"₹{pending_amt:,.0f}")

        # Apply filter
        if filter_val == "Pending":
            fees = [f for f in all_fees if f["status"] == "Pending"]
        elif filter_val == "Paid":
            fees = [f for f in all_fees if f["status"] == "Paid"]
        else:
            fees = all_fees

        if not fees:
            empty_msg = "No fee records found." if self.is_admin else "No fee records found for your account."
            ctk.CTkLabel(self.table_body, text=empty_msg, font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=30)
            return

        for idx, f in enumerate(fees):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.table_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            if self.is_admin:
                ctk.CTkLabel(row, text=f"{f.get('student_name', '')} ({f.get('student_code', '')})", font=theme.FONT_BODY_BOLD, width=200, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f"₹{f['amount']:,.0f}", font=theme.FONT_BODY_BOLD, width=120, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f['due_date'], font=theme.FONT_BODY, width=120, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f['payment_date'], font=theme.FONT_BODY, width=120, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

                status_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
                status_frame.pack(side="left", padx=8)
                StatusBadge(status_frame, f['status']).pack(anchor="w")

                action_frame = ctk.CTkFrame(row, fg_color="transparent", width=120)
                action_frame.pack(side="left", padx=8)

                if f["status"] == "Pending":
                    btn_pay = ctk.CTkButton(
                        action_frame,
                        text="Mark Paid",
                        font=theme.FONT_SMALL,
                        width=95,
                        height=28,
                        fg_color=theme.SUCCESS,
                        hover_color=theme.SUCCESS_HOVER,
                        command=lambda fid=f["id"]: self._confirm_pay(fid)
                    )
                    btn_pay.pack(anchor="w")
                else:
                    ctk.CTkLabel(action_frame, text="Paid ✓", font=theme.FONT_BODY_BOLD, text_color=theme.SUCCESS).pack(anchor="w")
            else:
                # Student View: Read-only, no admin actions
                ctk.CTkLabel(row, text=f"FEE-INV-{f['id']:04d}", font=theme.FONT_BODY_BOLD, width=160, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f"₹{f['amount']:,.0f}", font=theme.FONT_BODY_BOLD, width=130, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f['due_date'], font=theme.FONT_BODY, width=130, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
                ctk.CTkLabel(row, text=f['payment_date'], font=theme.FONT_BODY, width=140, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

                status_frame = ctk.CTkFrame(row, fg_color="transparent", width=110)
                status_frame.pack(side="left", padx=8)
                StatusBadge(status_frame, f['status']).pack(anchor="w")

                clearance_text = "Receipt Cleared ✓" if f["status"] == "Paid" else "Payment Pending (Contact Warden)"
                clearance_color = theme.SUCCESS if f["status"] == "Paid" else theme.WARNING
                ctk.CTkLabel(row, text=clearance_text, font=theme.FONT_SMALL, text_color=clearance_color, width=150, anchor="w").pack(side="left", padx=8)

    def _confirm_pay(self, fee_id):
        if not self.is_admin:
            messagebox.showerror("Permission Denied", "Students cannot mark fee payments.", parent=self.winfo_toplevel())
            return

        confirm = messagebox.askyesno(
            "Confirm Payment",
            "Mark this fee record as Paid with today's date?",
            parent=self.winfo_toplevel()
        )
        if confirm:
            ok, msg = db_service.mark_fee_paid(fee_id)
            if ok:
                messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
                self.load_fees()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_add_fee_dialog(self):
        if not self.is_admin:
            messagebox.showerror("Permission Denied", "Only administrators can issue new fee invoices.", parent=self.winfo_toplevel())
            return

        students = db_service.get_all_students()
        if not students:
            messagebox.showwarning("No Students", "Please register students first.", parent=self.winfo_toplevel())
            return

        dlg = ModalDialog(self.winfo_toplevel(), title="Add Fee Invoice", width=460, height=440)

        student_displays = [f"{s['student_id_str']} - {s['name']}" for s in students]
        e_student = ctk.CTkOptionMenu(dlg.body, values=student_displays)
        dlg.add_field("Select Student *", e_student)

        e_amt = dlg.add_field("Fee Amount (₹) *", ctk.CTkEntry(dlg.body, placeholder_text="15000"))
        e_amt.insert(0, "15000")

        default_due = str(date.today() + timedelta(days=15))
        e_due = dlg.add_field("Due Date (YYYY-MM-DD) *", ctk.CTkEntry(dlg.body, placeholder_text=default_due))
        e_due.insert(0, default_due)

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            chosen_stu = e_student.get()
            amt_str = e_amt.get().strip()
            due_str = e_due.get().strip()

            stu_code = chosen_stu.split(" - ")[0]
            stu_obj = next((s for s in students if s["student_id_str"] == stu_code), None)

            if not stu_obj or not amt_str:
                lbl_msg.configure(text="Please fill in all fee details.")
                return

            try:
                amt = float(amt_str)
            except ValueError:
                lbl_msg.configure(text="Amount must be a valid number.")
                return

            ok, res = db_service.add_fee(stu_obj["id"], amt, due_str)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_fees()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Save Invoice", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
