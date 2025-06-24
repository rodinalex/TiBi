from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .panels import SitePanel, TreeViewPanel, UnitCellPanel
from TiBi.ui import divider_line


class UnitCellView(QWidget):
    """
    Main UI component for managing unit cells, sites, and states.

    This widget combines a tree view of the unit cell hierarchy with
    dynamically swappable panels for editing properties of the selected
    tree node. It handles the data models and coordinates interactions
    between the tree view and detail panels.

    The UI consists of several main parts:

    1. Tree view panel showing the hierarchy of unit cells, sites, and states
    2. Button panel with actions for creating, deleting, and modifying items
    3. Form panels that change depending on what is selected in the tree
    4. Dimensionality controls for setting periodic boundary conditions

    Attributes
    ----------
    unit_cell_panel : UnitCellPanel
        Panel for editing `UnitCell` properties.
    site_panel : SitePanel
        Panel for editing `Site` properties.
    tree_view_panel : TreeViewPanel
        Panel displaying the tree view of `UnitCell`s, `Site`s, and `State`s.
    """

    def __init__(self):
        super().__init__()
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        # Initialize UI panels
        self.unit_cell_panel = UnitCellPanel()
        self.site_panel = SitePanel()
        self.tree_view_panel = TreeViewPanel()

        # Info labels
        self.uc_info_label = QLabel("Add/Select a Unit Cell")
        self.uc_info_label.setAlignment(Qt.AlignCenter)

        self.site_info_label = QLabel("Add/Select a Site")
        self.site_info_label.setAlignment(Qt.AlignCenter)

        # Panel stacks
        self.uc_stack = QStackedWidget()
        self.uc_stack.addWidget(self.uc_info_label)
        self.uc_stack.addWidget(self.unit_cell_panel)

        self.site_stack = QStackedWidget()
        self.site_stack.addWidget(self.site_info_label)
        self.site_stack.addWidget(self.site_panel)

        # Create the interface
        # Top panel contains the tree view
        top_panel = QVBoxLayout()
        top_panel.addWidget(self.tree_view_panel)

        # Bottom panel contains the unit cell/state editable fields
        bottom_panel = QVBoxLayout()
        bottom_panel.addWidget(self.uc_stack)
        bottom_panel.addWidget(divider_line())
        bottom_panel.addWidget(self.site_stack)

        layout.setSpacing(0)

        layout.addLayout(top_panel)
        layout.addWidget(divider_line())
        layout.addLayout(bottom_panel)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)
