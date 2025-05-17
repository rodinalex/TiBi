import copy
import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand
from typing import Tuple
import uuid

from src.tibitypes import UnitCell


# Tree Commands
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
        pair_selection: list,
        new_hoppings: list,
        hoppings: list[Tuple[Tuple[int, int, int], np.complex128]],
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

        self.uc_id = self.selection.get("unit_cell", None)
        self.site_id = self.selection.get("site", None)
        self.state_id = self.selection.get("state", None)

        # Selected state UUIDs
        self.s1_id = pair_selection[0][3]
        self.s2_id = pair_selection[0][3]

        self.new_hoppings = new_hoppings
        self.old_hoppings = copy.deepcopy(hoppings[(self.s1_id, self.s2_id)])

        # self.old_hoppings = copy.deepcopy(self.hoppings)
        self.signal = signal

        self.uc_id = self.selection["unit_cell"]

    def redo(self):
        # Select the appropriate item
        # Insert the hoppings into the unit cell model
        self.unit_cells[self.uc_id].hoppings[
            (self.s1_id, self.s2_id)
        ] = self.new_hoppings
        # Refresh the view
        pass

    def undo(self):

        self.unit_cells[self.uc_id].hoppings[
            (self.s1_id, self.s2_id)
        ] = self.old_hoppings

        pass

        # self.hoppings[
        #     (self.pair_selection[0][3], self.pair_selection[1][3])
        # ] = merged_couplings
        # self.unit_cells[self.selection["unit_cell"]].hoppings = self.hoppings

        # # Refresh the table with the new data
        # self.state_coupling = merged_couplings

        # # Update the matrix and the table to show the new coupling state
        # self._refresh_matrix()
        # self._refresh_table()


#         self.hoppings[
#             (self.pair_selection[0][3], self.pair_selection[1][3])
#         ] = merged_couplings
#         self.unit_cells[self.selection["unit_cell"]].hoppings = self.hoppings

#         # Refresh the table with the new data
#         self.state_coupling = merged_couplings

#         # Update the matrix and the table to show the new coupling state
#         self._refresh_matrix()
#         self._refresh_table()


# SaveHoppingsCommand(
#     unit_cells=self.unit_cells,
#     selection=self.selection,
#     pair_selection=self.pair_selection,
#     new_hoppings=merged_couplings,
#     hoppings=self.state_coupling,
#     signal=self.hopping_view_update_requested,
# )
