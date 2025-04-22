from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QGridLayout,
    QSizePolicy,
    QFrame,
    QScrollArea,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
)
from PySide6.QtCore import Qt, Signal
import numpy as np

from models.data_models import DataModel
import uuid


class HoppingMatrix(QWidget):
    """
    A grid of buttons representing possible hopping connections between quantum states.

    Each button in the grid represents a possible hopping between two states.
    The rows represent the destination states and columns represent the source states.
    Buttons are colored differently based on whether a hopping exists or not.
    """

    # Signal emitted when a button is clicked, carrying the source and destination state info
    # Params: (source_state_info, destination_state_info) where each is (site_name, state_name, state_id)
    button_clicked = Signal(object, object)

    # Signal emitted when couplings are modified from right-clicking on the button grid.
    # The signal triggers a table and matrix update
    hoppings_changed = Signal()

    # Button style constants
    BUTTON_STYLE_DEFAULT = """
        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #aaaaaa;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
            border: 1px solid #777777;
        }
    """

    BUTTON_STYLE_HAS_HOPPING = """
        QPushButton {
            background-color: #56b4e9;
            border: 1px solid #0072b2;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #50a7d9;
            border: 1px solid #015a8c;
        }
    """
    BUTTON_STYLE_NONHERMITIAN = """
        QPushButton {
            background-color: #cc79a7;
            border: 1px solid #d55c00;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #b86593;
            border: 1px solid #b34e02;
        }
    """

    def __init__(self, hopping_data):
        super().__init__()
        # Store tuples of (site_name, state_name, state_id).
        # We do NOT need the complete state structure here
        self.states = []
        self.hopping_data = hopping_data
        # Keep all the grid buttons as we will change their appearance based on the coupling
        self.buttons = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

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

    hoppings_saved = Signal()

    def __init__(self):
        super().__init__()

        #         self.state_coupling = []
        layout = QVBoxLayout(self)

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
    Widget for displaying and editing hopping terms between states in a unit cell.
    Displays a grid of buttons, where each button corresponds to a pair of states.
    """

    def __init__(self, unit_cells, selection, hopping_data, pair_selection):
        super().__init__()
        # All unit cells
        self.unit_cells = unit_cells
        self.selection = selection
        self.hopping_data = hopping_data
        self.pair_selection = pair_selection

        # # Initialize the panels
        self.matrix = HoppingMatrix(self.hopping_data)
        self.table = HoppingTable()

        # Main layout
        layout = QVBoxLayout(self)

        # Components
        self.info_label = QLabel("Select a unit cell with states")
        self.info_label.setAlignment(Qt.AlignCenter)

        self.table_info_label = QLabel("Select a pair of states")
        self.table_info_label.setAlignment(Qt.AlignCenter)

        # Main Panel
        self.panel = QWidget()
        panel_layout = QVBoxLayout(self.panel)

        self.table_stack = QStackedWidget()
        self.table_stack.addWidget(self.table_info_label)
        self.table_stack.addWidget(self.table)

        panel_layout.addWidget(self.matrix, stretch=1)
        panel_layout.addWidget(self.table_stack, stretch=1)

        # A stack that hides the main panel if no unit cell is selected/unit cell has no states
        self.panel_stack = QStackedWidget()
        self.panel_stack.addWidget(self.info_label)
        self.panel_stack.addWidget(self.panel)
        layout.addWidget(self.panel_stack)
