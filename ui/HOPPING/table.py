from PySide6.QtWidgets import (
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QTableWidget,
)
from PySide6.QtCore import Qt


class HoppingTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # self.label = QLabel("Table Goes here")
        # self.label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(self.label)

        title_label = QLabel("Hopping Terms")
        title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Table for hopping details
        self.hopping_table = QTableWidget(0, 4)  # 4 columns: d1, d2, d3, amplitude
        self.hopping_table.setHorizontalHeaderLabels(["d₁", "d₂", "d₃", "Amplitude"])
        self.hopping_table.setColumnWidth(0, 40)  # d₁
        self.hopping_table.setColumnWidth(1, 40)  # d₂
        self.hopping_table.setColumnWidth(2, 40)  # d₃

        layout.addWidget(title_label)
        layout.addWidget(self.hopping_table)


# Container for matrix and table
# self.main_panel = QWidget()
# main_layout = QHBoxLayout(self.main_panel)


#     # --- Hopping Details Panel ---
#     self.details_panel = QWidget()
#     details_layout = QVBoxLayout(self.details_panel)

#     self.details_label = QLabel("Select a cell to edit hopping parameters")
#     details_layout.addWidget(self.details_label)

#     # Table manipulation buttons at the top
#     table_buttons_layout = QHBoxLayout()

#     self.add_row_btn = QPushButton("Add")
#     self.add_row_btn.clicked.connect(self.add_empty_row)
#     table_buttons_layout.addWidget(self.add_row_btn)

#     self.remove_row_btn = QPushButton("Remove")
#     self.remove_row_btn.clicked.connect(self.remove_selected_hopping)
#     table_buttons_layout.addWidget(self.remove_row_btn)

#     details_layout.addLayout(table_buttons_layout)


#     # Make the table columns resize to content
#     self.hopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

#     # Enable editing in the table
#     self.hopping_table.setEditTriggers(
#         QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed
#     )
#     self.hopping_table.cellChanged.connect(self.on_table_cell_changed)

#     details_layout.addWidget(self.hopping_table, stretch=1)

#     # Add both panels to container
#     container_layout.addWidget(self.matrix_panel, 1)
#     container_layout.addWidget(self.details_panel, 1)

#     main_layout.addWidget(self.content_container)

#     # Initially hide the content container
#     self.content_container.setVisible(False)

#     # Current selection
#     self.selected_state1 = None
#     self.selected_state2 = None
