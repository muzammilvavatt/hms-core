"""
Main Application Window for Hostel Management System (HMS).
Built 100% in Python using CustomTkinter.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import ModalDialog
from app.gui.views.login_view import LoginView
from app.gui.views.admin_dashboard_view import AdminDashboardView
from app.gui.views.student_dashboard_view import StudentDashboardView
from app.gui.views.students_view import StudentsView
from app.gui.views.hostels_rooms_view import HostelsRoomsView
from app.gui.views.allocations_view import AllocationsView
from app.gui.views.fees_view import FeesView
from app.gui.views.attendance_view import AttendanceView
from app.gui.views.complaints_view import ComplaintsView
from app.gui.views.notices_view import NoticesView
from app.gui.views.visitors_view import VisitorsView
from app.gui.views.leaves_view import LeavesView
from app import db_service

class HMSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance & Themes
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Window settings
        self.title("Hostel Management System (HMS Nexus)")
        self.geometry("1260x780")
        self.minsize(1050, 680)

        # Center on screen
        self._center_window(1260, 780)

        self.current_user = None
        self.active_nav_btn = None
        self.nav_buttons = {}

        # Show Login Screen first
        self.show_login()

    def _center_window(self, width, height):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(20, (sw - width) // 2)
        y = max(20, (sh - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_login(self):
        """Displays the Login Screen."""
        for w in self.winfo_children():
            w.destroy()

        self.login_view = LoginView(self, on_login_success=self._on_login_success)
        self.login_view.pack(fill="both", expand=True)

    def _on_login_success(self, user_info):
        """Called when user successfully logs in."""
        self.current_user = user_info
        self._build_main_shell()

    def _build_main_shell(self):
        """Constructs the sidebar navigation and content view area."""
        for w in self.winfo_children():
            w.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=theme.BG_SIDEBAR,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # App Brand Header in Sidebar
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 16))

        logo_badge = ctk.CTkFrame(brand_frame, width=38, height=38, corner_radius=10, fg_color=theme.PRIMARY)
        logo_badge.pack(side="left", padx=(0, 10))
        logo_badge.pack_propagate(False)

        logo_lbl = ctk.CTkLabel(logo_badge, text="🏢", font=("Segoe UI Emoji", 18), text_color="#FFFFFF")
        logo_lbl.place(relx=0.5, rely=0.5, anchor="center")

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left", fill="both")

        ctk.CTkLabel(title_box, text="HMS Nexus", font=theme.FONT_APP_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        role_desc = "Administrator" if self.current_user["role"] == "Admin" else "Student Portal"
        ctk.CTkLabel(title_box, text=role_desc, font=theme.FONT_SMALL, text_color=theme.PRIMARY).pack(anchor="w")

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=theme.BORDER_COLOR).pack(fill="x", padx=16, pady=(0, 12))

        # Navigation Menu List
        self.menu_container = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.menu_container.pack(fill="both", expand=True, padx=12, pady=0)

        self._build_nav_items()

        # Sidebar Footer: User Card + Theme Toggle + Logout
        self._build_sidebar_footer()

        # Right Main Content Container
        self.content_container = ctk.CTkFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Default Landing View
        default_view = "admin_dashboard" if self.current_user["role"] == "Admin" else "student_dashboard"
        self.navigate_to(default_view)

    def _build_nav_items(self):
        self.nav_buttons.clear()
        is_admin = self.current_user["role"] == "Admin"

        if is_admin:
            items = [
                ("admin_dashboard", "📊 Dashboard"),
                ("students", "🎓 Students"),
                ("hostels_rooms", "🏢 Hostels & Rooms"),
                ("allocations", "🛏️ Allocations"),
                ("fees", "💰 Fee Invoices"),
                ("attendance", "📅 Attendance"),
                ("complaints", "⚠️ Complaints"),
                ("notices", "📢 Notice Board"),
                ("visitors", "🚪 Visitors Log"),
                ("leaves", "📝 Leave Requests"),
            ]
        else:
            items = [
                ("student_dashboard", "📊 My Dashboard"),
                ("fees", "💰 My Fees"),
                ("complaints", "⚠️ Complaints"),
                ("notices", "📢 Notice Board"),
                ("leaves", "📝 Leave Requests"),
            ]

        for view_key, label in items:
            btn = ctk.CTkButton(
                self.menu_container,
                text=f"  {label}",
                font=theme.FONT_BODY_BOLD,
                anchor="w",
                height=40,
                corner_radius=theme.RADIUS_BUTTON,
                fg_color="transparent",
                text_color=theme.TEXT_PRIMARY,
                hover_color=theme.BG_ROW_HOVER,
                command=lambda k=view_key: self.navigate_to(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[view_key] = btn

    def _build_sidebar_footer(self):
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(8, 16))

        # Divider
        ctk.CTkFrame(footer, height=1, fg_color=theme.BORDER_COLOR).pack(fill="x", pady=(0, 10))

        # User Profile Badge
        user_badge = ctk.CTkFrame(footer, fg_color=theme.BG_CARD_ALT, corner_radius=8)
        user_badge.pack(fill="x", pady=(0, 10))

        u_inner = ctk.CTkFrame(user_badge, fg_color="transparent")
        u_inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(u_inner, text="👤", font=("Segoe UI Emoji", 16)).pack(side="left", padx=(0, 6))

        user_info_box = ctk.CTkFrame(u_inner, fg_color="transparent")
        user_info_box.pack(side="left", fill="both")

        name_display = self.current_user["student_name"] or self.current_user["username"]
        ctk.CTkLabel(user_info_box, text=name_display, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(user_info_box, text=self.current_user["role"], font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w").pack(anchor="w")

        # Theme Selector Row
        theme_row = ctk.CTkFrame(footer, fg_color="transparent")
        theme_row.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(theme_row, text="Theme:", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(side="left")

        self.opt_theme = ctk.CTkOptionMenu(
            theme_row,
            values=["Dark", "Light"],
            width=90,
            height=28,
            font=theme.FONT_SMALL,
            command=self._change_theme
        )
        self.opt_theme.set(ctk.get_appearance_mode())
        self.opt_theme.pack(side="right")

        # Change Password Button
        btn_pw = ctk.CTkButton(
            footer,
            text="🔒 Change Password",
            font=theme.FONT_SMALL,
            height=30,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            hover_color=theme.BG_ROW_HOVER,
            command=self._open_change_password_dialog
        )
        btn_pw.pack(fill="x", pady=(0, 6))

        # Logout Button
        btn_logout = ctk.CTkButton(
            footer,
            text="🚪 Logout",
            font=theme.FONT_SMALL,
            height=30,
            fg_color=theme.DANGER,
            hover_color=theme.DANGER_HOVER,
            command=self._logout
        )
        btn_logout.pack(fill="x")

    def _change_theme(self, mode):
        ctk.set_appearance_mode(mode)

    def navigate_to(self, view_key):
        """Swaps the current view in the content area."""
        # Update nav button highlights
        for key, btn in self.nav_buttons.items():
            if key == view_key:
                btn.configure(fg_color=theme.PRIMARY, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=theme.TEXT_PRIMARY)

        # Clear existing view
        for w in self.content_container.winfo_children():
            w.destroy()

        # Instantiate requested view
        if view_key == "admin_dashboard":
            view = AdminDashboardView(self.content_container, navigate_to=self.navigate_to)
        elif view_key == "student_dashboard":
            view = StudentDashboardView(self.content_container, current_user=self.current_user, navigate_to=self.navigate_to)
        elif view_key == "students":
            view = StudentsView(self.content_container)
        elif view_key == "hostels_rooms":
            view = HostelsRoomsView(self.content_container)
        elif view_key == "allocations":
            view = AllocationsView(self.content_container)
        elif view_key == "fees":
            view = FeesView(self.content_container)
        elif view_key == "attendance":
            view = AttendanceView(self.content_container)
        elif view_key == "complaints":
            view = ComplaintsView(self.content_container, current_user=self.current_user)
        elif view_key == "notices":
            view = NoticesView(self.content_container, current_user=self.current_user)
        elif view_key == "visitors":
            view = VisitorsView(self.content_container)
        elif view_key == "leaves":
            view = LeavesView(self.content_container, current_user=self.current_user)
        else:
            view = ctk.CTkLabel(self.content_container, text=f"View '{view_key}' not found.")

        view.grid(row=0, column=0, sticky="nsew")

    def _open_change_password_dialog(self):
        dlg = ModalDialog(self, title="Change Account Password", width=420, height=400)

        e_old = dlg.add_field("Current Password *", ctk.CTkEntry(dlg.body, show="•"))
        e_new = dlg.add_field("New Password *", ctk.CTkEntry(dlg.body, show="•"))
        e_confirm = dlg.add_field("Confirm New Password *", ctk.CTkEntry(dlg.body, show="•"))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            old_p = e_old.get().strip()
            new_p = e_new.get().strip()
            conf_p = e_confirm.get().strip()

            if not (old_p and new_p and conf_p):
                lbl_msg.configure(text="Please fill in all password fields.")
                return

            if new_p != conf_p:
                lbl_msg.configure(text="New passwords do not match.")
                return

            ok, res = db_service.change_user_password(self.current_user["id"], old_p, new_p)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Update Password", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")

    def _logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?", parent=self)
        if confirm:
            self.current_user = None
            self.show_login()
