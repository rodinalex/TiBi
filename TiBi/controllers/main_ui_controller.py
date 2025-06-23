from functools import partial
import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QFileDialog, QMessageBox
import uuid

from TiBi.logic.serialization.serialization import (
    serialize_unit_cells,
    deserialize_unit_cells,
)
from TiBi.models import Selection, UnitCell
from TiBi.ui.actions import ActionManager
from TiBi.views.menu_bar_view import MenuBarView
from TiBi.views.main_toolbar_view import MainToolbarView
from TiBi.views.main_window import MainWindow
from TiBi.views.status_bar_view import StatusBarView


class MainUIController(QObject):
    """
    Controller for the main UI components (menu bar, toolbar, status bar).

    This controller connects the UI elements to the application logic and
    manages the action manager that provides shared actions to the menu
    bar and toolbar.

    Attributes
    ----------
    project_path : str | None
        The file to which the dictionary containing the unit
        cell objects is saved
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
    main_window : MainWindow
        Subclass of QMainWindow containing the application's main view
    menu_bar_view : MenuBarView
        Standard menu bar
    toolbar_view : MainToolbarView
        Toolbar at the top of the application window
    status_bar_view : StatusBarView
        Status bar at the bottom of the application window
    undo_stack : QUndoStack
        Stack for 'undo-able' actions
    project_refresh_requested : Signal
        Request to refresh the project view after loading or creating a new one
    unit_cell_update_requested : Signal
        Request to update the unit cell plot with new parameters

    Methods
    -------
    get_uc_plot_properties()
        Get the unit cell visualization properties.
    set_spinbox_status()
        Activate/deactivate unit cell spinboxes.
    update_status(message : str)
        Display a message in the status bar.
    """

    unit_cell_update_requested = Signal()
    # Requst an updated unit cell plot
    # Request a UI refresh after creating a new project
    # or loading an existing one
    project_refresh_requested = Signal()

    def __init__(
        self,
        project_path: str | None,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        main_window: MainWindow,
        menu_bar_view: MenuBarView,
        toolbar_view: MainToolbarView,
        status_bar_view: StatusBarView,
        undo_stack: QUndoStack,
    ):
        super().__init__()
        self.project_path = project_path
        self.unit_cells = unit_cells
        self.selection = selection
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

        # Connect spinbox signals
        self.toolbar.n1_spinbox.valueChanged.connect(
            lambda _: self.unit_cell_update_requested.emit()
        )
        self.toolbar.n2_spinbox.valueChanged.connect(
            lambda _: self.unit_cell_update_requested.emit()
        )
        self.toolbar.n3_spinbox.valueChanged.connect(
            lambda _: self.unit_cell_update_requested.emit()
        )

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

    # Methods to get information about the current state
    def get_uc_plot_properties(self):
        """
        Get the unit cell visualization properties.

        The function returns the number of unit cells to be plotted
        along each basis vector, as well as whether the wireframe
        is plotted.

        Returns
        -------
        int, int, int, bool
            Numbers of unit cells along each of the three vectors and
            a boolean for the wireframe.
        """
        n1, n2, n3 = [
            spinbox.value() if spinbox.isEnabled() else 1
            for spinbox in (
                self.toolbar.n1_spinbox,
                self.toolbar.n2_spinbox,
                self.toolbar.n3_spinbox,
            )
        ]
        wireframe_enabled = self.action_manager.unit_cell_actions[
            "wireframe"
        ].isChecked()
        return n1, n2, n3, wireframe_enabled

    def set_spinbox_status(self, n1_enabled, n2_enabled, n3_enabled):
        """Activate/deactivate the unit cell spinboxes"""
        self.toolbar.n1_spinbox.setEnabled(n1_enabled)
        self.toolbar.n2_spinbox.setEnabled(n2_enabled)
        self.toolbar.n3_spinbox.setEnabled(n3_enabled)

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
            self.project_path = None
            self.unit_cells.clear()
            self.undo_stack.clear()
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
                self.unit_cells.clear()
                self.unit_cells.update(unit_cells)
                self.project_path = file_path
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

                self.unit_cells.update(new_unit_cells)
                self.project_refresh_requested.emit()
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
        json_string = serialize_unit_cells(self.unit_cells)
        if use_existing_path:
            file_path = self.project_path
        else:
            file_path = None

        # If there is no path, open a dialog for the user to pick it
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
            self.project_path = file_path

    @Slot()
    def _handle_wireframe_toggle(self):
        """
        Handle wireframe toggle.

        Request a redrawing of the unit cell plot with/without the wireframe.
        """
        # Implementation will be added later
        self.unit_cell_update_requested.emit()

    # Methods to be called from other controllers
    def update_status(self, message):
        """
        Display a message in the status bar.

        Parameters
        ----------
        message : str
            Message to display
        """
        self.status_bar.update_status(message)
