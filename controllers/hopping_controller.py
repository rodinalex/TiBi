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
        self.table.set_state_coupling(new_couplings)
