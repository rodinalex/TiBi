import os

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon

basedir = os.path.dirname(__file__)


class ActionManager(QObject):
    """
    Central manager for application actions.

    This class manages the creation and organization of all application actions,
    allowing them to be shared between menu bars, toolbars, context menus, and
    keyboard shortcuts.

    It follows the manager pattern where a single class is responsible for
    creating and maintaining a collection of related objects (in this case, actions).
    """

    def __init__(self, parent=None):
        """
        Initialize the action manager with groups of actions.

        Args:
            parent: Parent QObject (typically the main window or app controller)
        """
        super().__init__(parent)

        # Initialize action dictionaries for different categories
        self.file_actions = {}
        self.edit_actions = {}
        self.view_actions = {}
        self.computation_actions = {}
        self.help_actions = {}
        self.unit_cell_actions = {}

        # Create all actions
        self._create_file_actions()
        self._create_unit_cell_actions()

    #     self._create_edit_actions()
    #     self._create_view_actions()
    #     self._create_computation_actions()
    #     self._create_help_actions()

    def _create_file_actions(self):
        """Create actions related to file operations."""
        # New Unit Cell action
        self.file_actions["new_project"] = QAction(
            QIcon(os.path.join(basedir, "icons/file.png")), "New Project", self
        )
        self.file_actions["new_project"].setStatusTip("Create a new project")

        # Save Project action
        self.file_actions["save_project"] = QAction(
            QIcon(os.path.join(basedir, "icons/save.png")),
            "Save Project",
            self,
        )
        self.file_actions["save_project"].setStatusTip(
            "Save the current project"
        )

        # Save As action
        self.file_actions["save_project_as"] = QAction(
            "Save Project As...", self
        )
        self.file_actions["save_project_as"].setStatusTip(
            "Save the current project to a new file"
        )

        # Open Project action
        self.file_actions["open_project"] = QAction(
            QIcon(os.path.join(basedir, "icons/open.png")),
            "Open Project...",
            self,
        )
        self.file_actions["open_project"].setStatusTip(
            "Open an existing project"
        )

        # Import action
        self.file_actions["import_project"] = QAction(
            QIcon(os.path.join(basedir, "icons/import.png")), "Import...", self
        )
        self.file_actions["import_project"].setStatusTip(
            "Import data from an exiting project"
        )

    def _create_unit_cell_actions(self):
        """Create actions for unit cell visualization."""
        # Toggle wireframe action
        self.unit_cell_actions["wireframe"] = QAction(
            QIcon(os.path.join(basedir, "icons/box.png")),
            "Toggle wireframe",
            self,
        )
        self.unit_cell_actions["wireframe"].setCheckable(True)
        self.unit_cell_actions["wireframe"].setStatusTip(
            "Show/hide unit cell wireframe"
        )

    def connect_signals(self, handlers):
        """
        Connect actions to their handlers.

        Args:
            handlers: Dictionary mapping action names to handler functions
        """
        # Connect file actions
        for action_name, action in self.file_actions.items():
            if action_name in handlers:
                action.triggered.connect(handlers[action_name])

        # Connect unit cell actions
        for action_name, action in self.unit_cell_actions.items():
            if action_name in handlers:
                action.triggered.connect(handlers[action_name])

    #     # Connect edit actions
    #     for action_name, action in self.edit_actions.items():
    #         if action_name in handlers:
    #             action.triggered.connect(handlers[action_name])

    #     # Connect view actions
    #     for action_name, action in self.view_actions.items():
    #         if action_name in handlers:
    #             action.triggered.connect(handlers[action_name])

    #     # Connect computation actions
    #     for action_name, action in self.computation_actions.items():
    #         if action_name in handlers:
    #             action.triggered.connect(handlers[action_name])

    #     # Connect help actions
    #     for action_name, action in self.help_actions.items():
    #         if action_name in handlers:
    #             action.triggered.connect(handlers[action_name])

    # # Export action
    # self.file_actions["export"] = QAction("Export...", self)
    # self.file_actions["export"].setStatusTip("Export data to file")

    # # Quit action
    # self.file_actions["quit"] = QAction("Quit", self)
    # self.file_actions["quit"].setStatusTip("Quit the application")

    # def _create_edit_actions(self):
    #     """Create actions related to editing operations."""
    #     # Cut action
    #     self.edit_actions["cut"] = QAction("Cut", self)
    #     self.edit_actions["cut"].setStatusTip("Cut the selected item")

    #     # Copy action
    #     self.edit_actions["copy"] = QAction("Copy", self)
    #     self.edit_actions["copy"].setStatusTip("Copy the selected item")

    #     # Paste action
    #     self.edit_actions["paste"] = QAction("Paste", self)
    #     self.edit_actions["paste"].setStatusTip("Paste from clipboard")

    #     # Preferences action
    #     self.edit_actions["preferences"] = QAction("Preferences", self)
    #     self.edit_actions["preferences"].setStatusTip("Application preferences")

    # def _create_view_actions(self):
    #     """Create actions related to view operations."""
    #     # Show Toolbar action
    #     self.view_actions["show_toolbar"] = QAction("Show Toolbar", self)
    #     self.view_actions["show_toolbar"].setCheckable(True)
    #     self.view_actions["show_toolbar"].setChecked(True)
    #     self.view_actions["show_toolbar"].setStatusTip("Show or hide the toolbar")

    #     # Show Status Bar action
    #     self.view_actions["show_statusbar"] = QAction("Show Status Bar", self)
    #     self.view_actions["show_statusbar"].setCheckable(True)
    #     self.view_actions["show_statusbar"].setChecked(True)
    #     self.view_actions["show_statusbar"].setStatusTip("Show or hide the status bar")

    # def _create_computation_actions(self):
    #     """Create actions related to computation operations."""
    #     # Compute Bands action
    #     self.computation_actions["compute_bands"] = QAction(
    #         "Compute Band Structure", self
    #     )
    #     self.computation_actions["compute_bands"].setStatusTip(
    #         "Calculate electronic band structure"
    #     )

    #     # Compute DOS action
    #     self.computation_actions["compute_dos"] = QAction(
    #         "Compute Density of States", self
    #     )
    #     self.computation_actions["compute_dos"].setStatusTip(
    #         "Calculate density of states"
    #     )

    # def _create_help_actions(self):
    #     """Create actions related to help and about."""
    #     # About action
    #     self.help_actions["about"] = QAction("About", self)
    #     self.help_actions["about"].setStatusTip("About TiBi")

    #     # Help action
    #     self.help_actions["help"] = QAction("Help Contents", self)
    #     self.help_actions["help"].setStatusTip("View help contents")
