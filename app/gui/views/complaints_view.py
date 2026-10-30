"""
Complaints Management View for HMS Desktop Application.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog
from app import db_service

class ComplaintsView(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        is_admin = current_user["role"] == "Admin"

        # Header
        action_text = None
        action_cmd = None
        if not is_admin:
            action_text = "⚠️ + Raise Complaint"
            action_cmd = self._open_add_complaint_dialog

        self.header = PageHeader(
            self,
            title="Complaints & Maintenance Tickets",
            subtitle="Review facility issues, priority levels, and resolution status",
            action_text=action_text,
            action_cmd=action_cmd,
            action_color=theme.DANGER
        )
        self.header.pack(fill="x", padx=20, pady=(16, 12))

        # Filter bar
        filter_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        filter_card.pack(fill="x", padx=20, pady=(0, 14))

        filter_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_inner.pack(fill="x", padx=16, pady=12)

        self.seg_filter = ctk.CTkSegmentedButton(
            filter_inner,
            values=["All Tickets", "Pending", "Resolved"],
            command=lambda v: self.load_complaints()
        )
        self.seg_filter.set("All Tickets")
        self.seg_filter.pack(side="left")

        btn_refresh = ctk.CTkButton(
            filter_inner,
            text="🔄 Refresh",
            width=80,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=self.load_complaints
        )
        btn_refresh.pack(side="left", padx=10)

        # Tickets Body
        self.tickets_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.tickets_body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.load_complaints()

    def load_complaints(self):
        for w in self.tickets_body.winfo_children():
            w.destroy()

        if self.current_user["role"] == "Admin":
            complaints = db_service.get_all_complaints()
        else:
            complaints = db_service.get_student_complaints(self.current_user["student_id"])

        filter_val = self.seg_filter.get()
        if filter_val == "Pending":
            complaints = [c for c in complaints if c["status"] == "Pending"]
        elif filter_val == "Resolved":
            complaints = [c for c in complaints if c["status"] == "Resolved"]

        if not complaints:
            empty = ctk.CTkLabel(
                self.tickets_body,
                text="No complaints matching selected filter.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED
            )
            empty.pack(pady=40)
            return

        for c in complaints:
            card = ctk.CTkFrame(
                self.tickets_body,
                fg_color=theme.BG_CARD,
                corner_radius=theme.RADIUS_CARD,
                border_width=1,
                border_color=theme.BORDER_COLOR
            )
            card.pack(fill="x", pady=6)

            # Top row: Student/Category + Badges + Date
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=(14, 6))

            student_tag = f"{c.get('student_name', 'Student')} ({c.get('student_code', '')}) - " if 'student_name' in c else ""
            ctk.CTkLabel(
                top,
                text=f"🔧 {student_tag}{c['category']}",
                font=theme.FONT_SECTION_TITLE,
                text_color=theme.TEXT_PRIMARY
            ).pack(side="left")

            StatusBadge(top, c['status']).pack(side="right")
            StatusBadge(top, c['priority']).pack(side="right", padx=6)

            # Description
            desc_box = ctk.CTkFrame(card, fg_color=theme.BG_CARD_ALT, corner_radius=8)
            desc_box.pack(fill="x", padx=18, pady=4)

            ctk.CTkLabel(
                desc_box,
                text=c['description'],
                font=theme.FONT_BODY,
                text_color=theme.TEXT_PRIMARY,
                wraplength=800,
                justify="left"
            ).pack(anchor="w", padx=14, pady=10)

            # Bottom row: Date + Resolve Action
            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=18, pady=(6, 14))

            ctk.CTkLabel(
                bottom,
                text=f"Reported on: {c['date']}",
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY
            ).pack(side="left")

            if self.current_user["role"] == "Admin" and c["status"] == "Pending":
                btn_resolve = ctk.CTkButton(
                    bottom,
                    text="✓ Mark Resolved",
                    font=theme.FONT_SMALL,
                    width=110,
                    height=28,
                    fg_color=theme.SUCCESS,
                    hover_color=theme.SUCCESS_HOVER,
                    command=lambda cid=c["id"]: self._confirm_resolve(cid)
                )
                btn_resolve.pack(side="right")

    def _confirm_resolve(self, complaint_id):
        confirm = messagebox.askyesno(
            "Confirm Resolution",
            "Mark this maintenance complaint as Resolved?",
            parent=self.winfo_toplevel()
        )
        if confirm:
            ok, msg = db_service.resolve_complaint(complaint_id)
            if ok:
                messagebox.showinfo("Success", msg, parent=self.winfo_toplevel())
                self.load_complaints()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())

    def _open_add_complaint_dialog(self):
        dlg = ModalDialog(self.winfo_toplevel(), title="Raise Maintenance Complaint", width=480, height=480)

        e_cat = ctk.CTkOptionMenu(dlg.body, values=["Electrical", "Plumbing", "Furniture", "Cleaning", "Mess / Food", "Wi-Fi / Internet", "Other"])
        dlg.add_field("Issue Category *", e_cat)

        e_pri = ctk.CTkOptionMenu(dlg.body, values=["Normal", "High", "Low"])
        dlg.add_field("Priority Level *", e_pri)

        lbl = ctk.CTkLabel(dlg.body, text="Description of the Issue *", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY, anchor="w")
        lbl.pack(fill="x", pady=(8, 4))

        e_desc = ctk.CTkTextbox(dlg.body, height=100, font=theme.FONT_BODY)
        e_desc.pack(fill="x", pady=(0, 6))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            cat = e_cat.get()
            pri = e_pri.get()
            desc = e_desc.get("1.0", "end").strip()

            if not desc:
                lbl_msg.configure(text="Please describe the problem.")
                return

            ok, res = db_service.add_complaint(self.current_user["student_id"], cat, desc, pri)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_complaints()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Submit Complaint", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
