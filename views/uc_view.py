from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QLabel,
    QButtonGroup,
    QRadioButton,
    QFormLayout,
    QPushButton,
    QDoubleSpinBox,
    QTreeView,
)
from PySide6.QtGui import QStandardItemModel, QKeySequence, QShortcut
from PySide6.QtCore import Qt, Signal


class ButtonPanel(QWidget):
    """
    Panel containing action buttons for the unit cell editor.

    This panel provides buttons for common operations:
    - Creating new unit cells, sites, and states
    - Deleting the currently selected item
    - Reducing the unit cell basis vectors (using the LLL algorithm)

    Buttons are automatically enabled/disabled based on the current selection state.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.new_uc_btn = QPushButton("New UC")
        self.new_site_btn = QPushButton("New Site")
        self.new_state_btn = QPushButton("New State")
        self.delete_btn = QPushButton("Delete")
        self.reduce_btn = QPushButton("Reduce UC")

        self.new_site_btn.setEnabled(False)
        self.new_state_btn.setEnabled(False)
        self.reduce_btn.setEnabled(False)

        layout.addWidget(self.new_uc_btn)
        layout.addWidget(self.new_site_btn)
        layout.addWidget(self.new_state_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.reduce_btn)


class UnitCellPanel(QWidget):
    """
    Form panel for editing unit cell properties.

    This panel provides a form interface for editing a unit cell's properties:
    - Name
    - Three basis vectors (v1, v2, v3) with x, y, z components
    - Periodicity flags for each basis vector

    The panel uses a reactive data binding approach, where UI components are
    automatically updated when the model changes, and model updates trigger
    appropriate UI refreshes.
    """

    def __init__(self):
        super().__init__()

        basis_header = QLabel("Unit Cell basis")
        basis_header.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(2)

        # Function to create a row with (x, y, z) input fields
        def create_vector_row(v):
            layout = QHBoxLayout()  # Pack x, y, and z fields horizontally
            x = QDoubleSpinBox()
            y = QDoubleSpinBox()
            z = QDoubleSpinBox()

            for coord in [x, y, z]:
                coord.setButtonSymbols(QDoubleSpinBox.NoButtons)
                coord.setRange(-1e308, 1e308)
                coord.setFixedWidth(40)
                coord.setDecimals(3)

            layout.addWidget(x)
            layout.addWidget(y)
            layout.addWidget(z)
            return layout, (x, y, z)

        # Create vector input rows
        self.v1_layout, self.v1 = create_vector_row("v1")
        self.v2_layout, self.v2 = create_vector_row("v2")
        self.v3_layout, self.v3 = create_vector_row("v3")

        form_layout.addRow("v<sub>1</sub>:", self.v1_layout)
        form_layout.addRow("v<sub>2</sub>:", self.v2_layout)
        form_layout.addRow("v<sub>3</sub>:", self.v3_layout)

        # Main layout
        layout = QVBoxLayout(self)

        layout.addWidget(basis_header)
        layout.addLayout(form_layout)


class SitePanel(QWidget):
    """
    Form panel for editing site properties.

    This panel provides a form interface for editing a site's properties:
    - Name
    - Fractional coordinates (c1, c2, c3) within the unit cell

    It uses reactive data binding to keep the UI and model in sync.
    """

    def __init__(self):
        super().__init__()

        header = QLabel("Site coordinates")
        header.setAlignment(Qt.AlignCenter)

        # Coordinate fields
        self.c1 = QDoubleSpinBox()
        self.c2 = QDoubleSpinBox()
        self.c3 = QDoubleSpinBox()

        for c in [self.c1, self.c2, self.c3]:
            c.setRange(0.0, 1.0)
            c.setSingleStep(0.01)
            c.setDecimals(3)

        # Create row layouts with labels on the left and spin boxes on the right
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(2)
        form_layout.addRow("c<sub>1</sub>:", self.c1)
        form_layout.addRow("c<sub>2</sub>:", self.c2)
        form_layout.addRow("c<sub>3</sub>:", self.c3)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(header)
        layout.addLayout(form_layout)


class TreeViewPanel(QWidget):
    """
    Tree view panel for displaying and selecting the unit cell hierarchy.

    This panel displays a hierarchical tree showing unit cells, their sites,
    and the states at each site. It handles selection events and emits signals
    when different types of nodes are selected, allowing other components to
    respond appropriately.

    The tree has three levels:
    1. Unit cells
    2. Sites within a unit cell
    3. States within a site

    Features:
    - Hierarchical display of unit cells, sites, and states
    - Single selection mode for focused editing
    - Double-click to edit names directly in the tree
    - Keyboard shortcuts for deletion (Del and Backspace)
    - Signal emission on deletion requests

    This panel is designed to work with a controller that will handle the actual
    data modifications in response to UI actions.
    """

    # Define signals
    delete = Signal()

    def __init__(self):
        super().__init__()

        # Create and configure tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setEditTriggers(QTreeView.DoubleClicked)

        # Create model
        self.tree_model = QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()

        # Set model to view
        self.tree_view.setModel(self.tree_model)

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)

        # Set up delete shortcut
        self.delete_shortcut = QShortcut(QKeySequence("Del"), self.tree_view)
        self.delete_shortcut.activated.connect(lambda: self.delete.emit())

        # Optional: Add Backspace as an alternative shortcut
        self.backspace_shortcut = QShortcut(QKeySequence("Backspace"), self.tree_view)
        self.backspace_shortcut.activated.connect(lambda: self.delete.emit())


class UnitCellView(QWidget):
    """
    Main UI component for managing unit cells, sites, and states.

    This widget combines a tree view of the unit cell hierarchy with dynamically
    swappable panels for editing properties of the selected tree node. It handles
    the data models and coordinates interactions between the tree view and detail panels.

    The UI consists of several main parts:
    1. Tree view panel showing the hierarchy of unit cells, sites, and states
    2. Button panel with actions for creating, deleting, and modifying items
    3. Form panels that change depending on what is selected in the tree
    4. Dimensionality controls for setting periodic boundary conditions

    Following the MVC pattern, this view is responsible for:
    - Displaying the UI elements and their layout
    - Providing controls for user interaction
    - Emitting signals when user actions occur

    However, it doesn't contain business logic - that's handled by the controller,
    which connects to these signals and interacts with the data models.
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Initialize UI panels
        self.unit_cell_panel = UnitCellPanel()
        self.site_panel = SitePanel()
        self.tree_view_panel = TreeViewPanel()
        self.button_panel = ButtonPanel()

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

        # Radio panel

        dimensionality_header = QLabel("Dimensionality")
        dimensionality_header.setAlignment(Qt.AlignCenter)

        # Radio buttons
        self.radio0D = QRadioButton("0D")
        self.radio1D = QRadioButton("1D")
        self.radio2D = QRadioButton("2D")
        self.radio3D = QRadioButton("3D")

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio0D, id=0)
        self.radio_group.addButton(self.radio1D, id=1)
        self.radio_group.addButton(self.radio2D, id=2)
        self.radio_group.addButton(self.radio3D, id=3)

        # Start by disabling the radio buttons
        for button in self.radio_group.buttons():
            button.setEnabled(False)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio0D)
        radio_layout.addWidget(self.radio1D)
        radio_layout.addWidget(self.radio2D)
        radio_layout.addWidget(self.radio3D)

        radio_form = QFormLayout()
        radio_form.addRow("Dimensionality:", radio_layout)

        # Create the interface

        top_panel = QHBoxLayout()
        top_panel.addWidget(self.tree_view_panel, stretch=2)
        top_panel.addWidget(self.button_panel, stretch=1)

        # Basis vectors and fractional coordinates
        bottom_panel = QHBoxLayout()

        bottom_panel.addWidget(self.uc_stack, stretch=2)
        bottom_panel.addWidget(self.site_stack, stretch=1)

        layout.setSpacing(0)

        layout.addLayout(top_panel)
        layout.addLayout(radio_form)
        layout.addLayout(bottom_panel)
