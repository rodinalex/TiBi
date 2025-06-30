from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFontMetrics, QIcon
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
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from TiBi.ui.utilities import get_resource_path, set_button_size


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
        title_label.setProperty("style", "bold")
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

        # Table manipulation buttons on the right
        table_buttons_layout = QVBoxLayout()

        self.add_row_btn = QPushButton()
        self.add_row_btn.setIcon(
            QIcon(str(get_resource_path("assets/icons/plus_hopping.svg")))
        )
        self.add_row_btn.setToolTip("New Hopping")
        self.add_row_btn.setStatusTip("Add a new hopping integral.")

        self.remove_row_btn = QPushButton()
        self.remove_row_btn.setIcon(
            QIcon(str(get_resource_path("assets/icons/trash_hopping.svg")))
        )
        self.remove_row_btn.setToolTip("Delete Hopping")
        self.remove_row_btn.setStatusTip(
            "Delete the selected hopping integral."
        )

        self.save_btn = QPushButton()
        self.save_btn.setIcon(
            QIcon(str(get_resource_path("assets/icons/save_hopping.svg")))
        )
        self.save_btn.setToolTip("Save Hoppings")
        self.save_btn.setStatusTip("Save the Hopping table.")

        table_buttons_layout.addWidget(self.add_row_btn)
        table_buttons_layout.addWidget(self.remove_row_btn)
        table_buttons_layout.addWidget(self.save_btn)

        # Table for hopping details
        self.hopping_table = QTableWidget(
            0, 5
        )  # 5 columns: d1, d2, d3, Re(amplitude), Im(amplitude)

        headers = ["d₁", "d₂", "d₃", "Re(t)", "Im(t)"]
        tooltips = [
            "Displacement along v₁",
            "Displacement along v₂",
            "Displacement along v₃",
            "Real part",
            "Imaginary part",
        ]
        statustips = [
            "Number of v₁'s from the origin site to the destination site",
            "Number of v₂'s from the origin site to the destination site",
            "Number of v₃'s from the origin site to the destination site",
            "Real part of hopping amplitude",
            "Imaginary part of hopping amplitude",
        ]

        # Assign headers with tooltips
        for i, (label, tip, status) in enumerate(
            zip(headers, tooltips, statustips)
        ):
            item = QTableWidgetItem(label)
            item.setToolTip(tip)
            item.setStatusTip(status)
            self.hopping_table.setHorizontalHeaderItem(i, item)

        # Get font metrics for the spinbox's current font
        font_metrics = QFontMetrics(self.hopping_table.font())

        # Add some padding for margins, borders, and spin buttons
        padding = 10  # Adjust as needed

        self.hopping_table.setColumnWidth(
            0, font_metrics.horizontalAdvance("0" * 3) + padding
        )  # d₁
        self.hopping_table.setColumnWidth(
            1, font_metrics.horizontalAdvance("0" * 3) + padding
        )  # d₂
        self.hopping_table.setColumnWidth(
            2, font_metrics.horizontalAdvance("0" * 3) + padding
        )  # d₃
        self.hopping_table.setColumnWidth(
            3, font_metrics.horizontalAdvance("0" * 6) + padding
        )  # Real amplitude part
        self.hopping_table.setColumnWidth(
            4, font_metrics.horizontalAdvance("0" * 6) + padding
        )  # Imaginary amplitude part

        # Table and buttons layout
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.hopping_table)
        control_layout.addLayout(table_buttons_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_title)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        content_height = self.table_title.sizeHint().height()
        scroll_area.setMaximumHeight(content_height + 20)

        layout.addWidget(scroll_area)
        layout.addLayout(control_layout)
        # Format the buttons
        icon_size = QSize(20, 20)
        for btn in [
            self.add_row_btn,
            self.remove_row_btn,
            self.save_btn,
        ]:
            set_button_size(btn, "compact")
            btn.setIconSize(icon_size)


class HoppingPanel(QWidget):
    """
    View for editing hopping parameters between quantum states.

    This widget combines two main components:

    1. A matrix grid where each button represents a possible hopping connection
       between two states [rows (columns) are destination (target) states]
    2. A table for editing specific hopping parameters when a connection
       is selected in the matrix

    The view uses a stacked widget approach to show different panels based on
    the current selection state (no unit cell, no states, or states selected).

    Attributes
    ----------
    matrix_panel : HoppingMatrix
        The panel displaying the hopping matrix as a grid of buttons.
    table_panel : HoppingTable
        The panel displaying the hopping parameters in a table format.
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
