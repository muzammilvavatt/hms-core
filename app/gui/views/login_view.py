"""
Modern Login View for HMS Desktop Application.
"""
import customtkinter as ctk
from app.gui import theme
from app import db_service

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=theme.BG_MAIN)
        self.on_login_success = on_login_success
        self.show_password = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Centered container card
        card = ctk.CTkFrame(
            self,
            width=420,
            corner_radius=16,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR
        )
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(True)

        # Icon and Header
        icon_badge = ctk.CTkFrame(
            card,
            width=64,
            height=64,
            corner_radius=16,
            fg_color=theme.PRIMARY
        )
        icon_badge.pack(pady=(36, 12))
        icon_badge.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_badge,
            text="🏢",
            font=("Segoe UI Emoji", 28),
            text_color="#FFFFFF"
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        title_lbl = ctk.CTkLabel(
            card,
            text="HMS Nexus",
            font=theme.FONT_TITLE_LARGE,
            text_color=theme.TEXT_PRIMARY
        )
        title_lbl.pack(pady=(0, 2))

        subtitle_lbl = ctk.CTkLabel(
            card,
            text="Hostel Management System",
            font=theme.FONT_CARD_LABEL,
            text_color=theme.TEXT_SECONDARY
        )
        subtitle_lbl.pack(pady=(0, 24))

        # Form Inputs Frame
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=36, pady=0)

        # Username Field
        lbl_user = ctk.CTkLabel(
            form_frame,
            text="Username / Student ID",
            font=theme.FONT_BODY_BOLD,
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        lbl_user.pack(fill="x", pady=(0, 4))

        self.entry_username = ctk.CTkEntry(
            form_frame,
            placeholder_text="e.g. admin or STU001",
            font=theme.FONT_BODY,
            height=42,
            corner_radius=theme.RADIUS_ENTRY
        )
        self.entry_username.pack(fill="x", pady=(0, 14))

        # Password Field
        lbl_pass = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=theme.FONT_BODY_BOLD,
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        lbl_pass.pack(fill="x", pady=(0, 4))

        pass_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        pass_container.pack(fill="x", pady=(0, 12))
        pass_container.grid_columnconfigure(0, weight=1)

        self.entry_password = ctk.CTkEntry(
            pass_container,
            placeholder_text="Enter your password",
            show="•",
            font=theme.FONT_BODY,
            height=42,
            corner_radius=theme.RADIUS_ENTRY
        )
        self.entry_password.grid(row=0, column=0, sticky="ew")

        self.btn_toggle_pw = ctk.CTkButton(
            pass_container,
            text="👁",
            width=42,
            height=42,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_SECONDARY,
            hover_color=theme.BG_ROW_HOVER,
            corner_radius=theme.RADIUS_ENTRY,
            command=self._toggle_password_visibility
        )
        self.btn_toggle_pw.grid(row=0, column=1, padx=(6, 0))

        # Bind Enter key to login
        self.entry_username.bind("<Return>", lambda event: self._handle_login())
        self.entry_password.bind("<Return>", lambda event: self._handle_login())

        # Error notification label
        self.lbl_error = ctk.CTkLabel(
            card,
            text="",
            font=theme.FONT_SMALL,
            text_color=theme.DANGER,
            anchor="center"
        )
        self.lbl_error.pack(fill="x", padx=36, pady=(4, 8))

        # Login button
        self.btn_login = ctk.CTkButton(
            card,
            text="Sign In",
            font=theme.FONT_BUTTON,
            height=44,
            corner_radius=theme.RADIUS_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            command=self._handle_login
        )
        self.btn_login.pack(fill="x", padx=36, pady=(0, 18))

        # Demo Quick-Fill Section
        demo_frame = ctk.CTkFrame(card, fg_color=theme.BG_CARD_ALT, corner_radius=10)
        demo_frame.pack(fill="x", padx=36, pady=(0, 24))

        lbl_demo = ctk.CTkLabel(
            demo_frame,
            text="Quick Fill Credentials",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY
        )
        lbl_demo.pack(pady=(10, 6))

        btn_box = ctk.CTkFrame(demo_frame, fg_color="transparent")
        btn_box.pack(pady=(0, 10))

        btn_demo_admin = ctk.CTkButton(
            btn_box,
            text="🔑 Admin",
            font=theme.FONT_SMALL,
            width=110,
            height=28,
            corner_radius=6,
            fg_color=theme.SECONDARY,
            hover_color=theme.SECONDARY_HOVER,
            command=lambda: self._fill_credentials("admin", "admin123")
        )
        btn_demo_admin.pack(side="left", padx=4)

        btn_demo_student = ctk.CTkButton(
            btn_box,
            text="🎓 Student",
            font=theme.FONT_SMALL,
            width=110,
            height=28,
            corner_radius=6,
            fg_color=theme.SECONDARY,
            hover_color=theme.SECONDARY_HOVER,
            command=lambda: self._fill_credentials("STU001", "STU001")
        )
        btn_demo_student.pack(side="left", padx=4)

    def _toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.entry_password.configure(show="")
            self.btn_toggle_pw.configure(text="🔒")
        else:
            self.entry_password.configure(show="•")
            self.btn_toggle_pw.configure(text="👁")

    def _fill_credentials(self, username, password):
        self.entry_username.delete(0, "end")
        self.entry_username.insert(0, username)
        self.entry_password.delete(0, "end")
        self.entry_password.insert(0, password)
        self.lbl_error.configure(text="")

    def _handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            self.lbl_error.configure(text="Please enter both username and password.")
            return

        self.btn_login.configure(state="disabled", text="Verifying...")
        self.update_idletasks()

        success, result = db_service.authenticate_user(username, password)
        self.btn_login.configure(state="normal", text="Sign In")

        if success:
            self.lbl_error.configure(text="")
            self.on_login_success(result)
        else:
            self.lbl_error.configure(text=f"❌ {result}")
