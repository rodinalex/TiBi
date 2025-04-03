import uuid
from PySide6.QtCore import QObject, Signal
from src.tibitypes import UnitCell, State
import numpy as np
from ui.HOPPING.matrix import HoppingMatrix
from ui.HOPPING.table import HoppingTable
from PySide6.QtWidgets import QLabel
from models.uc_models import ListModel


class HoppingController(QObject):
    """Controller to manage hopping parameters between states in unit cells."""

    def __init__(
        self,
        matrix: HoppingMatrix,
        table: HoppingTable,
        selected_state1,
        selected_state2,
        hopping_data,
    ):
        super().__init__()
        self.matrix = matrix
        self.table = table
        self.selected_state1 = selected_state1
        self.selected_state2 = selected_state2
        self.hopping_data = hopping_data

        # Connect matrix signals
        self.matrix.button_clicked.connect(self.handle_pair_selection)

        # Connect table signals
        self.table.save_btn.clicked.connect(self.save_couplings)

    def handle_pair_selection(self, s1, s2):
        self.selected_state1 = s1.id
        self.selected_state2 = s2.id
        state_coupling = self.hopping_data.get(
            (self.selected_state1, self.selected_state2), []
        )
        self.table.set_state_coupling(state_coupling)
        self.table.table_title(QLabel(f"{s2[0]}.{s2[1]} → {s1[0]}.{s1[1]}"))

    def save_couplings(self):
        """Extract table data and store it in self.table.state_coupling"""
        new_couplings = []
        for row in range(self.table.hopping_table.rowCount()):
            try:
                d1 = int(self.table.hopping_table.item(row, 0).text())
                d2 = int(self.table.hopping_table.item(row, 1).text())
                d3 = int(self.table.hopping_table.item(row, 2).text())
                re = float(self.table.hopping_table.item(row, 3).text())
                im = float(self.table.hopping_table.item(row, 4).text())

                amplitude = np.complex128(re + im * 1j)  # Convert to complex

                new_couplings.append(((d1, d2, d3), amplitude))
            except (ValueError, AttributeError):
                # Ignore rows with missing/invalid data
                continue
        self.hopping_data[(self.selected_state1, self.selected_state2)] = new_couplings
        self.table.set_state_coupling(new_couplings)

        # Next, clear self.table.state_coupling and append new_couplings there,
        # triggering the update and use the update the refresh the table


#         self.unit_cells = unit_cells
#         self.hopping_matrix = hopping_matrix
#         self.selection = selection

#         # Connect UI signals
#         self.hopping_matrix.hopping_added.connect(self.on_hopping_added)
#         self.hopping_matrix.hopping_removed.connect(self.on_hopping_removed)

#     def update_hopping_view(self):
#         """Updates the hopping matrix view when a unit cell is selected."""
#         if "unit_cell" in self.selection and self.selection["unit_cell"] in self.unit_cells:
#             unit_cell = self.unit_cells[self.selection["unit_cell"]]

#             # Debug information
#             print("Selected Unit Cell:", unit_cell.name)
#             print("Number of sites:", len(unit_cell.sites))
#             for site_id, site in unit_cell.sites.items():
#                 print(f"  Site {site.name} has {len(site.states)} states:")
#                 for state_id, state in site.states.items():
#                     print(f"    - State: {state.name}, Energy: {state.energy}")

#             self.hopping_matrix.set_unit_cell(unit_cell)
#         else:
#             self.hopping_matrix.set_unit_cell(None)

#     def on_hopping_added(self, hopping: Hopping):
#         """Handles when a new hopping is added in the UI."""
#         if "unit_cell" not in self.selection:
#             return

#         unit_cell_id = self.selection["unit_cell"]

#         # In a real implementation, we would add the hopping to the unit cell's data structure
#         # For example:
#         # if not hasattr(self.unit_cells[unit_cell_id], 'hoppings'):
#         #     self.unit_cells[unit_cell_id].hoppings = []
#         # self.unit_cells[unit_cell_id].hoppings.append(hopping)

#         # Emit signal that the model has changed
#         self.hopping_changed.emit()

#     def on_hopping_removed(self, hopping: Hopping):
#         """Handles when a hopping is removed in the UI."""
#         if "unit_cell" not in self.selection:
#             return

#         unit_cell_id = self.selection["unit_cell"]

#         # In a real implementation, we would remove the hopping from the unit cell's data structure
#         # For example:
#         # if hasattr(self.unit_cells[unit_cell_id], 'hoppings'):
#         #     self.unit_cells[unit_cell_id].hoppings.remove(hopping)

#         # Emit signal that the model has changed
#         self.hopping_changed.emit()

#     def load_hoppings_for_unit_cell(self, unit_cell_id):
#         """Loads hopping data for a specific unit cell into the matrix view."""
#         if unit_cell_id not in self.unit_cells:
#             return

#         unit_cell = self.unit_cells[unit_cell_id]

#         # Clear existing hopping data in the matrix view
#         self.hopping_matrix.hopping_data = {}

#         # In a real implementation, we would load hoppings from the unit cell's data structure
#         # For example:
#         # if hasattr(unit_cell, 'hoppings'):
#         #     for hopping in unit_cell.hoppings:
#         #         # Need to map from state objects to row/column indices in the matrix
#         #         # This would require building a state_map dictionary
#         #         state_map = {}
#         #         for i, state in enumerate(self.hopping_matrix.states):
#         #             state_map[state.id] = i
#         #
#         #         if hopping.s1.id in state_map and hopping.s2.id in state_map:
#         #             row = state_map[hopping.s1.id]
#         #             col = state_map[hopping.s2.id]
#         #
#         #             if (row, col) not in self.hopping_matrix.hopping_data:
#         #                 self.hopping_matrix.hopping_data[(row, col)] = []
#         #
#         #             self.hopping_matrix.hopping_data[(row, col)].append(hopping)

#         # Update the matrix view
#         self.hopping_matrix.set_unit_cell(unit_cell)
