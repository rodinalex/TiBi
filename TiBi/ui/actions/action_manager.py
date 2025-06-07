import os
from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon, QUndoStack

basedir = os.path.dirname(__file__)


class ActionManager(QObject):
    """
    Central manager for application actions.

    This class manages the creation and organization of all application
    actions, allowing them to be shared between menu bars, toolbars,
    context menus, and keyboard shortcuts.

    Attributes
    ----------
    undo_stack : QUndoStack
        Application-wide undo stack
    file_actions : dict[str, QAction]
        Actions pertinent to new project reset, saving, and loading
    undo_redo_actions : dict[str, QAction]
        Undo and Redo actions
    unit_cell_actions : dict[str, QAction]
        Actions to control the unit cell visualization
        (toggling the unit cell wireframe on/off and )
    """

    def __init__(self, undo_stack: QUndoStack, parent=None):
        """
        Initialize the action manager with groups of actions.


        Parameters
        ----------
        undo_stack : QUndoStack
            Application-wide undo stack
        parent  : QObject
            Parent QObject; in this case, its MainUIController
        """
        super().__init__(parent)
        self.undo_stack = undo_stack
        # Initialize action dictionaries for different categories
        self.file_actions: dict[str, QAction] = {}
        self.undo_redo_actions: dict[str, QAction] = {}
        # self.view_actions: dict[str, QAction] = {}
        # self.computation_actions: dict[str, QAction] = {}
        # self.help_actions: dict[str, QAction] = {}
        self.unit_cell_actions: dict[str, QAction] = {}

        # Create all actions
        self._create_file_actions()
        self._create_undo_redo_actions()
        self._create_unit_cell_actions()

    def _create_file_actions(self):
        """Create actions related to file operations."""
        # New Unit Cell action
        self.file_actions["new_project"] = QAction(
            QIcon(os.path.join(basedir, "../../assets/icons/file.png")),
            "New Project",
            self,
        )
        self.file_actions["new_project"].setStatusTip("Create a new project")

        # Save Project action
        self.file_actions["save_project"] = QAction(
            QIcon(os.path.join(basedir, "../../assets/icons/save.png")),
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
            QIcon(os.path.join(basedir, "../../assets/icons/open.png")),
            "Open Project...",
            self,
        )
        self.file_actions["open_project"].setStatusTip(
            "Open an existing project"
        )

        # Import action
        self.file_actions["import_project"] = QAction(
            QIcon(os.path.join(basedir, "../../assets/icons/import.png")),
            "Import...",
            self,
        )
        self.file_actions["import_project"].setStatusTip(
            "Import data from an exiting project"
        )

    def _create_undo_redo_actions(self):
        """Create the "forward/back" arrow undo/redo actions."""
        self.undo_redo_actions["undo"] = QAction(
            QIcon(os.path.join(basedir, "../../assets/icons/undo.png")),
            "Undo",
            self,
        )
        self.undo_redo_actions["undo"].setStatusTip("Undo")

        self.undo_redo_actions["redo"] = QAction(
            QIcon(os.path.join(basedir, "../../assets/icons/redo.png")),
            "Redo",
            self,
        )
        self.undo_redo_actions["redo"].setStatusTip("Redo")

        # Disable/enable based on stack state.
        # The actions become disabled if there is nothing to undo/redo
        self.undo_redo_actions["undo"].setEnabled(self.undo_stack.canUndo())
        self.undo_redo_actions["redo"].setEnabled(self.undo_stack.canRedo())

        # Keep the action status updated as the user performs operations
        self.undo_stack.canUndoChanged.connect(
            self.undo_redo_actions["undo"].setEnabled
        )
        self.undo_stack.canRedoChanged.connect(
            self.undo_redo_actions["redo"].setEnabled
        )

        # When an undo/redo item is pushed to the stack, we track the
        # text of the associated item
        # (provided inside the command constructors)
        # The new text is then used to construct the status bar tip
        self.undo_stack.undoTextChanged.connect(self._update_undo_tooltip)
        self.undo_stack.redoTextChanged.connect(self._update_redo_tooltip)

    def _update_undo_tooltip(self):
        if self.undo_stack.canUndo():
            self.undo_redo_actions["undo"].setStatusTip(
                f"Undo {self.undo_stack.undoText()}"
            )
        else:
            self.undo_redo_actions["undo"].setStatusTip("Nothing to undo")

    def _update_redo_tooltip(self):
        if self.undo_stack.canRedo():
            self.undo_redo_actions["redo"].setStatusTip(
                f"Redo {self.undo_stack.redoText()}"
            )
        else:
            self.undo_redo_actions["redo"].setStatusTip("Nothing to redo")

    def disconnect_undo_redo(self):
        """Disconnect the signals during the shutdown.

        This step prevents the objects deleted during the shutdown from
        being accessed
        """
        self.undo_stack.canUndoChanged.disconnect(
            self.undo_redo_actions["undo"].setEnabled
        )
        self.undo_stack.canRedoChanged.disconnect(
            self.undo_redo_actions["redo"].setEnabled
        )
        self.undo_stack.undoTextChanged.disconnect(self._update_undo_tooltip)
        self.undo_stack.redoTextChanged.disconnect(self._update_redo_tooltip)

    def _create_unit_cell_actions(self):
        """Create actions for unit cell visualization."""
        # Toggle wireframe action
        self.unit_cell_actions["wireframe"] = QAction(
            QIcon(os.path.join(basedir, "../../assets/icons/box.png")),
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

        Parameters
        ----------
        handlers
            Dictionary mapping action names to handler functions
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
