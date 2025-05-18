import copy
import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand
from typing import Tuple
import uuid

from src.tibitypes import UnitCell


class SaveHoppingsCommand(QUndoCommand):
    """
    Save the hoppings between two states.

    Update the hoppings in the main model, as well as the local
    controller model
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        pair_selection: list[Tuple[str, uuid.UUID, str, uuid.UUID]],
        new_hoppings: list[Tuple[Tuple[int, int, int], np.complex128]],
        signal: Signal,
    ):
        """
        Initialize the command.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            tree_view: UI object containing the tree view
        """
        super().__init__("Add Unit Cell")
        self.unit_cells = unit_cells
        self.selection = selection
        self.uc_id = self.selection["unit_cell"]
        self.site_id = self.selection["site"]
        self.state_id = self.selection["state"]

        # Selected state UUIDs
        self.s1 = pair_selection[0]
        self.s2 = pair_selection[1]

        self.new_hoppings = new_hoppings
        # self.new_hoppings = copy.deepcopy(new_hoppings)
        self.old_hoppings = copy.deepcopy(
            self.unit_cells[self.uc_id].hoppings.get(
                (self.s1[3], self.s2[3]), []
            )
        )
        print(self.old_hoppings)
        self.signal = signal

    def redo(self):
        # Select the appropriate item
        self.selection.update(
            {
                "unit_cell": self.uc_id,
                "site": self.site_id,
                "state": self.state_id,
            }
        )
        # Insert the hoppings into the unit cell model
        if self.new_hoppings == []:
            del self.unit_cells[self.uc_id].hoppings[(self.s1[3], self.s2[3])]
        else:
            self.unit_cells[self.uc_id].hoppings[
                (self.s1[3], self.s2[3])
            ] = self.new_hoppings
        # Update Pair Selection
        self.pair_selection = [self.s1, self.s2]

        # Emit the signal
        self.signal.emit()

    def undo(self):
        # Select the appropriate item
        self.selection.update(
            {
                "unit_cell": self.uc_id,
                "site": self.site_id,
                "state": self.state_id,
            }
        )
        # Insert the hoppings into the unit cell model
        if self.old_hoppings == []:
            del self.unit_cells[self.uc_id].hoppings[(self.s1[3], self.s2[3])]
        else:
            self.unit_cells[self.uc_id].hoppings[
                (self.s1[3], self.s2[3])
            ] = self.old_hoppings

        # Update Pair Selection
        self.pair_selection = [self.s1, self.s2]
        # Emit the signal
        self.signal.emit()
