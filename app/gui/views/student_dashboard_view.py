"""
Student Personal Dashboard View for HMS Desktop Application.
"""
import customtkinter as ctk
from app.gui import theme
from app.gui.components import PageHeader, StatCard, StatusBadge
from app import db_service

class StudentDashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, current_user, navigate_to):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.navigate_to = navigate_to
        self.student_id = current_user["student_id"]

        # Header
        self.header = PageHeader(
            self,
            title=f"Welcome, {current_user.get('student_name', 'Student')}!",
            subtitle=f"Student Portal  •  ID: {current_user['username']}",
            action_text="🔄 Refresh",
            action_cmd=self.refresh,
            action_color=theme.SECONDARY
        )
        self.header.pack(fill="x", padx=20, pady=(16, 16))

        # Stat cards row
        self.stats_row = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_row.pack(fill="x", padx=20, pady=(0, 16))
        for col in range(4):
            self.stats_row.grid_columnconfigure(col, weight=1, uniform="stu_stat")

        self.card_bed = StatCard(self.stats_row, "Assigned Bed", "-", "🛏️", theme.PRIMARY)
        self.card_bed.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_attendance = StatCard(self.stats_row, "Attendance Rate", "100%", "📅", theme.SUCCESS)
        self.card_attendance.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_fees = StatCard(self.stats_row, "Pending Fees", "₹0", "💰", theme.WARNING)
        self.card_fees.grid(row=0, column=2, padx=4, sticky="ew")

        self.card_requests = StatCard(self.stats_row, "Active Tickets", "0", "📋", theme.INFO)
        self.card_requests.grid(row=0, column=3, padx=(8, 0), sticky="ew")

        # Two-column container: Room Info Card + Quick Actions
        mid_row = ctk.CTkFrame(self, fg_color="transparent")
        mid_row.pack(fill="x", padx=20, pady=(0, 18))
        mid_row.grid_columnconfigure(0, weight=3)
        mid_row.grid_columnconfigure(1, weight=2)

        # Accommodation Details Card
        self.alloc_card = ctk.CTkFrame(mid_row, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        self.alloc_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(self.alloc_card, text="🏢 My Hostel Accommodation", font=theme.FONT_SECTION_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 10))

        self.alloc_details_frame = ctk.CTkFrame(self.alloc_card, fg_color=theme.BG_CARD_ALT, corner_radius=10)
        self.alloc_details_frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        # Quick Actions Card
        qa_card = ctk.CTkFrame(mid_row, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        qa_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(qa_card, text="⚡ Quick Actions", font=theme.FONT_SECTION_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 12))

        btn_qa_frame = ctk.CTkFrame(qa_card, fg_color="transparent")
        btn_qa_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        ctk.CTkButton(
            btn_qa_frame,
            text="📝 Apply for Leave",
            font=theme.FONT_BODY_BOLD,
            height=38,
            fg_color=theme.PRIMARY,
            command=lambda: self.navigate_to("leaves")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            btn_qa_frame,
            text="⚠️ Report Issue / Complaint",
            font=theme.FONT_BODY_BOLD,
            height=38,
            fg_color=theme.DANGER,
            command=lambda: self.navigate_to("complaints")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            btn_qa_frame,
            text="💰 View My Fee Invoices",
            font=theme.FONT_BODY_BOLD,
            height=38,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            hover_color=theme.BG_ROW_HOVER,
            command=lambda: self.navigate_to("fees")
        ).pack(fill="x", pady=4)

        # Bottom Section: Notice Board
        notices_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.RADIUS_CARD, border_width=1, border_color=theme.BORDER_COLOR)
        notices_card.pack(fill="x", padx=20, pady=(0, 24))

        ctk.CTkLabel(notices_card, text="📢 Campus & Hostel Announcements", font=theme.FONT_SECTION_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 10))

        self.notices_frame = ctk.CTkFrame(notices_card, fg_color="transparent")
        self.notices_frame.pack(fill="x", padx=20, pady=(0, 18))

        self.refresh()

    def refresh(self):
        data = db_service.get_student_dashboard_stats(self.student_id)
        if not data:
            return

        self.card_bed.update_value(data["bed"])
        self.card_attendance.update_value(f"{data['attendance_percentage']}%")
        self.card_fees.update_value(f"₹{data['pending_fee_amount']:,.0f}")
        self.card_requests.update_value(data["complaint_count"] + data["leave_count"])

        # Populate allocation card
        for w in self.alloc_details_frame.winfo_children():
            w.destroy()

        if data["has_allocation"]:
            rows = [
                ("Hostel Block:", data["hostel"]),
                ("Room Number:", data["room"]),
                ("Assigned Bed:", data["bed"]),
                ("Course & Year:", f"{data['course']} (Year {data['year']})"),
                ("Allocation Status:", "Active & Occupied")
            ]
            for label, val in rows:
                r = ctk.CTkFrame(self.alloc_details_frame, fg_color="transparent")
                r.pack(fill="x", padx=16, pady=5)
                ctk.CTkLabel(r, text=label, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=140, anchor="w").pack(side="left")
                ctk.CTkLabel(r, text=val, font=theme.FONT_BODY_BOLD if label == "Assigned Bed:" else theme.FONT_BODY, text_color=theme.TEXT_PRIMARY, anchor="w").pack(side="left")
        else:
            ctk.CTkLabel(
                self.alloc_details_frame,
                text="⚠️ You do not currently have an assigned hostel room.\nPlease contact the hostel warden or administrator.",
                font=theme.FONT_BODY,
                text_color=theme.WARNING,
                justify="left"
            ).pack(padx=20, pady=24)

        # Populate notices
        for w in self.notices_frame.winfo_children():
            w.destroy()

        notices = data["notices"]
        if not notices:
            ctk.CTkLabel(self.notices_frame, text="No announcements posted yet.", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED).pack(anchor="w", pady=10)
        else:
            for n in notices[:3]:
                box = ctk.CTkFrame(self.notices_frame, fg_color=theme.BG_CARD_ALT, corner_radius=8)
                box.pack(fill="x", pady=4)

                top = ctk.CTkFrame(box, fg_color="transparent")
                top.pack(fill="x", padx=14, pady=(10, 4))
                ctk.CTkLabel(top, text=n['title'], font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY).pack(side="left")
                StatusBadge(top, n['category']).pack(side="right")

                ctk.CTkLabel(box, text=n['description'], font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, wraplength=780, justify="left").pack(anchor="w", padx=14, pady=(0, 6))
                ctk.CTkLabel(box, text=f"Published: {n['date']}", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED).pack(anchor="w", padx=14, pady=(0, 10))
