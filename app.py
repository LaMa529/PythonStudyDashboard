import customtkinter as ctk
import webbrowser
from datetime import date
from database import DatabaseManager
from models import Module, Settings
from enums import ExamType, StatusType, StudyModel, ThemeMode
import calculate


class DashboardApp(ctk.CTk):
    """
    Main GUI Application class.
    Inherits from CustomTkinter window and manages the overall layout,
    navigation, and view rendering. It acts as the Controller between the DB and the UI.
    """

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.settings = self.db.get_settings()
        self.apply_theme()

        self.title("Study Dashboard")
        self.geometry("1300x900")
        self.current_page = "dashboard"  # Saves the current view

        # Grid setup: Main content takes full space, sidebar floats on top (overlay)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.sidebar_expanded = False

        self.setup_header()

        # Main container for the dynamic pages (Dashboard, Modules, Settings)
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)

        self.setup_sidebar()
        self.show_dashboard()  # Load default view

    def apply_theme(self):
        """Applies the user's preferred theme (Light/Dark) to the CustomTkinter app."""
        mode = "dark" if self.settings and self.settings.theme == ThemeMode.DARK.value else "light"
        ctk.set_appearance_mode(mode)

    # ==========================================
    # Header & Sidebar
    # ==========================================
    def setup_header(self):
        """Builds the top navigation bar with the hamburger menu and user profile indicator."""
        self.header = ctk.CTkFrame(self, height=70, fg_color=("white", "#1c1c1e"), corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(self.header, text="☰", width=50, height=50, font=ctk.CTkFont(size=24),
                      fg_color="transparent", text_color=("black", "white"), hover_color=("gray90", "gray20"),
                      command=self.toggle_sidebar).grid(row=0, column=0, padx=20, pady=10)

        ctk.CTkLabel(self.header, text="Study Dashboard", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0,
                                                                                                         column=1,
                                                                                                         sticky="w")

    def setup_sidebar(self):
        """Builds the collapsible side navigation menu."""
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=("#f4f5f7", "#121212"), corner_radius=0, border_width=1)
        self.sidebar.grid_rowconfigure(4, weight=1)  # Spacer to push buttons up

        ctk.CTkLabel(self.sidebar, text="IU", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1a73e8").grid(
            row=0, column=0, pady=30, padx=20, sticky="w")

        nav_items = [("⌂", " Übersicht", self.show_dashboard),
                     ("≣", " Module", self.show_modules),
                     ("⛭", " Einstellungen", self.show_settings)]

        for i, (icon, text, cmd) in enumerate(nav_items, start=1):
            ctk.CTkButton(self.sidebar, text=f"{icon}   {text}", anchor="w", font=ctk.CTkFont(size=16),
                          fg_color="transparent", text_color=("black", "gray90"), hover_color=("gray80", "gray25"),
                          height=45, command=lambda c=cmd: self.handle_nav_click(c)).grid(row=i, column=0, sticky="ew",
                                                                                          padx=15, pady=8)

    def handle_nav_click(self, command):
        """Executes the view change and auto-closes the sidebar."""
        command()
        if self.sidebar_expanded: self.toggle_sidebar()

    def toggle_sidebar(self):
        """Toggles the visibility of the sidebar overlay."""
        if self.sidebar_expanded:
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid(row=1, column=0, sticky="nsw")
            self.sidebar.lift()
        self.sidebar_expanded = not self.sidebar_expanded

    def clear_content(self):
        """Utility to clear the main content frame before rendering a new view."""
        for widget in self.content_frame.winfo_children(): widget.destroy()

    # ==========================================
    # VIEW: DASHBOARD (Overview)
    # ==========================================
    def show_dashboard(self):
        """Renders the main dashboard view with KPI cards and What-If calculator."""
        self.current_page = "dashboard"
        self.clear_content()
        modules = self.db.get_modules()

        ctk.CTkLabel(self.content_frame, text=f"Hallo {self.settings.first_name}!",
                     font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 30))

        # Render KPI Cards
        kpi_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 30))
        kpi_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Top functions
        kpis = [
            ("Notendurchschnitt", f"{calculate.calculate_average_grade(modules):.2f}",
             f"Ziel: {self.settings.target_grade:.2f}"),
            ("Studienfortschritt", f"{calculate.calculate_progress_percentage(modules, self.settings) * 100:.0f}%",
             f"{calculate.calculate_completed_ects(modules)} von {self.settings.total_ects} ECTS"),
            ("Ziel-Prognose", calculate.calculate_end_date(modules, self.settings), "Voraussichtliches Ende")
        ]

        for i, (title, val, sub) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=("white", "#1c1c1e"), corner_radius=15)
            card.grid(row=0, column=i, padx=(0, 15) if i < 2 else 0, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=25, pady=(20, 5))
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=36, weight="bold"), text_color="#1a73e8").pack(
                anchor="w", padx=25)
            ctk.CTkLabel(card, text=sub, text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=25,
                                                                                            pady=(0, 20))

        # Render What-If Calculator Section
        wi_card = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=15)
        wi_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(wi_card, text="What-If Rechner", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=25,
                                                                                            pady=(20, 5))

        wi_input = ctk.CTkFrame(wi_card, fg_color="transparent")
        wi_input.pack(fill="x", padx=25, pady=15)

        # Target Grade
        self.entry_target_grade = ctk.CTkEntry(wi_input, placeholder_text="Ziel-Note (z.B. 2.0)", width=200, height=35)
        self.entry_target_grade.pack(side="left")

        self.lbl_whatif_res = ctk.CTkLabel(wi_input, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_whatif_res.pack(side="left", padx=20)

        ctk.CTkButton(wi_input, text="Berechnen", height=35, fg_color="#0b1021",
                      command=lambda: self.run_whatif(modules)).pack(side="right")

        # Render Active Modules List
        mod_card = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=15)
        mod_card.pack(fill="x")
        ctk.CTkLabel(mod_card, text="Aktuell belegte Module", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=25,
                                                                                                    pady=(20, 10))
        # Check for active modules
        active_mods = [m for m in modules if m.status in [StatusType.REGISTERED, StatusType.IN_PROGRESS]]
        if not active_mods: ctk.CTkLabel(mod_card, text="Keine aktiven Module.", text_color="gray").pack(pady=20)

        #List of active modules
        for mod in active_mods:
            row = ctk.CTkFrame(mod_card, fg_color="transparent", border_width=1, border_color=("gray85", "gray25"),
                               corner_radius=8)
            row.pack(fill="x", padx=25, pady=8)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=15, pady=15)
            ctk.CTkLabel(info, text=mod.name, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Prüfungsform: {mod.exam_type.value}    Status: {mod.status.value}",
                         text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w")

            btn_box = ctk.CTkFrame(row, fg_color="transparent")
            btn_box.pack(side="right", padx=15)

            b_kw = {"height": 30, "fg_color": "transparent", "border_width": 1, "text_color": ("black", "white"),
                    "hover_color": ("gray90", "gray20")}
            ctk.CTkButton(btn_box, text="↗ Webseite", width=80, state="normal" if mod.website_url else "disabled",
                          command=lambda url=mod.website_url: webbrowser.open(url) if url else None, **b_kw).pack( side="left", padx=5)
            ctk.CTkButton(btn_box, text="📄 PDF", width=60, state="normal" if mod.pdf_url else "disabled",
                          command=lambda url=mod.pdf_url: webbrowser.open(url) if url else None, **b_kw).pack(side="left", padx=5)
            ctk.CTkButton(btn_box, text="ⓘ Info", width=60, command=lambda m=mod: self.open_module_info_modal(m), **b_kw).pack(side="left", padx=5)

    def run_whatif(self, modules):
        """Action handler for the What-If calculation button."""
        try:
            val = float(self.entry_target_grade.get().replace(",", "."))
            needed = calculate.calculate_needed_grade(modules, val)
            if needed:
                self.lbl_whatif_res.configure(text=f"Benötigte Note: {needed:.2f}", text_color="#1a73e8")
            else:
                self.lbl_whatif_res.configure(text="Schnitt rechnerisch nicht erreichbar.", text_color="#ef4444")
        except ValueError:
            self.lbl_whatif_res.configure(text="Ungültige Eingabe.", text_color="#ef4444")

    # ==========================================
    # VIEW: MODULES LIST (CRUD Operations)
    # ==========================================
    def show_modules(self):
        """Renders the comprehensive module list with filters and edit/delete capabilities."""
        self.current_page = "modules"  # Set status
        self.clear_content()
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Module & Noten", font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Neues Modul", font=ctk.CTkFont(weight="bold"), fg_color="#0b1021", height=40, command=self.open_module_modal).pack(side="right")

        # Render Filters
        filter_card = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=10)
        filter_card.pack(fill="x", pady=(0, 20))

        f_grid = ctk.CTkFrame(filter_card, fg_color="transparent")
        f_grid.pack(fill="x", padx=25, pady=20)
        f_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Filter by semester, exam type, and status
        self.f_sem = ctk.StringVar(value="Alle")
        self.f_type = ctk.StringVar(value="Alle")
        self.f_stat = ctk.StringVar(value="Alle")

        all_mods = self.db.get_modules()
        sems = ["Alle"] + sorted(list(set(m.semester for m in all_mods)))

        ctk.CTkOptionMenu(f_grid, variable=self.f_sem, values=sems, command=lambda _: self.render_module_list()).grid(
            row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkOptionMenu(f_grid, variable=self.f_type, values=["Alle"] + ExamType.get_values(),
                          command=lambda _: self.render_module_list()).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ctk.CTkOptionMenu(f_grid, variable=self.f_stat, values=["Alle"] + StatusType.get_values(),
                          command=lambda _: self.render_module_list()).grid(row=0, column=2, sticky="ew")

        self.mod_list_container = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=10)
        self.mod_list_container.pack(fill="both", expand=True)
        self.render_module_list()

    def render_module_list(self):
        """Helper to re-render the module list dynamically when filters change."""
        for widget in self.mod_list_container.winfo_children(): widget.destroy()

        modules = self.db.get_modules()
        if self.f_sem.get() != "Alle": modules = [m for m in modules if m.semester == self.f_sem.get()]
        if self.f_type.get() != "Alle": modules = [m for m in modules if m.exam_type.value == self.f_type.get()]
        if self.f_stat.get() != "Alle": modules = [m for m in modules if m.status.value == self.f_stat.get()]

        if not modules:
            ctk.CTkLabel(
                self.mod_list_container,
                text="❌ Keine Module gefunden.\nLege ein neues Modul an oder ändere die Filter.",
                text_color="gray",
                font=ctk.CTkFont(size=14)
            ).pack(pady=40)
            return

        for mod in modules:
            row = ctk.CTkFrame(self.mod_list_container, fg_color=("gray98", "gray10"), corner_radius=8)
            row.pack(fill="x", padx=20, pady=5)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=1)
            row.grid_columnconfigure(3, weight=1)

            # Information per module
            ctk.CTkLabel(row, text=f"{mod.name} ({mod.semester})", font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=0, sticky="w", padx=15, pady=10)
            ctk.CTkLabel(row, text=f"{mod.exam_type.value} | {mod.status.value}").grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(row, text=f"Note: {mod.grade}" if mod.grade else "Note: -").grid(row=0, column=2)

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=3, sticky="e", padx=10)

            # Edit or delete modules
            ctk.CTkButton(actions, text="✎", width=30, height=30, fg_color="transparent", text_color=("black", "white"),
                          command=lambda m=mod: self.open_module_modal(m)).pack(side="left", padx=2)
            ctk.CTkButton(actions, text="🗑", width=30, height=30, fg_color="transparent", text_color="red",
                          command=lambda m=mod: self.delete_module(m)).pack(side="left")

    def delete_module(self, mod):
        """Action handler to delete a module and refresh the view."""
        self.db.delete_module(mod.id)
        self.show_modules()

    def open_module_info_modal(self, mod: Module):
        """Opens a read-only info window for the dashboard."""
        modal = ctk.CTkToplevel(self)
        modal.title("Modul-Details")
        modal.geometry("450x550")
        modal.grab_set()  # Locks the main window until it is closed

        # Headline
        ctk.CTkLabel(modal, text="Modul-Informationen", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w",
                                                                                                       padx=25,
                                                                                                       pady=(25, 5))
        ctk.CTkLabel(modal, text="Alle Details auf einen Blick (schreibgeschützt)", text_color="gray").pack(anchor="w",
                                                                                                            padx=25,
                                                                                                            pady=(0,
                                                                                                                  20))

        # Data container (in the form of a stylish card)
        card = ctk.CTkFrame(modal, fg_color=("gray95", "#1c1c1e"), corner_radius=10)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        # Help feature for consistent info lines
        def add_info_row(parent, label, value):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(row, text=label, text_color="gray", width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", fill="x",
                                                                                                 expand=True)

        # Show data
        add_info_row(card, "Modulname:", mod.name)
        add_info_row(card, "Semester:", mod.semester)
        add_info_row(card, "ECTS:", mod.ects)
        add_info_row(card, "Prüfungsform:", mod.exam_type.value)
        add_info_row(card, "Status:", mod.status.value)

        grade_text = f"{mod.grade:.2f}" if mod.grade else "Noch keine Note"
        add_info_row(card, "Note:", grade_text)

        date_text = mod.exam_date.strftime("%d.%m.%Y") if mod.exam_date else "Nicht festgelegt"
        add_info_row(card, "Prüfungsdatum:", date_text)

        # Close Button
        ctk.CTkButton(modal, text="Schließen", fg_color="#0b1021", height=40, font=ctk.CTkFont(weight="bold"),
                      command=modal.destroy).pack(pady=(0, 25))

    def open_module_modal(self, mod: Module = None):
        modal = ctk.CTkToplevel(self)
        modal.title("Modul bearbeiten" if mod else "Neues Modul")
        modal.geometry("500x700")
        modal.grab_set()

        def add_entry(parent, label_text, default_val=""):
            ctk.CTkLabel(parent, text=label_text).pack(anchor="w", padx=20, pady=(10, 0))
            e = ctk.CTkEntry(parent)
            e.pack(fill="x", padx=20, pady=(0, 5))
            if default_val is not None: e.insert(0, str(default_val))
            return e

        e_name = add_entry(modal, "Modulname *", mod.name if mod else "")
        e_sem = add_entry(modal, "Semester *", mod.semester if mod else "WS 2024")
        e_ects = add_entry(modal, "ECTS *", mod.ects if mod else 5)

        ctk.CTkLabel(modal, text="Prüfungsform").pack(anchor="w", padx=20, pady=(10, 0))
        cb_type = ctk.CTkOptionMenu(modal, values=ExamType.get_values())
        cb_type.pack(fill="x", padx=20)
        cb_type.set(mod.exam_type.value if mod else ExamType.WRITTENEXAM.value)

        ctk.CTkLabel(modal, text="Status").pack(anchor="w", padx=20, pady=(10, 0))
        cb_stat = ctk.CTkOptionMenu(modal, values=StatusType.get_values())
        cb_stat.pack(fill="x", padx=20)
        cb_stat.set(mod.status.value if mod else StatusType.REGISTERED.value)

        e_grade = add_entry(modal, "Note", mod.grade if mod else "")
        e_web = add_entry(modal, "Website URL", mod.website_url if mod else "")
        e_pdf = add_entry(modal, "PDF URL", mod.pdf_url if mod else "")

        # Define the error label
        self.lbl_modal_error = ctk.CTkLabel(modal, text="", text_color="#ef4444", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_modal_error.pack(pady=(10, 0))

        def save():
            """
            Validates user input and saves the module to the SQLite database.
            Updates the UI based on the current active page.
            """
            try:
                # Clear previous error messages
                self.lbl_modal_error.configure(text="")

                # 1. Basic Validation (Mandatory fields)
                name = e_name.get().strip()
                sem = e_sem.get().strip()
                ects_raw = e_ects.get().strip()

                if not name or not sem or not ects_raw:
                    self.lbl_modal_error.configure(text="❌ Name, Semester and ECTS are required!")
                    return

                # 2. Number Conversion & Validation
                try:
                    ects = int(ects_raw)
                except ValueError:
                    self.lbl_modal_error.configure(text="❌ ECTS must be a whole number!")
                    return

                # Handle optional grade (allows empty string or number)
                grade_str = e_grade.get().replace(",", ".").strip()
                grade = float(grade_str) if grade_str else None

                # 3. Enum Mapping
                etype = ExamType.from_value(cb_type.get())
                stype = StatusType.from_value(cb_stat.get())

                # 4. Create or Update Module Object
                # If mod exists, we keep the original ID, otherwise 0 for new entry
                m = Module(
                    id=mod.id if mod else 0,
                    name=name,
                    semester=sem,
                    exam_type=etype,
                    status=stype,
                    ects=ects,
                    grade=grade,
                    website_url=e_web.get().strip() or None,
                    pdf_url=e_pdf.get().strip() or None
                )

                # 5. Database Transaction
                if mod:
                    self.db.update_module(m)
                else:
                    self.db.add_module(m)

                # 6. UI Cleanup and Refresh
                modal.destroy()

                # Determine which view to refresh based on our state variable
                if self.current_page == "dashboard":
                    self.show_dashboard()
                else:
                    self.show_modules()

            except Exception as e:
                # Catch-all for unexpected errors (e.g. Database locked)
                # Only update label if the window hasn't been closed yet
                if modal.winfo_exists():
                    self.lbl_modal_error.configure(text=f"❌ Error: {str(e)}")

        ctk.CTkButton(modal, text="Speichern", command=save, fg_color="#0b1021", height=40).pack(pady=20, padx=20, fill="x")

    # ==========================================
    # VIEW: SETTINGS
    # ==========================================
    def show_settings(self):
        """Renders the settings view for user preferences, split into logical cards."""
        self.clear_content()
        s = self.db.get_settings()

        ctk.CTkLabel(self.content_frame, text="Einstellungen", font=ctk.CTkFont(size=32, weight="bold")).pack(
            anchor="w", pady=(0, 20))

        # --- Name ---
        card_name = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=15)
        card_name.pack(fill="x", pady=10)
        ctk.CTkLabel(card_name, text="Name", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=25,
                                                                                            pady=(20, 10))

        f_name = ctk.CTkFrame(card_name, fg_color="transparent")
        f_name.pack(fill="x", padx=25, pady=(0, 25))
        f_name.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(f_name, text="Vorname", text_color="gray").grid(row=0, column=0, sticky="w")
        e_first = ctk.CTkEntry(f_name, height=35)
        e_first.grid(row=1, column=0, sticky="ew", padx=(0, 15))
        e_first.insert(0, s.first_name)

        ctk.CTkLabel(f_name, text="Nachname", text_color="gray").grid(row=0, column=1, sticky="w")
        e_last = ctk.CTkEntry(f_name, height=35)
        e_last.grid(row=1, column=1, sticky="ew")
        e_last.insert(0, s.last_name)

        # --- Study ---
        card_study = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=15)
        card_study.pack(fill="x", pady=10)
        ctk.CTkLabel(card_study, text="Studium", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=25,
                                                                                                pady=(20, 10))

        f_study = ctk.CTkFrame(card_study, fg_color="transparent")
        f_study.pack(fill="x", padx=25, pady=(0, 25))
        f_study.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(f_study, text="Studiengang", text_color="gray").grid(row=0, column=0, sticky="w")
        e_prog = ctk.CTkEntry(f_study, height=35)
        e_prog.grid(row=1, column=0, sticky="ew", padx=(0, 15), pady=(0, 15))
        e_prog.insert(0, s.study_program)

        ctk.CTkLabel(f_study, text="ECTS Gesamt", text_color="gray").grid(row=0, column=1, sticky="w")
        e_ects = ctk.CTkEntry(f_study, height=35)
        e_ects.grid(row=1, column=1, sticky="ew", pady=(0, 15))
        e_ects.insert(0, str(s.total_ects))

        ctk.CTkLabel(f_study, text="Studienbeginn (YYYY-MM)", text_color="gray").grid(row=2, column=0, sticky="w")
        e_start = ctk.CTkEntry(f_study, height=35)
        e_start.grid(row=3, column=0, sticky="ew", padx=(0, 15), pady=(0, 15))
        e_start.insert(0, s.study_start)

        ctk.CTkLabel(f_study, text="Ziel-Note (Wunschschnitt)", text_color="gray").grid(row=2, column=1, sticky="w")
        e_target = ctk.CTkEntry(f_study, height=35)
        e_target.grid(row=3, column=1, sticky="ew", pady=(0, 15))
        e_target.insert(0, str(s.target_grade))

        ctk.CTkLabel(f_study, text="Studienmodell", text_color="gray").grid(row=4, column=0, columnspan=2, sticky="w")
        cb_model = ctk.CTkOptionMenu(f_study, values=StudyModel.get_values(), height=35, fg_color=("gray95", "gray20"),
                                     text_color=("black", "white"))
        cb_model.grid(row=5, column=0, columnspan=2, sticky="ew")
        cb_model.set(s.study_model.value)

        # --- Darkmode ---
        card_theme = ctk.CTkFrame(self.content_frame, fg_color=("white", "#1c1c1e"), corner_radius=15)
        card_theme.pack(fill="x", pady=10)
        ctk.CTkLabel(card_theme, text="Darstellung", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=25,
                                                                                                 pady=(20, 10))

        theme_var = ctk.StringVar(value=s.theme)

        def toggle_t():
            # Changes the design immediately when clicked (preview effect)
            ctk.set_appearance_mode("dark" if theme_var.get() == "Dark" else "light")

        ctk.CTkSwitch(card_theme, text="Darkmode", font=ctk.CTkFont(weight="bold"), variable=theme_var,
                      onvalue="Dark", offvalue="Light", command=toggle_t).pack(anchor="w", padx=25, pady=(0, 25))

        # Create error messages
        self.lbl_settings_error = ctk.CTkLabel(self.content_frame, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_settings_error.pack(pady=5, anchor="e")

        # --- Storage Logic ---
        def save_s():
            """Action handler to update user settings in DB and refresh the UI."""
            try:
                s.first_name, s.last_name = e_first.get(), e_last.get()
                s.study_program, s.study_start = e_prog.get(), e_start.get()
                s.total_ects = int(e_ects.get())
                s.target_grade = float(e_target.get().replace(",", "."))
                s.study_model, s.theme = StudyModel.from_value(cb_model.get()), theme_var.get()

                self.db.save_settings(s)
                self.lbl_settings_error.configure(text="✅ Einstellungen erfolgreich gespeichert!", text_color="#10b981")
                self.after(1000, lambda: self.show_dashboard())
            except ValueError:
                self.lbl_settings_error.configure(text="❌ ECTS und Note müssen Zahlen sein!", text_color="#ef4444")

        ctk.CTkButton(self.content_frame, text="Einstellungen speichern", command=save_s, height=45,
                      font=ctk.CTkFont(size=14, weight="bold"), fg_color="#0b1021").pack(anchor="e", pady=20)


if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()