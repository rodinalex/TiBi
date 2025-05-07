from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class HoppingMatrix(QWidget):
    """
    A grid of buttons representing possible hopping connections between states.

    Each button in the grid represents a possible hopping between two states.
    The rows (columns) represent the destination (source) states.
    Buttons are colored differently based on whether a hopping exists or not,
    and whether the hopping is Hermitian.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable Area for Matrix
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Content widget for grid
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(3)

        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        title_label = QLabel("Coupling Matrix")
        title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(title_label)
        layout.addWidget(self.scroll_area)


class HoppingTable(QWidget):
    """
    A table containing hoppings between the selected states.

    Each row of the table describes a hopping and contains five columns.
    The first three columns provide the displacements from the origin site
    to the destination site in terms of the basis vectors. The last two
    columns are the real and imaginary parts of the hopping term, respectively.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table_title = QLabel("")
        self.table_title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Table manipulation buttons at the top
        table_buttons_layout = QHBoxLayout()

        self.add_row_btn = QPushButton("Add")
        self.remove_row_btn = QPushButton("Remove")
        self.save_btn = QPushButton("Save")

        table_buttons_layout.addWidget(self.add_row_btn)
        table_buttons_layout.addWidget(self.remove_row_btn)
        table_buttons_layout.addWidget(self.save_btn)

        # Table for hopping details
        self.hopping_table = QTableWidget(
            0, 5
        )  # 5 columns: d1, d2, d3, Re(amplitude), Im(amplitude)
        self.hopping_table.setHorizontalHeaderLabels(
            ["d₁", "d₂", "d₃", "Re(t)", "Im(t)"]
        )

        self.hopping_table.setColumnWidth(0, 40)  # d₁
        self.hopping_table.setColumnWidth(1, 40)  # d₂
        self.hopping_table.setColumnWidth(2, 40)  # d₃
        self.hopping_table.setColumnWidth(3, 60)  # Real amplitude part
        self.hopping_table.setColumnWidth(4, 60)  # Imaginary amplitude part

        layout.addWidget(self.table_title)
        layout.addLayout(table_buttons_layout)
        layout.addWidget(self.hopping_table)


class HoppingView(QWidget):
    """
    View for editing hopping parameters between quantum states.

    This widget combines two main components:
    1. A matrix grid where each button represents a possible hopping connection
       between two states [rows (columns) are destination (target) states]
    2. A table for editing specific hopping parameters when a connection
       is selected in the matrix

    The view uses a stacked widget approach to show different panels based on
    the current selection state (no unit cell, no states, or states selected).

    This component follows the MVC pattern and doesn't contain business logic.
    Instead, it provides UI elements that the controller can connect to
    and manipulate.
    """

    def __init__(self):
        super().__init__()

        # Initialize the panels
        self.matrix_panel = HoppingMatrix()
        self.table_panel = HoppingTable()

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        # Components
        self.info_label = QLabel("Select a Unit Cell with States")
        self.info_label.setAlignment(Qt.AlignCenter)

        self.table_info_label = QLabel("Select a matrix element to edit")
        self.table_info_label.setAlignment(Qt.AlignCenter)

        # Main Panel
        self.panel = QWidget()
        panel_layout = QVBoxLayout(self.panel)

        # A stack that hides the table if no state pair is selected
        self.table_stack = QStackedWidget()
        self.table_stack.addWidget(self.table_info_label)
        self.table_stack.addWidget(self.table_panel)

        panel_layout.addWidget(self.matrix_panel, stretch=3)
        panel_layout.addWidget(self.table_stack, stretch=2)

        # A stack that hides the main panel if no unit cell is selected or
        # the selected unit cell has no states
        self.panel_stack = QStackedWidget()
        self.panel_stack.addWidget(self.info_label)
        self.panel_stack.addWidget(self.panel)
        layout.addWidget(self.panel_stack)
