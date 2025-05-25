from PySide6.QtWidgets import QToolBar, QWidget, QLabel, QSpinBox, QHBoxLayout

from ui.actions.action_manager import ActionManager


class MainToolbarView(QToolBar):
    """
    Main toolbar view that contains application-wide actions.

    This class is a view component that provides a toolbar with common actions
    such as creating new unit cells, saving/loading projects, and accessing
    computation options.

    It does not create actions itself, receiving them from an action manager.
    """

    def __init__(self):
        """Initialize the main toolbar without actions."""
        super().__init__("Main Toolbar")

        # Allow the toolbar to be moved by the user
        self.setMovable(True)

    def set_actions(self, action_manager: ActionManager):
        """
        Set actions from the action manager to the toolbar.

        Args:
            action_manager: ActionManager instance containing all actions
        """
        # Add File actions
        self.addAction(action_manager.file_actions["new_project"])
        self.addAction(action_manager.file_actions["open_project"])
        self.addAction(action_manager.file_actions["import_project"])
        self.addAction(action_manager.file_actions["save_project"])

        self.addSeparator()

        self.addAction(action_manager.undo_redo_actions["undo"])
        self.addAction(action_manager.undo_redo_actions["redo"])

        self.addSeparator()

        self.addAction(action_manager.unit_cell_actions["wireframe"])
        # Add the grouped spinboxes
        self.addWidget(self._create_uc_spinbox_group())

    def _create_uc_spinbox_group(self):
        """
        Create a grouped widget containing spinboxes for unit cell repetitions.
        """
        group_widget = QWidget()
        layout = QHBoxLayout(group_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove padding to fit nicely
        layout.setSpacing(5)  # Small spacing between spinboxes and labels

        self.n1_spinbox = QSpinBox()
        self.n2_spinbox = QSpinBox()
        self.n3_spinbox = QSpinBox()

        for ii, spinbox in enumerate(
            [self.n1_spinbox, self.n2_spinbox, self.n3_spinbox]
        ):
            spinbox.setRange(1, 10)
            spinbox.setFixedWidth(50)
            spinbox.setToolTip(f"Along v<sub>{ii+1}</sub>")
            spinbox.setStatusTip("Number of unit cells")
            spinbox.setEnabled(False)

        layout.addWidget(QLabel("n<sub>1</sub>:"))
        # layout.addWidget(QLabel("n\u2081:"))
        layout.addWidget(self.n1_spinbox)
        layout.addWidget(QLabel("n<sub>2</sub>:"))
        # layout.addWidget(QLabel("n\u2082:"))
        layout.addWidget(self.n2_spinbox)
        layout.addWidget(QLabel("n<sub>3</sub>:"))
        # layout.addWidget(QLabel("n\u2083:"))
        layout.addWidget(self.n3_spinbox)

        return group_widget
