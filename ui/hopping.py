from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
)
from PySide6.QtCore import Qt
import numpy as np
from src.tibitypes import get_states

from ui.HOPPING.matrix import HoppingMatrix
from ui.HOPPING.table import HoppingTable

from models.uc_models import DataModel
import uuid


class HoppingPanel(QWidget):
    """
    Widget for displaying and editing hopping terms between states in a unit cell.
    Displays a grid of buttons, where each button corresponds to a pair of states.
    """

    def __init__(self, unit_cells):
        super().__init__()
        # All unit cells
        self.unit_cells = unit_cells
        self.uc_id = None
        """A dictionary of hoppings for the selected unit cell. 
        The keys are Tuple[uuid, uuid] and the values are 
        list[Tuple[int, int, int], np.complex128]"""
        self.hopping_data = DataModel()

        # Current selection of a hopping pair from the list of states inside the unit cell
        self.selected_state1 = None
        self.selected_state2 = None

        # Initialize the panels
        self.matrix = HoppingMatrix(self.hopping_data)
        self.table = HoppingTable()

        # Connect Signals
        self.matrix.button_clicked.connect(self.handle_pair_selection)
        self.table.save_btn.clicked.connect(self.save_couplings)

        # Main layout
        layout = QVBoxLayout(self)

        # Components
        self.info_label = QLabel(
            "Select a unit cell with states to view hopping parameters"
        )
        self.info_label.setAlignment(Qt.AlignCenter)

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

    def set_uc_id(self, uc_id: uuid.UUID):
        """
        Called when a unit cell is selected in the tree view.
        Updates the hopping panel to display the selected unit cell's states and hoppings.

        Args:
            uc_id: UUID of the selected unit cell, or None if no unit cell is selected
        """
        self.uc_id = uc_id
        # Reset state selections and clear existing data
        self.selected_state1 = None
        self.selected_state2 = None
        self.hopping_data = None  # Will be populated with the unit cell's hopping data if a valid selection exists

        # Clear the table since no state pair is selected yet
        self.table.set_state_coupling([])
        self.table.table_title.setText("")
        # If no unit cell selected, hide the panels
        if uc_id == None:
            self.panel_stack.setCurrentWidget(self.info_label)
        else:
            uc = self.unit_cells[uc_id]
            # Get the states and their "info" from inside the unit cell
            new_states, new_info = get_states(uc)
            # Use the states and the info to construct the hopping matrix grid
            self.matrix.set_states(new_info)
            # Extract the hopping data
            self.hopping_data = DataModel(uc.hoppings)
            self.matrix.set_hopping_data(self.hopping_data)
            # If there are no states in the unit cell, hide the panels
            if new_states == []:
                self.panel_stack.setCurrentWidget(self.info_label)
            else:
                self.panel_stack.setCurrentWidget(self.panel)

    def handle_pair_selection(self, s1, s2):
        """
        Called when a button is clicked in the hopping matrix.
        Updates the table to display hopping terms between the selected states.

        Args:
            s1: Tuple of (site_name, state_name, state_id) for the destination state (row)
            s2: Tuple of (site_name, state_name, state_id) for the source state (column)
        """
        # Store the UUIDs of the selected states
        self.selected_state1 = s1[2]  # Destination state UUID
        self.selected_state2 = s2[2]  # Source state UUID

        # Retrieve existing hopping terms between these states, or empty list if none exist
        state_coupling = self.hopping_data.get(
            (self.selected_state1, self.selected_state2), []
        )

        # Update the table with the retrieved hopping terms
        self.table.set_state_coupling(state_coupling)

        # Update the table title to show the selected states (source → destination)
        self.table.table_title.setText(f"{s2[0]}.{s2[1]} → {s1[0]}.{s1[1]}")

    def save_couplings(self):
        """
        Extracts data from the hopping table and saves it to the unit cell model.

        Reads all rows from the table, converting cell values to the appropriate types:
        - First 3 columns (d₁,d₂,d₃) to integers (displacement vector)
        - Last 2 columns (Re(t), Im(t)) to floats (complex amplitude)

        If any conversion fails (invalid input), the operation is aborted and
        the table is reset to the last valid state.
        """
        new_couplings = []
        try:
            # Extract values from each row in the table
            for row in range(self.table.hopping_table.rowCount()):
                # Get displacement vector components (integers)
                d1 = int(self.table.hopping_table.item(row, 0).text())
                d2 = int(self.table.hopping_table.item(row, 1).text())
                d3 = int(self.table.hopping_table.item(row, 2).text())

                # Get complex amplitude components (floats)
                re = float(self.table.hopping_table.item(row, 3).text())
                im = float(self.table.hopping_table.item(row, 4).text())

                # Create the complex amplitude
                amplitude = np.complex128(re + im * 1j)

                # Add this coupling to the new list
                new_couplings.append(((d1, d2, d3), amplitude))

            # Update the data model with the new couplings
            self.hopping_data[(self.selected_state1, self.selected_state2)] = (
                new_couplings
            )

            # Update the unit cell model (important for persistence)
            self.unit_cells[self.uc_id].hoppings = self.hopping_data

            # Refresh the table with the new data
            self.table.set_state_coupling(new_couplings)

            # Update the matrix to show the new coupling state
            self.matrix.refresh_matrix()
        except ValueError:
            # If there's an error parsing inputs, revert to the last valid state
            self.table.set_state_coupling(
                self.hopping_data.get((self.selected_state1, self.selected_state2), [])
            )
