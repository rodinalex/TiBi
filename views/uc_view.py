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
    QGridLayout,
    QSpinBox,
    QFrame,
    QStyledItemDelegate,
)
from PySide6.QtGui import QStandardItemModel, QKeySequence, QShortcut
from PySide6.QtCore import Qt, Signal, QEvent
from resources.colors import CF_vermillion, CF_green, CF_sky
from resources.ui_elements import divider_line


class UnitCellPanel(QWidget):
    """
    Form panel for editing unit cell properties.

    This panel provides a form interface for editing a unit cell's properties:
    - Three basis vectors (v1, v2, v3) with x, y, z components

    The panel uses a reactive data binding approach, where UI components are
    automatically updated when the model changes, and model updates trigger
    appropriate UI refreshes.
    """

    def __init__(self):
        super().__init__()

        # Layout
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()  # For basis vector creation

        panel_header = QLabel("Unit Cell Parameters")
        panel_header.setAlignment(Qt.AlignCenter)

        basis_header = QLabel("Basis Vectors")
        basis_header.setAlignment(Qt.AlignCenter)

        dimensionality_header = QLabel("Dimensionality")
        dimensionality_header.setAlignment(Qt.AlignCenter)

        # Radio buttons
        self.radio0D = QRadioButton("0")
        self.radio1D = QRadioButton("1")
        self.radio2D = QRadioButton("2")
        self.radio3D = QRadioButton("3")

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio0D, id=0)
        self.radio_group.addButton(self.radio1D, id=1)
        self.radio_group.addButton(self.radio2D, id=2)
        self.radio_group.addButton(self.radio3D, id=3)

        # Add Site and Reduce UC buttons
        button_layout = QHBoxLayout()
        self.new_site_btn = QPushButton("+ Site")
        self.reduce_btn = QPushButton("Reduce")
        button_layout.addWidget(self.new_site_btn)
        button_layout.addWidget(self.reduce_btn)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio0D)
        radio_layout.addWidget(self.radio1D)
        radio_layout.addWidget(self.radio2D)
        radio_layout.addWidget(self.radio3D)

        layout.addWidget(panel_header)
        layout.addWidget(dimensionality_header)
        layout.addLayout(radio_layout)
        layout.addLayout(grid_layout)

        layout.addLayout(button_layout)
        grid_layout.addWidget(basis_header, 0, 1, 1, 3)

        # Function to create a row with (x, y, z) input fields
        def create_vector_column(n):
            x = QDoubleSpinBox()
            y = QDoubleSpinBox()
            z = QDoubleSpinBox()

            for coord in [x, y, z]:
                coord.setButtonSymbols(QDoubleSpinBox.NoButtons)
                coord.setRange(-1e308, 1e308)
                coord.setFixedWidth(40)
                coord.setDecimals(3)

            grid_layout.addWidget(x, 2, n)
            grid_layout.addWidget(y, 3, n)
            grid_layout.addWidget(z, 4, n)
            return (x, y, z)

        # Create vector input rows
        self.v1 = create_vector_column(1)
        self.v2 = create_vector_column(2)
        self.v3 = create_vector_column(3)

        v1_label = QLabel("v<sub>1</sub>")
        v1_label.setAlignment(Qt.AlignCenter)
        v2_label = QLabel("v<sub>2</sub>")
        v2_label.setAlignment(Qt.AlignCenter)
        v3_label = QLabel("v<sub>3</sub>")
        v3_label.setAlignment(Qt.AlignCenter)

        grid_layout.addWidget(v1_label, 1, 1)
        grid_layout.addWidget(v2_label, 1, 2)
        grid_layout.addWidget(v3_label, 1, 3)

        # Create a coordinate label row
        for ii, (text, color) in enumerate(
            zip(["x", "y", "z"], [CF_vermillion, CF_green, CF_sky]), start=1
        ):
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                f"color: rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, {color[3]});"
            )
            grid_layout.addWidget(label, 1 + ii, 0)

        grid_layout.setVerticalSpacing(2)

        # # Add spinners to control how many unit cells are shown
        # n_spinner_label = QLabel("Number of cells to show")
        # n_spinner_label.setAlignment(Qt.AlignCenter)
        # grid_layout.addWidget(n_spinner_label, 5, 1, 1, 3)
        # self.n1 = QSpinBox()
        # self.n2 = QSpinBox()
        # self.n3 = QSpinBox()
        # for ii, x in enumerate([self.n1, self.n2, self.n3]):
        #     x.setFixedWidth(40)
        #     x.setRange(1, 10)
        #     x.setEnabled(False)
        #     grid_layout.addWidget(x, 6, 1 + ii)


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

        panel_header = QLabel("Site Parameters")
        panel_header.setAlignment(Qt.AlignCenter)

        header = QLabel("Site Coordinates")
        header.setAlignment(Qt.AlignCenter)

        # Coordinate and radius fields
        self.R = QDoubleSpinBox()
        self.c1 = QDoubleSpinBox()
        self.c2 = QDoubleSpinBox()
        self.c3 = QDoubleSpinBox()

        for c in [self.R, self.c1, self.c2, self.c3]:
            c.setRange(0.0, 1.0)
            c.setDecimals(3)
            c.setButtonSymbols(QDoubleSpinBox.NoButtons)

        # Color picker button
        self.color_picker_btn = QPushButton()
        self.color_picker_btn.setFixedWidth(25)

        appearance_layout = QHBoxLayout()
        appearance_layout.addWidget(QLabel("Radius:"))
        appearance_layout.addWidget(self.R)
        appearance_layout.addWidget(QLabel("Color:"))
        appearance_layout.addWidget(self.color_picker_btn)

        # Create a grid layout with labels on top and spin boxes below
        c1_label = QLabel("c<sub>1</sub>")
        c1_label.setAlignment(Qt.AlignCenter)
        c2_label = QLabel("c<sub>2</sub>")
        c2_label.setAlignment(Qt.AlignCenter)
        c3_label = QLabel("c<sub>3</sub>")
        c3_label.setAlignment(Qt.AlignCenter)

        grid_layout = QGridLayout()
        grid_layout.addWidget(c1_label, 1, 0)
        grid_layout.addWidget(c2_label, 1, 1)
        grid_layout.addWidget(c3_label, 1, 2)

        grid_layout.addWidget(self.c1, 2, 0)
        grid_layout.addWidget(self.c2, 2, 1)
        grid_layout.addWidget(self.c3, 2, 2)
        grid_layout.setVerticalSpacing(2)

        self.new_state_btn = QPushButton("+ State")
        # self.new_state_btn.setFixedSize(60, 30)
        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(panel_header)
        layout.addLayout(appearance_layout)
        layout.addWidget(header)
        layout.addLayout(grid_layout)
        layout.addWidget(self.new_state_btn)


class EnterOnlyDelegate(QStyledItemDelegate):
    """
    A delegate that requires the user to commit changes to tree item names by pressing "Enter".
    Clicking away/defocusing resets the tree item name to its pre-edit form. The purpose is to
    handle the Qt default behavior, where defocusing keeps the new display name in the tree
    but does not send an updated signal so that the data can be updated internally.
    """

    def eventFilter(self, editor, event):
        if event.type() == QEvent.FocusOut:
            # Cancel editing on focus out
            editor.blockSignals(True)
            editor.setText(editor.property("originalText"))
            editor.blockSignals(False)
            self.closeEditor.emit(editor, QStyledItemDelegate.RevertModelCache)
            return True

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            # Accept editing on Enter
            return super().eventFilter(editor, event)

        return super().eventFilter(editor, event)

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        editor.setProperty("originalText", index.data())  # Store original value
        return editor


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

        # Set the delegate to save the data only on Enter-press
        delegate = EnterOnlyDelegate(self.tree_view)
        self.tree_view.setItemDelegate(delegate)

        button_layout = QHBoxLayout()
        self.new_uc_btn = QPushButton("+ UC")
        self.delete_btn = QPushButton("Delete")

        button_layout.addWidget(self.new_uc_btn)
        button_layout.addWidget(self.delete_btn)

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        layout.addLayout(button_layout)

        # Set up Delete shortcut
        self.delete_shortcut = QShortcut(QKeySequence("Del"), self.tree_view)
        self.delete_shortcut.activated.connect(lambda: self.delete.emit())

        # Add Backspace as an alternative shortcut
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
        # self.button_panel = ButtonPanel()

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

        top_panel = QVBoxLayout()
        top_panel.addWidget(self.tree_view_panel, stretch=4)

        # Basis vectors and fractional coordinates
        bottom_panel = QVBoxLayout()

        bottom_panel.addWidget(self.uc_stack, stretch=2)
        bottom_panel.addWidget(divider_line())
        bottom_panel.addWidget(self.site_stack, stretch=1)

        layout.setSpacing(0)

        layout.addLayout(top_panel, stretch=2)
        layout.addWidget(divider_line())
        layout.addLayout(bottom_panel)
