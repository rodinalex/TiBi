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
        self.uc_id = uc_id
        # Deselect states when any selection occurs in the tree (even if within the same unit cell).
        # Clear the hopping data also and redraw the couplings table
        self.selected_state1 = None
        self.selected_state2 = None
        self.hopping_data = None
        # Clearing the table because no site pair is selected
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
        self.selected_state1 = s1[2]
        self.selected_state2 = s2[2]
        state_coupling = self.hopping_data.get(
            (self.selected_state1, self.selected_state2), []
        )
        self.table.set_state_coupling(state_coupling)
        self.table.table_title.setText(f"{s2[0]}.{s2[1]} → {s1[0]}.{s1[1]}")

    def save_couplings(self):
        """Extract table data and store it in self.table.state_coupling"""
        new_couplings = []
        for row in range(self.table.hopping_table.rowCount()):
            d1 = int(self.table.hopping_table.item(row, 0).text())
            d2 = int(self.table.hopping_table.item(row, 1).text())
            d3 = int(self.table.hopping_table.item(row, 2).text())
            re = float(self.table.hopping_table.item(row, 3).text())
            im = float(self.table.hopping_table.item(row, 4).text())

            amplitude = np.complex128(re + im * 1j)

            new_couplings.append(((d1, d2, d3), amplitude))
        self.hopping_data[(self.selected_state1, self.selected_state2)] = new_couplings
        self.unit_cells[self.uc_id].hoppings = self.hopping_data
        self.table.set_state_coupling(new_couplings)
