"""
Reusable CustomTkinter UI Components for Hostel Management System.
"""
import customtkinter as ctk
from app.gui import theme

class StatCard(ctk.CTkFrame):
    """Modern metric dashboard card with icon, count, and label."""
    def __init__(self, master, title, value, icon, color=theme.PRIMARY, **kwargs):
        super().__init__(
            master,
            corner_radius=theme.RADIUS_CARD,
            fg_color=theme.BG_CARD,
            border_width=1,
            border_color=theme.BORDER_COLOR,
            **kwargs
        )
        self.grid_columnconfigure(1, weight=1)

        # Icon pill on left
        self.icon_frame = ctk.CTkFrame(
            self,
            width=48,
            height=48,
            corner_radius=10,
            fg_color=color
        )
        self.icon_frame.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16)
        self.icon_frame.grid_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_frame,
            text=icon,
            font=("Segoe UI Emoji", 20),
            text_color="#FFFFFF"
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Number count
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=theme.FONT_CARD_VALUE,
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        self.value_label.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=(14, 0))

        # Title / Label
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=theme.FONT_CARD_LABEL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.title_label.grid(row=1, column=1, sticky="w", padx=(0, 16), pady=(0, 14))

    def update_value(self, new_val):
        self.value_label.configure(text=str(new_val))


class PageHeader(ctk.CTkFrame):
    """Standard header row for each view with Title, Subtitle, and Action buttons."""
    def __init__(self, master, title, subtitle="", action_text=None, action_cmd=None, action_color=theme.PRIMARY, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")

        self.title_lbl = ctk.CTkLabel(
            title_frame,
            text=title,
            font=theme.FONT_TITLE_LARGE,
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        self.title_lbl.pack(anchor="w")

        if subtitle:
            self.sub_lbl = ctk.CTkLabel(
                title_frame,
                text=subtitle,
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY,
                anchor="w"
            )
            self.sub_lbl.pack(anchor="w", pady=(2, 0))

        if action_text and action_cmd:
            self.action_btn = ctk.CTkButton(
                self,
                text=action_text,
                command=action_cmd,
                font=theme.FONT_BUTTON,
                fg_color=action_color,
                corner_radius=theme.RADIUS_BUTTON,
                height=36,
                hover_color=theme.PRIMARY_HOVER
            )
            self.action_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))


class StatusBadge(ctk.CTkLabel):
    """Colored status badge/pill (e.g. Active, Occupied, Paid, Pending)."""
    COLOR_MAP = {
        "active": (theme.SUCCESS, "#FFFFFF"),
        "available": (theme.SUCCESS, "#FFFFFF"),
        "paid": (theme.SUCCESS, "#FFFFFF"),
        "approved": (theme.SUCCESS, "#FFFFFF"),
        "present": (theme.SUCCESS, "#FFFFFF"),
        "resolved": (theme.SUCCESS, "#FFFFFF"),
        
        "pending": (theme.WARNING, "#FFFFFF"),
        "partially filled": (theme.WARNING, "#FFFFFF"),
        "in progress": (theme.WARNING, "#FFFFFF"),
        "leave": (theme.WARNING, "#FFFFFF"),
        
        "occupied": (theme.DANGER, "#FFFFFF"),
        "full": (theme.DANGER, "#FFFFFF"),
        "rejected": (theme.DANGER, "#FFFFFF"),
        "absent": (theme.DANGER, "#FFFFFF"),
        "overdue": (theme.DANGER, "#FFFFFF"),
        
        "inactive": (theme.SECONDARY, "#FFFFFF"),
        "normal": (theme.INFO, "#FFFFFF"),
        "urgent": (theme.DANGER, "#FFFFFF"),
        "high": (theme.DANGER, "#FFFFFF"),
        "low": (theme.SECONDARY, "#FFFFFF")
    }

    def __init__(self, master, status_text, **kwargs):
        normalized = status_text.strip().lower()
        bg_col, text_col = self.COLOR_MAP.get(normalized, (theme.SECONDARY, "#FFFFFF"))

        super().__init__(
            master,
            text=f"  {status_text}  ",
            fg_color=bg_col,
            text_color=text_col,
            corner_radius=theme.RADIUS_BADGE,
            font=("Segoe UI", 10, "bold"),
            height=22,
            **kwargs
        )


class ModalDialog(ctk.CTkToplevel):
    """Base class for modern modal dialogs with backdrop focus."""
    def __init__(self, parent, title="Dialog", width=480, height=520):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_CARD)

        # Center on parent
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
            self.geometry(f"+{max(50, x)}+{max(50, y)}")
        except Exception:
            pass

        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=24, pady=(20, 10))

        self.lbl_title = ctk.CTkLabel(
            self.header,
            text=title,
            font=theme.FONT_SECTION_TITLE,
            text_color=theme.TEXT_PRIMARY
        )
        self.lbl_title.pack(anchor="w")

        # Scrollable / Body frame
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=24, pady=10)

        # Footer with action buttons
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=24, pady=(10, 20))

    def add_field(self, label_text, widget):
        """Helper to append a labeled form field into the dialog body."""
        lbl = ctk.CTkLabel(
            self.body,
            text=label_text,
            font=theme.FONT_BODY_BOLD,
            text_color=theme.TEXT_PRIMARY,
            anchor="w"
        )
        lbl.pack(fill="x", pady=(8, 4))
        widget.pack(fill="x", pady=(0, 6))
        return widget
