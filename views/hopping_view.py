from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from .panels import HoppingMatrix, HoppingTable


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
