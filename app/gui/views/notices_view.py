"""
Notices & Announcements View for HMS Desktop Application.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog
from app import db_service

class NoticesView(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        is_admin = current_user["role"] == "Admin"

        action_text = "📢 + Publish Notice" if is_admin else None
        action_cmd = self._open_add_notice_dialog if is_admin else None

        # Header
        self.header = PageHeader(
            self,
            title="Notice Board",
            subtitle="Campus notifications, hostel guidelines, and official circulars",
            action_text=action_text,
            action_cmd=action_cmd,
            action_color=theme.PRIMARY
        )
        self.header.pack(fill="x", padx=20, pady=(16, 14))

        # Body container
        self.notices_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.notices_body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.load_notices()

    def load_notices(self):
        for w in self.notices_body.winfo_children():
            w.destroy()

        notices = db_service.get_all_notices()
        if not notices:
            empty = ctk.CTkLabel(
                self.notices_body,
                text="No notices published yet.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED
            )
            empty.pack(pady=40)
            return

        for n in notices:
            card = ctk.CTkFrame(
                self.notices_body,
                fg_color=theme.BG_CARD,
                corner_radius=theme.RADIUS_CARD,
                border_width=1,
                border_color=theme.BORDER_COLOR
            )
            card.pack(fill="x", pady=8)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=20, pady=(16, 8))

            ctk.CTkLabel(
                top,
                text=n['title'],
                font=theme.FONT_SECTION_TITLE,
                text_color=theme.TEXT_PRIMARY
            ).pack(side="left")

            StatusBadge(top, n['category']).pack(side="right")

            # Description
            desc_box = ctk.CTkFrame(card, fg_color=theme.BG_CARD_ALT, corner_radius=8)
            desc_box.pack(fill="x", padx=20, pady=4)

            ctk.CTkLabel(
                desc_box,
                text=n['description'],
                font=theme.FONT_BODY,
                text_color=theme.TEXT_PRIMARY,
                wraplength=800,
                justify="left"
            ).pack(anchor="w", padx=14, pady=12)

            # Footer
            footer = ctk.CTkFrame(card, fg_color="transparent")
            footer.pack(fill="x", padx=20, pady=(8, 16))

            ctk.CTkLabel(
                footer,
                text=f"📅 Published: {n['date']}",
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY
            ).pack(side="left")

    def _open_add_notice_dialog(self):
        dlg = ModalDialog(self.winfo_toplevel(), title="Publish Notice", width=500, height=520)

        e_title = dlg.add_field("Notice Title *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Water Tank Cleaning Schedule"))
        e_cat = ctk.CTkOptionMenu(dlg.body, values=["General", "Urgent", "Maintenance", "Rules", "Events"])
        dlg.add_field("Category *", e_cat)

        lbl = ctk.CTkLabel(dlg.body, text="Notice Description *", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY, anchor="w")
        lbl.pack(fill="x", pady=(8, 4))
        e_desc = ctk.CTkTextbox(dlg.body, height=120, font=theme.FONT_BODY)
        e_desc.pack(fill="x", pady=(0, 6))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            title = e_title.get().strip()
            cat = e_cat.get()
            desc = e_desc.get("1.0", "end").strip()

            if not (title and desc):
                lbl_msg.configure(text="Please fill in title and description.")
                return

            ok, res = db_service.add_notice(title, cat, desc)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_notices()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Publish", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
