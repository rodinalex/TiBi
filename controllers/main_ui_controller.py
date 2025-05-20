from functools import partial
import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QFileDialog, QMessageBox
import uuid

from resources.action_manager import ActionManager
from src.serialization import serialize_unit_cells, deserialize_unit_cells
from views.menu_bar_view import MenuBarView
from views.main_toolbar_view import MainToolbarView
from views.status_bar_view import StatusBarView


class MainUIController(QObject):
    """
    Controller for the main UI components (menu bar, toolbar, status bar).

    This controller connects the UI elements to the application logic and
    manages the action manager that provides shared actions to the menu
    bar and toolbar.

    Attributes
    ----------

    Signals
    -------
    """

    wireframe_toggled = Signal(bool)  # Toggle the unit cell wireframe on/off
    # Request a UI refresh after creating a new project
    # or loading an existing one
    project_refresh_requested = Signal()

    def __init__(
        self,
        models,
        main_window,
        menu_bar_view: MenuBarView,
        toolbar_view: MainToolbarView,
        status_bar_view: StatusBarView,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the main UI controller.

        Args:
            models: Dictionary of data models used in the application
            main_window: MainWindow instance
            menu_bar_view: MenuBarView instance
            toolbar_view: MainToolbarView instance
            status_bar_view: StatusBarView instance
            undo_stack: QUndoStack instance
        """
        super().__init__()
        self.models = models
        self.main_window = main_window
        self.menu_bar = menu_bar_view
        self.toolbar = toolbar_view
        self.status_bar = status_bar_view
        self.undo_stack = undo_stack

        # Create the action manager
        self.action_manager = ActionManager(
            undo_stack=self.undo_stack, parent=self
        )

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
            "save_project": partial(
                self._handle_save_project, use_existing_path=True
            ),
            "save_project_as": partial(
                self._handle_save_project, use_existing_path=False
            ),
            # Undo/Redo actions
            "undo": self.undo_stack.undo,
            "redo": self.undo_stack.redo,
            # Unit cell actions
            "wireframe": self._handle_wireframe_toggle,
        }

        # Connect actions to handlers
        self.action_manager.connect_signals(handlers)

    # Handler methods for actions

    @Slot()
    def _handle_new_project(self):
        """
        Handle request to create a new project.

        A new project clears the current project, so the user has to
        respond to a warning. If the user confirms the creation of the project,
        the unit_cells dictionary is cleared, the project_path is set to None,
        and a request is set to reset all the models to the pristine state.
        """
        self.update_status("Creating new project...")
        reply = QMessageBox.question(
            self.main_window,
            "Start New Project?",
            """⚠️  This will clear your current project.\n\n
            Are you sure you want to continue?""",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.models["unit_cells"].clear()
            self.models["project_path"] = None
            self.project_refresh_requested.emit()

    @Slot()
    def _handle_open_project(self):
        """
        Handle request to open a project from a JSON file.

        Opening a project clears the current project.
        The JSON data from the loaded file is deserialized so that the
        unit_cell dictionary can be filled. The project path is updated
        and a request is sent out to reset all other models
        to the pristine state (nothing selected).
        """
        self.update_status("Opening project...")

        # Open a file dialog for selecting a JSON file
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Unit Cells JSON",
            os.getcwd(),  # starting directory
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_string = f.read()
                unit_cells = deserialize_unit_cells(json_string)
                self.models["unit_cells"].clear()
                self.models["unit_cells"].update(unit_cells)
                self.models["project_path"] = file_path
                self.project_refresh_requested.emit()
            except Exception as e:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    f"Failed to open file:\n{str(e)}",
                )
                self.update_status("Failed to open project.")

    @Slot()
    def _handle_import_project(self):
        """
        Handle request to import a project.

        Importing a project is similar to loading with the difference being
        that the imported unit cells are added to the current project
        rather than replacing them.
        To avoid UUID clashes (if one imports the same project twice),
        the newly-imported unit cells have their UUID's regenerated.
        """
        self.update_status("Importing project...")

        # Open a file dialog for selecting a JSON file
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Unit Cells JSON",
            os.getcwd(),  # starting directory
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_string = f.read()
                unit_cells = deserialize_unit_cells(json_string)

                # Go over the imported unit cells and regenerate their UUID's
                new_unit_cells = {}
                for _, uc in unit_cells.items():
                    new_id = uuid.uuid4()
                    uc.id = new_id
                    new_unit_cells[new_id] = uc

                self.models["unit_cells"].update(new_unit_cells)
                self.project_refresh_requested.emit()
                print(self.models["unit_cells"])
            except Exception as e:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    f"Failed to open file:\n{str(e)}",
                )
                self.update_status("Failed to open project.")

    @Slot()
    def _handle_save_project(self, use_existing_path=True):
        """
        Handle request to save the current project.

        Save the current project to a JSON file. If the project already has
        a path, depending on whether the user clicks on Save or Save As,
        the project is either saved to that path or the user chooses a
        new file name. If there is no path, Save acts as Save As.
        """
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
        """
        Handle wireframe toggle.

        Request a redrawing of the unit cell plot with/without the wireframe.
        """
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
