from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt
import numpy as np


class IntegerTableItem(QTableWidgetItem):
    """
    Custom QTableWidgetItem that enforces integer values.
    
    Displays integers centered in the cell and ensures that any text entered
    by the user is converted to an integer. If conversion fails, defaults to 0.
    """
    def __init__(self, value=0):
        super().__init__(str(value))
        self.setTextAlignment(Qt.AlignCenter)
    
    def data(self, role):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            try:
                return int(self.text())
            except ValueError:
                return 0
        return super().data(role)


class FloatTableItem(QTableWidgetItem):
    """
    Custom QTableWidgetItem that enforces floating-point values.
    
    Displays floats centered in the cell and ensures that any text entered
    by the user is converted to a float. If conversion fails, defaults to 0.0.
    """
    def __init__(self, value=0.0):
        super().__init__(str(value))
        self.setTextAlignment(Qt.AlignCenter)
    
    def data(self, role):
        if role == Qt.EditRole or role == Qt.DisplayRole:
            try:
                return float(self.text())
            except ValueError:
                return 0.0
        return super().data(role)


class HoppingTable(QWidget):
    """
    Table widget for editing hopping parameters between quantum states.
    
    Allows adding, removing, and editing hopping terms with displacement vectors (d₁,d₂,d₃)
    and complex amplitudes (real and imaginary parts). Uses custom table items to enforce
    proper data types (integer for displacements, float for amplitudes).
    """

    def __init__(self):
        super().__init__()
        self.state_coupling = []
        layout = QVBoxLayout(self)

        self.table_title = QLabel("")
        self.table_title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Table manipulation buttons at the top
        table_buttons_layout = QHBoxLayout()

        self.add_row_btn = QPushButton("Add")
        self.remove_row_btn = QPushButton("Remove")
        self.save_btn = QPushButton("Save")

        self.add_row_btn.clicked.connect(self.add_empty_row)
        self.remove_row_btn.clicked.connect(self.remove_selected_coupling)

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

    def set_state_coupling(self, state_coupling):
        """Setter for hoppings that also refreshes the table"""
        self.state_coupling = state_coupling
        self.refresh_table()

    def refresh_table(self):
        """Clear the table and repopulate it with the latest hopping terms"""
        self.hopping_table.setRowCount(0)  # Clear existing data

        for (d1, d2, d3), amplitude in self.state_coupling:
            row_index = self.hopping_table.rowCount()
            self.hopping_table.insertRow(row_index)

            self.hopping_table.setItem(row_index, 0, IntegerTableItem(d1))
            self.hopping_table.setItem(row_index, 1, IntegerTableItem(d2))
            self.hopping_table.setItem(row_index, 2, IntegerTableItem(d3))
            self.hopping_table.setItem(
                row_index, 3, FloatTableItem(np.real(amplitude))
            )
            self.hopping_table.setItem(
                row_index, 4, FloatTableItem(np.imag(amplitude))
            )

    def add_empty_row(self):
        """Add a new empty row to the table"""
        row_index = self.hopping_table.rowCount()
        self.hopping_table.insertRow(row_index)

        # Pre-fill with default values
        self.hopping_table.setItem(row_index, 0, IntegerTableItem(0))
        self.hopping_table.setItem(row_index, 1, IntegerTableItem(0))
        self.hopping_table.setItem(row_index, 2, IntegerTableItem(0))
        self.hopping_table.setItem(row_index, 3, FloatTableItem(0.0))
        self.hopping_table.setItem(row_index, 4, FloatTableItem(0.0))

    def remove_selected_coupling(self):
        """Remove selected row(s) from the table"""
        selected_rows = set(item.row() for item in self.hopping_table.selectedItems())

        for row in sorted(selected_rows, reverse=True):
            self.hopping_table.removeRow(row)
