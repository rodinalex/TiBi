import os
from functools import partial
from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QMessageBox, QFileDialog

from resources.action_manager import ActionManager
from src.serialization import serialize_unit_cells, deserialize_unit_cells


class MainUIController(QObject):
    """
    Controller for the main UI components (menu bar, toolbar, status bar).

    This controller connects the UI elements to the application logic and manages
    the action manager that provides shared actions to the menu bar and toolbar.
    """

    wireframe_toggled = Signal(bool)  # Toggle the unit cell wireframe on/off
    new_project_requested = (
        Signal()
    )  # New project signal: handled by the AppController to reset all models to their pristine state

    def __init__(
        self, models, main_window, menu_bar_view, toolbar_view, status_bar_view
    ):
        """
        Initialize the main UI controller.

        Args:
            models: Dictionary of data models used in the application
            main_window: MainWindow instance
            menu_bar_view: MenuBarView instance
            toolbar_view: MainToolbarView instance
            status_bar_view: StatusBarView instance
        """
        super().__init__()
        self.models = models
        self.main_window = main_window
        self.menu_bar = menu_bar_view
        self.toolbar = toolbar_view
        self.status_bar = status_bar_view

        # Create the action manager
        self.action_manager = ActionManager(self)

        # Set up action handlers
        self._connect_action_handlers()

        # Set actions to views
        self.menu_bar.set_actions(self.action_manager)
        self.toolbar.set_actions(self.action_manager)

    def _connect_action_handlers(self):
        """Connect actions to their handler methods."""
        # Create a dictionary mapping action names to handler methods
        handlers = {
            # File actions
            "new_project": self._handle_new_project,
            "open_project": self._handle_open_project,
            "import_project": self._handle_import_project,
            "save_project": partial(self._handle_save_project, use_existing_path=True),
            "save_project_as": partial(
                self._handle_save_project, use_existing_path=False
            ),
            # "export": self._handle_export,
            # "quit": self._handle_quit,
            # # Edit actions
            # "preferences": self._handle_preferences,
            # # View actions
            # "show_toolbar": self._handle_show_toolbar,
            # "show_statusbar": self._handle_show_statusbar,
            # # Computation actions
            # "compute_bands": self._handle_compute_bands,
            # "compute_dos": self._handle_compute_dos,
            # # Help actions
            # "about": self._handle_about,
            # "help": self._handle_help,
            # Unit cell actions
            "wireframe": self._handle_wireframe_toggle,
        }

        # Connect actions to handlers
        self.action_manager.connect_signals(handlers)

    # Handler methods for actions

    @Slot()
    def _handle_new_project(self):
        """Handle request to create a new project."""
        self.update_status("Creating new project...")
        reply = QMessageBox.question(
            self.main_window,
            "Start New Project?",
            "⚠️  This will clear your current project.\n\nAre you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.new_project_requested.emit()

    @Slot()
    def _handle_open_project(self):
        """Handle request to open a project."""
        self.update_status("Opening project...")
        # Implementation will be added later

    @Slot()
    def _handle_import_project(self):
        """Handle request to import a project."""
        self.update_status("Importing project...")
        # Implementation will be added later

    @Slot()
    def _handle_save_project(self, use_existing_path=True):
        """Handle request to save the current project."""
        self.update_status("Saving project...")
        json_string = serialize_unit_cells(self.models["unit_cells"])
        if use_existing_path:
            file_path = self.models["project_path"]
        else:
            file_path = None

        if not file_path:
            # Open a save file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Unit Cells As JSON",
                os.getcwd(),  # starting directory
                "JSON Files (*.json)",
            )

        if file_path:
            if file_path and not file_path.endswith(".json"):
                file_path += ".json"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_string)
            self.models["project_path"] = file_path

    @Slot()
    def _handle_wireframe_toggle(self, is_checked):
        """Handle wireframe toggle."""
        self.update_status("Wireframe...")
        # Implementation will be added later
        self.wireframe_toggled.emit(is_checked)

    # Methods to be called from other controllers

    def update_status(self, message):
        """
        Display a message in the status bar.

        Args:
            message: Message to display
        """
        self.status_bar.update_status(message)

    # @Slot()
    # def _handle_export(self):
    #     """Handle request to export data."""
    #     self.update_status("Exporting data...")
    #     # Implementation will be added later

    # @Slot()
    # def _handle_quit(self):
    #     """Handle request to quit the application."""
    #     self.update_status("Quitting application...")
    #     # Implementation will be added later

    # @Slot()
    # def _handle_preferences(self):
    #     """Handle request to open preferences."""
    #     self.update_status("Opening preferences...")
    #     # Implementation will be added later

    # @Slot(bool)
    # def _handle_show_toolbar(self, checked):
    #     """
    #     Handle request to show/hide toolbar.

    #     Args:
    #         checked: Whether the action is checked or not
    #     """
    #     self.toolbar.setVisible(checked)
    #     self.update_status(f"Toolbar {'shown' if checked else 'hidden'}")

    # @Slot(bool)
    # def _handle_show_statusbar(self, checked):
    #     """
    #     Handle request to show/hide status bar.

    #     Args:
    #         checked: Whether the action is checked or not
    #     """
    #     self.status_bar.setVisible(checked)
    #     # Can't update status if it's hidden
    #     if checked:
    #         self.update_status("Status bar shown")

    # @Slot()
    # def _handle_compute_bands(self):
    #     """Handle request to compute band structure."""
    #     self.update_status("Computing bands...")
    #     # Implementation will be added later

    # @Slot()
    # def _handle_compute_dos(self):
    #     """Handle request to compute density of states."""
    #     self.update_status("Computing density of states...")
    #     # Implementation will be added later

    # @Slot()
    # def _handle_about(self):
    #     """Handle request to show about dialog."""
    #     self.update_status("About TiBi")
    #     # Implementation will be added later

    # @Slot()
    # def _handle_help(self):
    #     """Handle request to show help."""
    #     self.update_status("Opening help...")
    #     # Implementation will be added later
