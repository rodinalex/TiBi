from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import numpy as np
from src.tibitypes import State, Hopping, get_states

from ui.HOPPING.matrix import HoppingMatrix
from ui.HOPPING.table import HoppingTable
from ui.UC.tree_view_panel import TreeViewPanel


class HoppingPanel(QWidget):
    """
    Widget for displaying and editing hopping terms between states in a unit cell.
    Displays a grid of buttons, where each button corresponds to a pair of states.
    """

    hopping_added = Signal(Hopping)
    hopping_removed = Signal(Hopping)

    def __init__(self, unit_cells, tree_view_panel: TreeViewPanel):
        super().__init__()
        # All unit cells
        self.unit_cells = unit_cells
        # self.hopping_data = {}  # Dictionary to store hopping data for each state pair
        # Reference to the tree view panel to register selection changes
        self.tree_view_panel = tree_view_panel
        # Main layout
        layout = QVBoxLayout(self)

        # Components
        self.info_label = QLabel(
            "Select a unit cell with states to view hopping parameters"
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        self.matrix = HoppingMatrix()
        self.table = HoppingTable()

        # Main Panel
        self.panel = QWidget()
        panel_layout = QHBoxLayout(self.panel)

        panel_layout.addWidget(self.matrix, stretch=1)
        panel_layout.addWidget(self.table, stretch=1)

        # A stack that hides the main panel if no unit cell is selected/unit cell has no states
        self.panel_stack = QStackedWidget()
        self.panel_stack.addWidget(self.info_label)
        self.panel_stack.addWidget(self.panel)
        layout.addWidget(self.panel_stack)

        # Connect tree view signals to show the appropriate panel
        self.tree_view_panel.none_selected.connect(self.show_info_panel)
        self.tree_view_panel.unit_cell_selected.connect(self.unit_cell_selected)
        self.tree_view_panel.site_selected.connect(self.site_selected)
        self.tree_view_panel.state_selected.connect(self.state_selected)

    def show_info_panel(self):
        self.panel_stack.setCurrentWidget(self.info_label)

    def unit_cell_selected(self, unit_cell_id):
        uc = self.unit_cells[unit_cell_id]
        new_states, new_info = get_states(uc)
        self.matrix.set_states(new_states, new_info)
        if new_states == []:
            self.panel_stack.setCurrentWidget(self.info_label)
        else:
            self.panel_stack.setCurrentWidget(self.panel)

    def site_selected(self, unit_cell_id, site_id):
        uc = self.unit_cells[unit_cell_id]
        new_states, new_info = get_states(uc)
        self.matrix.set_states(new_states, new_info)
        if new_states == []:
            self.panel_stack.setCurrentWidget(self.info_label)
        else:
            self.panel_stack.setCurrentWidget(self.panel)

    def state_selected(self, unit_cell_id, site_id, state_id):
        uc = self.unit_cells[unit_cell_id]
        new_states, new_info = get_states(uc)
        self.matrix.set_states(new_states, new_info)
        if new_states == []:
            self.panel_stack.setCurrentWidget(self.info_label)
        else:
            self.panel_stack.setCurrentWidget(self.panel)


# def set_unit_cell(self, unit_cell):
#     """Updates the matrix with states from the given unit cell."""
#     self.unit_cell = unit_cell
#     self.refresh_matrix()


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

# def on_table_cell_changed(self, row, column):
#     """Handle edits in the table cells."""
#     # Temporarily disconnect to prevent recursive calls
#     self.hopping_table.cellChanged.disconnect(self.on_table_cell_changed)

#     try:
#         if not self.selected_state1 or not self.selected_state2:
#             return

#         matrix_row = self.states.index(self.selected_state1)
#         matrix_col = self.states.index(self.selected_state2)

#         # Ensure hopping_data dictionary has an entry for this cell
#         if (matrix_row, matrix_col) not in self.hopping_data:
#             self.hopping_data[(matrix_row, matrix_col)] = []

#         # Ensure we have all cells in this row populated before proceeding
#         all_cells_populated = True
#         for col in range(4):
#             item = self.hopping_table.item(row, col)
#             if item is None:
#                 all_cells_populated = False
#                 # Create default cell if missing
#                 default_value = "0" if col < 3 else "0.0 + 0.0j"
#                 self.hopping_table.setItem(
#                     row, col, QTableWidgetItem(default_value)
#                 )

#         # Only continue processing if all cells are now available
#         if all_cells_populated:
#             # If we're modifying an existing row
#             if row < len(self.hopping_data[(matrix_row, matrix_col)]):
#                 self.update_existing_hopping(row, column, matrix_row, matrix_col)
#             else:
#                 # If we're dealing with a new row, create a new hopping
#                 self.create_new_hopping_from_row(row, matrix_row, matrix_col)

#             # Update UI
#             self.refresh_button_colors()
#     finally:
#         # Reconnect the signal
#         self.hopping_table.cellChanged.connect(self.on_table_cell_changed)

# def update_existing_hopping(self, row, column, matrix_row, matrix_col):
#     """Update an existing hopping based on table cell edit."""
#     # Get the current hopping
#     hopping = self.hopping_data[(matrix_row, matrix_col)][row]

#     # Get values from all cells in this row
#     try:
#         d1 = int(self.hopping_table.item(row, 0).text())
#         d2 = int(self.hopping_table.item(row, 1).text())
#         d3 = int(self.hopping_table.item(row, 2).text())

#         # Parse complex amplitude
#         amp_text = self.hopping_table.item(row, 3).text()
#         # Handle complex number formats like "1.0 + 2.0j" or "1.0+2.0j" or "1.0,2.0"
#         amp_text = amp_text.replace(" ", "").replace("j", "").replace("i", "")

#         if "+" in amp_text:
#             parts = amp_text.split("+")
#             real = float(parts[0])
#             imag = float(parts[1])
#         elif "," in amp_text:
#             parts = amp_text.split(",")
#             real = float(parts[0])
#             imag = float(parts[1])
#         else:
#             real = float(amp_text)
#             imag = 0.0

#         amplitude = complex(real, imag)

#         # Create displacement tuple
#         displacement = (d1, d2, d3)

#         # Update hopping
#         old_hopping = hopping

#         # Create new hopping with updated values
#         new_hopping = Hopping(
#             s1=self.selected_state1,
#             s2=self.selected_state2,
#             displacement=displacement,
#             amplitude=amplitude,
#         )

#         # Replace the old hopping
#         self.hopping_data[(matrix_row, matrix_col)][row] = new_hopping

#         # Update the conjugate hopping for symmetry
#         if matrix_row != matrix_col:
#             self.update_conjugate_hopping(
#                 old_hopping, new_hopping, matrix_row, matrix_col
#             )

#         # Emit signal
#         self.hopping_added.emit(new_hopping)

#     except (ValueError, IndexError) as e:
#         print(f"Error updating hopping: {e}")
#         # Revert to previous values if parsing fails
#         self.populate_hopping_table(matrix_row, matrix_col)

# def create_new_hopping_from_row(self, row, matrix_row, matrix_col):
#     """Create a new hopping from a table row."""
#     try:
#         # Safety checks for items
#         for col in range(4):
#             if self.hopping_table.item(row, col) is None:
#                 default_value = "0" if col < 3 else "0.0 + 0.0j"
#                 self.hopping_table.setItem(
#                     row, col, QTableWidgetItem(default_value)
#                 )

#         # Get values from the table cells
#         d1 = int(self.hopping_table.item(row, 0).text())
#         d2 = int(self.hopping_table.item(row, 1).text())
#         d3 = int(self.hopping_table.item(row, 2).text())

#         # Parse complex amplitude
#         amp_text = self.hopping_table.item(row, 3).text()
#         amp_text = amp_text.replace(" ", "").replace("j", "").replace("i", "")

#         try:
#             if "+" in amp_text:
#                 parts = amp_text.split("+")
#                 real = float(parts[0])
#                 imag = float(parts[1])
#             elif "," in amp_text:
#                 parts = amp_text.split(",")
#                 real = float(parts[0])
#                 imag = float(parts[1])
#             else:
#                 real = float(amp_text)
#                 imag = 0.0
#         except (ValueError, IndexError):
#             # If parsing fails, default to zero
#             real = 0.0
#             imag = 0.0

#         amplitude = complex(real, imag)
#         displacement = (d1, d2, d3)

#         # Check if this is a duplicate displacement
#         is_duplicate = False
#         for existing_hopping in self.hopping_data.get((matrix_row, matrix_col), []):
#             if existing_hopping.displacement == displacement:
#                 is_duplicate = True
#                 break

#         if is_duplicate:
#             print(
#                 f"Duplicate displacement {displacement} - updating existing entry"
#             )
#             # Find and update the existing entry instead of creating a new one
#             for idx, existing_hopping in enumerate(
#                 self.hopping_data[(matrix_row, matrix_col)]
#             ):
#                 if existing_hopping.displacement == displacement:
#                     new_hopping = Hopping(
#                         s1=self.selected_state1,
#                         s2=self.selected_state2,
#                         displacement=displacement,
#                         amplitude=amplitude,
#                     )
#                     self.hopping_data[(matrix_row, matrix_col)][idx] = new_hopping

#                     # Update the conjugate if needed
#                     if matrix_row != matrix_col:
#                         self.update_conjugate_for_displacement(
#                             displacement, amplitude, matrix_row, matrix_col
#                         )
#                     break
#         else:
#             # Create new hopping
#             new_hopping = Hopping(
#                 s1=self.selected_state1,
#                 s2=self.selected_state2,
#                 displacement=displacement,
#                 amplitude=amplitude,
#             )

#             # Add to hopping data
#             self.hopping_data[(matrix_row, matrix_col)].append(new_hopping)

#             # Add the hermitian conjugate for symmetry
#             if matrix_row != matrix_col:
#                 conj_displacement = (-d1, -d2, -d3)
#                 conj_amplitude = amplitude.conjugate()

#                 conj_hopping = Hopping(
#                     s1=self.selected_state2,
#                     s2=self.selected_state1,
#                     displacement=conj_displacement,
#                     amplitude=conj_amplitude,
#                 )

#                 if (matrix_col, matrix_row) not in self.hopping_data:
#                     self.hopping_data[(matrix_col, matrix_row)] = []

#                 self.hopping_data[(matrix_col, matrix_row)].append(conj_hopping)

#         # Emit signal for either case
#         self.hopping_added.emit(new_hopping)

#         # Format the display of the amplitude nicely
#         amp_item = self.hopping_table.item(row, 3)
#         amp_item.setText(f"{amplitude.real:.2f} + {amplitude.imag:.2f}j")

#     except (ValueError, IndexError, AttributeError) as e:
#         print(f"Error creating hopping: {e}")
#         # Don't remove the row, just populate with defaults
#         for col in range(4):
#             if self.hopping_table.item(row, col) is None:
#                 default_value = "0" if col < 3 else "0.0 + 0.0j"
#                 self.hopping_table.setItem(
#                     row, col, QTableWidgetItem(default_value)
#                 )

# def update_conjugate_for_displacement(
#     self, displacement, amplitude, matrix_row, matrix_col
# ):
#     """Update the conjugate hopping for a specific displacement."""
#     conj_displacement = (-displacement[0], -displacement[1], -displacement[2])
#     conj_amplitude = amplitude.conjugate()

#     # Look for existing conjugate with this displacement
#     found = False

#     if (matrix_col, matrix_row) in self.hopping_data:
#         for idx, hopping in enumerate(self.hopping_data[(matrix_col, matrix_row)]):
#             if hopping.displacement == conj_displacement:
#                 # Update the existing conjugate
#                 new_conj = Hopping(
#                     s1=self.selected_state2,
#                     s2=self.selected_state1,
#                     displacement=conj_displacement,
#                     amplitude=conj_amplitude,
#                 )

#                 self.hopping_data[(matrix_col, matrix_row)][idx] = new_conj
#                 found = True
#                 break

#     # If not found, create new conjugate
#     if not found:
#         new_conj = Hopping(
#             s1=self.selected_state2,
#             s2=self.selected_state1,
#             displacement=conj_displacement,
#             amplitude=conj_amplitude,
#         )

#         if (matrix_col, matrix_row) not in self.hopping_data:
#             self.hopping_data[(matrix_col, matrix_row)] = []

#         self.hopping_data[(matrix_col, matrix_row)].append(new_conj)

# def update_conjugate_hopping(
#     self, old_hopping, new_hopping, matrix_row, matrix_col
# ):
#     """Update the conjugate hopping when the original is modified."""
#     # Find the conjugate hopping
#     old_conj_displacement = (
#         -old_hopping.displacement[0],
#         -old_hopping.displacement[1],
#         -old_hopping.displacement[2],
#     )

#     if (matrix_col, matrix_row) in self.hopping_data:
#         for i, h in enumerate(self.hopping_data[(matrix_col, matrix_row)]):
#             if h.displacement == old_conj_displacement:
#                 # Create new conjugate
#                 new_conj_displacement = (
#                     -new_hopping.displacement[0],
#                     -new_hopping.displacement[1],
#                     -new_hopping.displacement[2],
#                 )
#                 new_conj_amplitude = new_hopping.amplitude.conjugate()

#                 new_conj_hopping = Hopping(
#                     s1=self.selected_state2,
#                     s2=self.selected_state1,
#                     displacement=new_conj_displacement,
#                     amplitude=new_conj_amplitude,
#                 )

#                 # Replace the old conjugate
#                 self.hopping_data[(matrix_col, matrix_row)][i] = new_conj_hopping
#                 break

# def remove_selected_hopping(self):
#     """Removes the selected hopping from the table."""
#     current_row = self.hopping_table.currentRow()
#     if current_row < 0:
#         return

#     if not self.selected_state1 or not self.selected_state2:
#         return

#     # Find row and col for the selected states
#     row = self.states.index(self.selected_state1)
#     col = self.states.index(self.selected_state2)

#     if (row, col) in self.hopping_data and current_row < len(
#         self.hopping_data[(row, col)]
#     ):
#         # Get the hopping to be removed
#         hopping = self.hopping_data[(row, col)][current_row]

#         # Remove from hopping data
#         self.hopping_data[(row, col)].pop(current_row)

#         # Find and remove the hermitian conjugate hopping if it exists
#         if row != col:  # Only if not on diagonal
#             conj_displacement = (
#                 -hopping.displacement[0],
#                 -hopping.displacement[1],
#                 -hopping.displacement[2],
#             )

#             # Find the matching conjugate hopping
#             if (col, row) in self.hopping_data:
#                 for i, h in enumerate(self.hopping_data[(col, row)]):
#                     if h.displacement == conj_displacement:
#                         self.hopping_data[(col, row)].pop(i)
#                         break

#         # Update UI
#         self.refresh_button_colors()
#         self.populate_hopping_table(row, col)

#         # Emit signal
#         self.hopping_removed.emit(hopping)
