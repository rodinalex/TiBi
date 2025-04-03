from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt, Signal
import numpy as np


class HoppingTable(QWidget):

    hoppings_saved = Signal()

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
        self.hopping_table.setColumnWidth(3, 40)  # Real amplitude part
        self.hopping_table.setColumnWidth(4, 40)  # Imaginary amplitude part

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

            self.hopping_table.setItem(row_index, 0, QTableWidgetItem(str(d1)))
            self.hopping_table.setItem(row_index, 1, QTableWidgetItem(str(d2)))
            self.hopping_table.setItem(row_index, 2, QTableWidgetItem(str(d3)))
            self.hopping_table.setItem(
                row_index, 3, QTableWidgetItem(str(np.real(amplitude)))
            )
            self.hopping_table.setItem(
                row_index, 4, QTableWidgetItem(str(np.imag(amplitude)))
            )

    def add_empty_row(self):
        """Add a new empty row to the table"""
        row_index = self.hopping_table.rowCount()
        self.hopping_table.insertRow(row_index)

        # Pre-fill with default values
        self.hopping_table.setItem(row_index, 0, QTableWidgetItem("0"))
        self.hopping_table.setItem(row_index, 1, QTableWidgetItem("0"))
        self.hopping_table.setItem(row_index, 2, QTableWidgetItem("0"))
        self.hopping_table.setItem(row_index, 3, QTableWidgetItem("0.0"))
        self.hopping_table.setItem(row_index, 4, QTableWidgetItem("0.0"))

    def remove_selected_coupling(self):
        """Remove selected row(s) from the table"""
        selected_rows = set(item.row() for item in self.hopping_table.selectedItems())

        for row in sorted(selected_rows, reverse=True):
            self.hopping_table.removeRow(row)


# def show_hopping_details(self, row, col):
#     """Shows details for hopping between states at row,col positions."""
#     if not self.states:
#         return

#     # Update selected states
#     self.selected_state1 = self.states[row]
#     self.selected_state2 = self.states[col]

#     # Highlight the selected button
#     for pos, btn in self.buttons.items():
#         i, j = pos
#         if i == row and j == col:
#             # Highlight selected button
#             if pos in self.hopping_data and self.hopping_data[pos]:
#                 btn.setStyleSheet(
#                     """
#                     QPushButton {
#                         background-color: #4a86e8;
#                         border: 2px solid #2a56b8;
#                         border-radius: 3px;
#                     }
#                 """
#                 )
#             else:
#                 btn.setStyleSheet(
#                     """
#                     QPushButton {
#                         background-color: #e0e0e0;
#                         border: 2px solid #2a56b8;
#                         border-radius: 3px;
#                     }
#                 """
#                 )
#         else:
#             # Reset other buttons using the refresh method
#             if pos in self.hopping_data and self.hopping_data[pos]:
#                 btn.setStyleSheet(
#                     """
#                     QPushButton {
#                         background-color: #4a86e8;
#                         border: 1px solid #2a56b8;
#                         border-radius: 3px;
#                     }
#                     QPushButton:hover {
#                         background-color: #3a76d8;
#                         border: 1px solid #1a46a8;
#                     }
#                 """
#                 )
#             else:
#                 btn.setStyleSheet(
#                     """
#                     QPushButton {
#                         background-color: #e0e0e0;
#                         border: 1px solid #aaaaaa;
#                         border-radius: 3px;
#                     }
#                     QPushButton:hover {
#                         background-color: #d0d0d0;
#                         border: 1px solid #777777;
#                     }
#                 """
#                 )

#     # Update details label
#     state1_info = self.state_info[row]
#     state2_info = self.state_info[col]
#     self.details_label.setText(
#         f"Hopping: {state1_info[0]}.{state1_info[1]} → {state2_info[0]}.{state2_info[1]}"
#     )

#     # Populate table with existing hopping data
#     self.populate_hopping_table(row, col)

# def populate_hopping_table(self, row, col):
#     """Fills the table with hopping data for the selected state pair."""
#     self.hopping_table.setRowCount(0)  # Clear existing rows

#     if (row, col) not in self.hopping_data:
#         self.hopping_data[(row, col)] = []

#     for idx, hopping in enumerate(self.hopping_data.get((row, col), [])):
#         self.hopping_table.insertRow(idx)

#         # Add displacement vector components
#         d1_item = QTableWidgetItem(str(hopping.displacement[0]))
#         d2_item = QTableWidgetItem(str(hopping.displacement[1]))
#         d3_item = QTableWidgetItem(str(hopping.displacement[2]))

#         # Add amplitude (format as complex number)
#         amp_item = QTableWidgetItem(
#             f"{hopping.amplitude.real:.2f} + {hopping.amplitude.imag:.2f}j"
#         )

#         self.hopping_table.setItem(idx, 0, d1_item)
#         self.hopping_table.setItem(idx, 1, d2_item)
#         self.hopping_table.setItem(idx, 2, d3_item)
#         self.hopping_table.setItem(idx, 3, amp_item)

# def add_empty_row(self):
#     """Adds an empty row to the hopping table for user input."""
#     if not self.selected_state1 or not self.selected_state2:
#         return

#     # Temporarily disconnect cell changed signal to prevent triggering while adding cells
#     self.hopping_table.cellChanged.disconnect(self.on_table_cell_changed)

#     try:
#         # Get the current row count and add a new row
#         row_idx = self.hopping_table.rowCount()
#         self.hopping_table.insertRow(row_idx)

#         # Add default items (editable)
#         for col in range(3):  # displacement columns
#             item = QTableWidgetItem("0")
#             self.hopping_table.setItem(row_idx, col, item)

#         # Add default amplitude
#         amp_item = QTableWidgetItem("0.0 + 0.0j")
#         self.hopping_table.setItem(row_idx, 3, amp_item)

#         # Select the newly added row
#         self.hopping_table.selectRow(row_idx)

#         # Create a new hopping with default values
#         matrix_row = self.states.index(self.selected_state1)
#         matrix_col = self.states.index(self.selected_state2)

#         displacement = (0, 0, 0)
#         amplitude = complex(0.0, 0.0)

#         # Create new hopping
#         new_hopping = Hopping(
#             s1=self.selected_state1,
#             s2=self.selected_state2,
#             displacement=displacement,
#             amplitude=amplitude,
#         )

#         # Add to hopping data
#         if (matrix_row, matrix_col) not in self.hopping_data:
#             self.hopping_data[(matrix_row, matrix_col)] = []

#         self.hopping_data[(matrix_row, matrix_col)].append(new_hopping)

#         # Add hermitian conjugate if needed
#         if matrix_row != matrix_col:
#             conj_hopping = Hopping(
#                 s1=self.selected_state2,
#                 s2=self.selected_state1,
#                 displacement=(0, 0, 0),
#                 amplitude=complex(0.0, 0.0),
#             )

#             if (matrix_col, matrix_row) not in self.hopping_data:
#                 self.hopping_data[(matrix_col, matrix_row)] = []

#             self.hopping_data[(matrix_col, matrix_row)].append(conj_hopping)

#         # Update UI
#         self.refresh_button_colors()

#         # Emit signal
#         self.hopping_added.emit(new_hopping)
#     finally:
#         # Reconnect signal
#         self.hopping_table.cellChanged.connect(self.on_table_cell_changed)
