from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QHeaderView,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import numpy as np
from src.tibitypes import State, get_states

from ui.HOPPING.matrix import HoppingMatrix
from ui.HOPPING.table import HoppingTable

from models.uc_models import DataModel
from controllers.hopping_controller import HoppingController
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
        self.matrix = HoppingMatrix()
        self.table = HoppingTable()

        # Initialize the controller
        self.controller = HoppingController(
            self.matrix,
            self.table,
            self.selected_state1,
            self.selected_state2,
            self.hopping_data,
        )

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

        # UI Signals

    def set_uc_id(self, uc_id: uuid.UUID):
        self.uc_id = uc_id
        # Deselect states when any selection occurs in the tree (even if within the same unit cell).
        # Clear the hopping data also and redraw the couplings table
        self.selected_state1 = None
        self.selected_state2 = None
        self.hopping_data = None
        # Clearing the table because no site pair is selected
        self.table.set_state_coupling([])
        # If no unit cell selected, hide the panels
        if uc_id == None:
            self.panel_stack.setCurrentWidget(self.info_label)
        else:
            uc = self.unit_cells[uc_id]
            # Get the states and their "info" from inside the unit cell
            new_states, new_info = get_states(uc)
            # Use the states and the info to construct the hopping matrix grid
            self.matrix.set_states(new_states, new_info)
            # Extract the hopping data
            self.hopping_data = DataModel(uc.hoppings)
            # If there are no states in the unit cell, hide the panels
            if new_states == []:
                self.panel_stack.setCurrentWidget(self.info_label)
            else:
                self.panel_stack.setCurrentWidget(self.panel)
