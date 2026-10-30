"""
Hostels & Rooms Management View for HMS Desktop Application.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.gui import theme
from app.gui.components import PageHeader, StatusBadge, ModalDialog
from app import db_service

class HostelsRoomsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Header with dual actions
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=(16, 12))
        self.header.grid_columnconfigure(0, weight=1)

        header_title = ctk.CTkLabel(
            self.header,
            text="Hostel Blocks & Rooms",
            font=theme.FONT_TITLE_LARGE,
            text_color=theme.TEXT_PRIMARY
        )
        header_title.grid(row=0, column=0, sticky="w")

        btn_box = ctk.CTkFrame(self.header, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="e")

        btn_add_hostel = ctk.CTkButton(
            btn_box,
            text="🏢 + Add Hostel",
            font=theme.FONT_BUTTON,
            fg_color=theme.PRIMARY,
            command=self._open_add_hostel_dialog,
            height=36
        )
        btn_add_hostel.pack(side="left", padx=(0, 8))

        btn_add_room = ctk.CTkButton(
            btn_box,
            text="🚪 + Add Room",
            font=theme.FONT_BUTTON,
            fg_color=theme.INFO,
            command=self._open_add_room_dialog,
            height=36
        )
        btn_add_room.pack(side="left")

        # Tabview for Hostels vs Rooms
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=theme.BG_CARD,
            segmented_button_fg_color=theme.BG_CARD_ALT,
            segmented_button_selected_color=theme.PRIMARY,
            segmented_button_selected_hover_color=theme.PRIMARY_HOVER,
            corner_radius=theme.RADIUS_CARD
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tab_hostels = self.tabview.add("Hostel Blocks")
        self.tab_rooms = self.tabview.add("Rooms & Beds")

        self._build_hostels_tab()
        self._build_rooms_tab()

        self.load_all()

    def _build_hostels_tab(self):
        # Header row
        header = ctk.CTkFrame(self.tab_hostels, fg_color=theme.BG_CARD_ALT, height=40, corner_radius=8)
        header.pack(fill="x", padx=8, pady=(8, 6))
        header.pack_propagate(False)

        cols = [
            ("Hostel Block", 180),
            ("Type", 100),
            ("Location", 160),
            ("Total Rooms", 120),
            ("Beds (Occupied / Total)", 180),
            ("Status", 100)
        ]
        for name, width in cols:
            ctk.CTkLabel(header, text=name, font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY, width=width, anchor="w").pack(side="left", padx=8)

        self.hostels_body = ctk.CTkScrollableFrame(self.tab_hostels, fg_color="transparent")
        self.hostels_body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_rooms_tab(self):
        # Filter bar
        filter_bar = ctk.CTkFrame(self.tab_rooms, fg_color="transparent")
        filter_bar.pack(fill="x", padx=8, pady=(8, 10))

        ctk.CTkLabel(filter_bar, text="Filter by Hostel:", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_PRIMARY).pack(side="left", padx=(0, 8))

        self.opt_hostel_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Hostels"],
            command=lambda v: self.load_rooms()
        )
        self.opt_hostel_filter.pack(side="left", padx=(0, 10))

        btn_refresh = ctk.CTkButton(
            filter_bar,
            text="🔄 Refresh",
            width=80,
            fg_color=theme.BG_CARD_ALT,
            text_color=theme.TEXT_PRIMARY,
            command=self.load_all
        )
        btn_refresh.pack(side="left")

        # Rooms grid
        self.rooms_body = ctk.CTkScrollableFrame(self.tab_rooms, fg_color="transparent")
        self.rooms_body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def load_all(self):
        self.load_hostels()
        self.load_rooms()

    def load_hostels(self):
        for w in self.hostels_body.winfo_children():
            w.destroy()

        hostels = db_service.get_all_hostels()
        if not hostels:
            ctk.CTkLabel(self.hostels_body, text="No hostel blocks registered.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=30)
            return

        # Update filter dropdown options
        options = ["All Hostels"] + [h["name"] for h in hostels]
        self.opt_hostel_filter.configure(values=options)

        for idx, h in enumerate(hostels):
            bg = theme.BG_CARD if idx % 2 == 0 else theme.BG_CARD_ALT
            row = ctk.CTkFrame(self.hostels_body, fg_color=bg, height=48, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"🏢 {h['name']}", font=theme.FONT_BODY_BOLD, width=180, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=h["type"], font=theme.FONT_BODY, width=100, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=h["location"], font=theme.FONT_BODY, width=160, anchor="w", text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"{h['room_count']} Rooms", font=theme.FONT_BODY, width=120, anchor="w", text_color=theme.TEXT_PRIMARY).pack(side="left", padx=8)

            beds_text = f"{h['occupied_beds']} / {h['total_beds']} Occupied"
            ctk.CTkLabel(row, text=beds_text, font=theme.FONT_BODY_BOLD, width=180, anchor="w", text_color=theme.PRIMARY).pack(side="left", padx=8)

            status_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
            status_frame.pack(side="left", padx=8)
            StatusBadge(status_frame, h["status"]).pack(anchor="w")

    def load_rooms(self):
        for w in self.rooms_body.winfo_children():
            w.destroy()

        selected_hostel = self.opt_hostel_filter.get()
        hostel_id = None
        if selected_hostel != "All Hostels":
            all_h = db_service.get_all_hostels()
            matched = next((h for h in all_h if h["name"] == selected_hostel), None)
            if matched:
                hostel_id = matched["id"]

        rooms = db_service.get_all_rooms(hostel_id)
        if not rooms:
            ctk.CTkLabel(self.rooms_body, text="No rooms found.", font=theme.FONT_BODY, text_color=theme.TEXT_MUTED).pack(pady=30)
            return

        for r in rooms:
            card = ctk.CTkFrame(self.rooms_body, fg_color=theme.BG_CARD_ALT, corner_radius=10, border_width=1, border_color=theme.BORDER_COLOR)
            card.pack(fill="x", pady=6, padx=4)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(12, 6))

            ctk.CTkLabel(top_row, text=f"🚪 Room {r['room_number']}", font=theme.FONT_SECTION_TITLE, text_color=theme.TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(top_row, text=f"({r['hostel_name']} - Floor {r['floor']})", font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY).pack(side="left", padx=8)

            StatusBadge(top_row, r['status']).pack(side="right")

            # Beds status pills
            beds_frame = ctk.CTkFrame(card, fg_color="transparent")
            beds_frame.pack(fill="x", padx=16, pady=(0, 12))

            ctk.CTkLabel(beds_frame, text="Beds: ", font=theme.FONT_BODY_BOLD, text_color=theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

            for b in r["beds"]:
                b_color = theme.DANGER if b["status"] == "Occupied" else theme.SUCCESS
                chip = ctk.CTkLabel(
                    beds_frame,
                    text=f" {b['number']} ({b['status'][:3]}) ",
                    fg_color=b_color,
                    text_color="#FFFFFF",
                    corner_radius=6,
                    font=("Segoe UI", 10, "bold"),
                    height=20
                )
                chip.pack(side="left", padx=4)

    def _open_add_hostel_dialog(self):
        dlg = ModalDialog(self.winfo_toplevel(), title="Add Hostel Block", width=460, height=480)

        e_name = dlg.add_field("Hostel Name *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. Gamma Block"))
        e_type = ctk.CTkOptionMenu(dlg.body, values=["Boys", "Girls", "Co-ed"])
        dlg.add_field("Hostel Type *", e_type)
        e_loc = dlg.add_field("Campus Location *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. West Campus Gate 2"))
        e_cap = dlg.add_field("Capacity (Approx beds) *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. 100"))

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            name = e_name.get().strip()
            h_type = e_type.get()
            loc = e_loc.get().strip()
            cap = e_cap.get().strip()

            if not (name and loc and cap and cap.isdigit()):
                lbl_msg.configure(text="Please fill in all fields with valid numbers.")
                return

            ok, res = db_service.add_hostel(name, h_type, loc, cap)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_all()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Create Hostel", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")

    def _open_add_room_dialog(self):
        hostels = db_service.get_all_hostels()
        if not hostels:
            messagebox.showwarning("No Hostels", "Please add a hostel block first before adding rooms.", parent=self.winfo_toplevel())
            return

        dlg = ModalDialog(self.winfo_toplevel(), title="Add Room & Generate Beds", width=460, height=520)

        hostel_names = [h["name"] for h in hostels]
        e_hostel = ctk.CTkOptionMenu(dlg.body, values=hostel_names)
        dlg.add_field("Hostel Block *", e_hostel)

        e_room_no = dlg.add_field("Room Number *", ctk.CTkEntry(dlg.body, placeholder_text="e.g. A-201"))
        e_floor = ctk.CTkOptionMenu(dlg.body, values=["1", "2", "3", "4", "5"])
        dlg.add_field("Floor Number *", e_floor)

        e_capacity = ctk.CTkOptionMenu(dlg.body, values=["1", "2", "3", "4", "6"])
        dlg.add_field("Bed Capacity (Beds will auto-generate) *", e_capacity)

        lbl_msg = ctk.CTkLabel(dlg.footer, text="", font=theme.FONT_SMALL, text_color=theme.DANGER)
        lbl_msg.pack(fill="x", pady=(0, 8))

        def submit():
            chosen_hostel_name = e_hostel.get()
            room_no = e_room_no.get().strip()
            floor = e_floor.get()
            capacity = e_capacity.get()

            h_obj = next((h for h in hostels if h["name"] == chosen_hostel_name), None)
            if not h_obj or not room_no:
                lbl_msg.configure(text="Please fill in all room details.")
                return

            ok, res = db_service.add_room(h_obj["id"], room_no, floor, capacity)
            if ok:
                messagebox.showinfo("Success", res, parent=dlg)
                dlg.destroy()
                self.load_all()
            else:
                lbl_msg.configure(text=f"❌ {res}")

        btn_box = ctk.CTkFrame(dlg.footer, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Create Room", font=theme.FONT_BUTTON, fg_color=theme.PRIMARY, command=submit).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_box, text="Cancel", font=theme.FONT_BODY_BOLD, fg_color=theme.SECONDARY, command=dlg.destroy).pack(side="right")
