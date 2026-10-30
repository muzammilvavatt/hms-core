"""
Admin Dashboard View for HMS Desktop Application.
"""
import customtkinter as ctk
from app.gui import theme
from app.gui.components import PageHeader, StatCard
from app import db_service

class AdminDashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_to):
        super().__init__(master, fg_color="transparent")
        self.navigate_to = navigate_to

        # Header
        self.header = PageHeader(
            self,
            title="Admin Dashboard",
            subtitle="Overview of hostel occupancy, students, and active operations",
            action_text="🔄 Refresh",
            action_cmd=self.refresh,
            action_color=theme.SECONDARY
        )
        self.header.pack(fill="x", padx=20, pady=(16, 20))

        # Stats Grid 1: Students & Accommodations
        self.stats_frame_1 = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame_1.pack(fill="x", padx=20, pady=(0, 14))
        for col in range(4):
            self.stats_frame_1.grid_columnconfigure(col, weight=1, uniform="stat_col")

        self.card_students = StatCard(self.stats_frame_1, "Total Students", "0", "🎓", theme.PRIMARY)
        self.card_students.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_rooms = StatCard(self.stats_frame_1, "Total Rooms", "0", "🏢", theme.INFO)
        self.card_rooms.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_available_beds = StatCard(self.stats_frame_1, "Available Beds", "0", "🛏️", theme.SUCCESS)
        self.card_available_beds.grid(row=0, column=2, padx=4, sticky="ew")

        self.card_occupied_beds = StatCard(self.stats_frame_1, "Occupied Beds", "0", "🔒", theme.WARNING)
        self.card_occupied_beds.grid(row=0, column=3, padx=(8, 0), sticky="ew")

        # Stats Grid 2: Operations & Alerts
        self.stats_frame_2 = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame_2.pack(fill="x", padx=20, pady=(0, 20))
        for col in range(3):
            self.stats_frame_2.grid_columnconfigure(col, weight=1, uniform="stat_col_2")

        self.card_complaints = StatCard(self.stats_frame_2, "Pending Complaints", "0", "⚠️", theme.DANGER)
        self.card_complaints.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_fees = StatCard(self.stats_frame_2, "Pending Fee Invoices", "0", "💰", theme.WARNING)
        self.card_fees.grid(row=0, column=1, padx=4, sticky="ew")

        self.card_leaves = StatCard(self.stats_frame_2, "Pending Leaves", "0", "📝", theme.INFO)
        self.card_leaves.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # Quick Actions Bar
        self._build_quick_actions()

        # Two-Column Info Section: Occupancy Meter + Recent Notices
        self.info_container = ctk.CTkFrame(self, fg_color="transparent")
        self.info_container.pack(fill="x", padx=20, pady=(0, 24))
        self.info_container.grid_columnconfigure(0, weight=1)
        self.info_container.grid_columnconfigure(1, weight=1)

        self._build_occupancy_card()
        self._build_notices_card()

        # Load real data
        self.refresh()

    def _build_quick_actions(self):
        qa_frame = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_CARD,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        qa_frame.pack(fill="x", padx=20, pady=(0, 20))

        lbl = ctk.CTkLabel(
            qa_frame,
            text="⚡ Quick Actions",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        )
        lbl.pack(anchor="w", padx=20, pady=(16, 12))

        btn_row = ctk.CTkFrame(qa_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        actions = [
            ("➕ Register Student", lambda: self.navigate_to("students")),
            ("🛏️ Allocate Bed", lambda: self.navigate_to("allocations")),
            ("📅 Mark Attendance", lambda: self.navigate_to("attendance")),
            ("📢 Publish Notice", lambda: self.navigate_to("notices")),
            ("⚠️ View Complaints", lambda: self.navigate_to("complaints")),
        ]

        for text, cmd in actions:
            btn = ctk.CTkButton(
                btn_row,
                text=text,
                command=cmd,
                font=theme.FONT_BODY_BOLD,
                height=36,
                corner_radius=theme.RADIUS_BUTTON,
                fg_color=theme.BG_CARD_ALT,
                text_color=theme.TEXT_PRIMARY,
                hover_color=theme.BG_ROW_HOVER
            )
            btn.pack(side="left", padx=(0, 10))

    def _build_occupancy_card(self):
        self.occ_card = ctk.CTkFrame(
            self.info_container,
            corner_radius=theme.RADIUS_CARD,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        self.occ_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl = ctk.CTkLabel(
            self.occ_card,
            text="📊 Bed Occupancy Rate",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        )
        lbl.pack(anchor="w", padx=20, pady=(16, 10))

        self.occ_percent_lbl = ctk.CTkLabel(
            self.occ_card,
            text="0%",
            font=("Segoe UI", 32, "bold"),
            text_color=theme.PRIMARY
        )
        self.occ_percent_lbl.pack(anchor="w", padx=20, pady=(0, 6))

        self.progress_bar = ctk.CTkProgressBar(
            self.occ_card,
            height=12,
            corner_radius=6,
            progress_color=theme.PRIMARY
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 14))
        self.progress_bar.set(0)

        self.occ_subtext = ctk.CTkLabel(
            self.occ_card,
            text="0 of 0 beds occupied",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY
        )
        self.occ_subtext.pack(anchor="w", padx=20, pady=(0, 18))

    def _build_notices_card(self):
        self.notices_card = ctk.CTkFrame(
            self.info_container,
            corner_radius=theme.RADIUS_CARD,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        self.notices_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        lbl = ctk.CTkLabel(
            self.notices_card,
            text="📢 Recent Announcements",
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        )
        lbl.pack(anchor="w", padx=20, pady=(16, 10))

        self.notices_list_frame = ctk.CTkFrame(self.notices_card, fg_color="transparent")
        self.notices_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def refresh(self):
        stats = db_service.get_admin_dashboard_stats()

        self.card_students.update_value(stats["total_students"])
        self.card_rooms.update_value(stats["total_rooms"])
        self.card_available_beds.update_value(stats["available_beds"])
        self.card_occupied_beds.update_value(stats["occupied_beds"])
        self.card_complaints.update_value(stats["pending_complaints"])
        self.card_fees.update_value(stats["pending_fees"])
        self.card_leaves.update_value(stats["pending_leaves"])

        # Occupancy calculation
        total_beds = stats["total_beds"]
        occupied_beds = stats["occupied_beds"]
        rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0
        self.occ_percent_lbl.configure(text=f"{rate}%")
        self.progress_bar.set(rate / 100 if total_beds > 0 else 0)
        self.occ_subtext.configure(text=f"{occupied_beds} of {total_beds} beds currently occupied")

        # Notices list
        for widget in self.notices_list_frame.winfo_children():
            widget.destroy()

        notices = stats["recent_notices"]
        if not notices:
            empty = ctk.CTkLabel(
                self.notices_list_frame,
                text="No recent announcements.",
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_MUTED
            )
            empty.pack(anchor="w", pady=10)
        else:
            for n in notices[:4]:
                row = ctk.CTkFrame(self.notices_list_frame, fg_color=theme.BG_CARD_ALT, corner_radius=8)
                row.pack(fill="x", pady=4)

                title_lbl = ctk.CTkLabel(
                    row,
                    text=n["title"],
                    font=theme.FONT_BODY_BOLD,
                    text_color=theme.TEXT_PRIMARY,
                    anchor="w"
                )
                title_lbl.pack(side="left", padx=12, pady=8)

                date_lbl = ctk.CTkLabel(
                    row,
                    text=n["date"],
                    font=theme.FONT_SMALL,
                    text_color=theme.TEXT_SECONDARY
                )
                date_lbl.pack(side="right", padx=12, pady=8)
