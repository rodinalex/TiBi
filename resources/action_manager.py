import os

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon

basedir = os.path.dirname(__file__)


class ActionManager(QObject):
    """
    Central manager for application actions.

    This class manages the creation and organization of all application
    actions, allowing them to be shared between menu bars, toolbars,
    context menus, and keyboard shortcuts.

    It follows the manager pattern where a single class is responsible for
    creating and maintaining a collection of related objects.
    """

    def __init__(self, parent=None):
        """
        Initialize the action manager with groups of actions.

        Args:
            parent: Parent QObject (typically the main window or
            app controller)
        """
        super().__init__(parent)

        # Initialize action dictionaries for different categories
        self.file_actions: dict[str, QAction] = {}
        self.undo_redo_actions: dict[str, QAction] = {}
        self.view_actions: dict[str, QAction] = {}
        self.computation_actions: dict[str, QAction] = {}
        self.help_actions: dict[str, QAction] = {}
        self.unit_cell_actions: dict[str, QAction] = {}

        # Create all actions
        self._create_file_actions()
        self._create_undo_redo_actions()
        self._create_unit_cell_actions()

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

    def _create_undo_redo_actions(self):
        self.undo_redo_actions["undo"] = QAction(
            QIcon(os.path.join(basedir, "icons/undo.png")), "Undo", self
        )
        self.undo_redo_actions["undo"].setStatusTip("Undo")

        self.undo_redo_actions["redo"] = QAction(
            QIcon(os.path.join(basedir, "icons/redo.png")), "Redo", self
        )
        self.undo_redo_actions["redo"].setStatusTip("Redo")

        # # Optional: Disable/enable based on stack state
        # self.undo_redo_actions["undo"].setEnabled(self.undo_stack.canUndo())
        # self.undo_redo_actions["redo"].setEnabled(self.undo_stack.canRedo())

        # # Keep them updated as the stack changes
        # self.undo_stack.canUndoChanged.connect(
        #     self.undo_redo_actions["undo"].setEnabled
        # )
        # self.undo_stack.canRedoChanged.connect(
        #     self.undo_redo_actions["redo"].setEnabled
        # )

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
        # Connect undo/redo actions
        for action_name, action in self.undo_redo_actions.items():
            if action_name in handlers:
                action.triggered.connect(handlers[action_name])
        # Connect unit cell actions
        for action_name, action in self.unit_cell_actions.items():
            if action_name in handlers:
                action.triggered.connect(handlers[action_name])
