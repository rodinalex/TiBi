import copy
import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand
from typing import Tuple
import uuid

from models import Selection, UnitCell


class SaveHoppingsCommand(QUndoCommand):
    """
    Save the hoppings between two states.

    Update the entry in the `hoppings` dictionary of the selected unit
    for the selected pair of states.

    Attributes
    ----------

    unit_cells : dict[uuid.UUID, UnitCell]
        Reference to the dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Reference to the dictionary containing the current selection
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site_id : uuid.UUID
        UUID of the selected `Site` when the command was issued
    state_id : uuid.UUID
        UUID of the selected `State` when the command was issued
    pair_selection : list[Tuple[str, uuid.UUID, str, uuid.UUID]]
        Reference to the list of selected `State`s
    s1, s2 : Tuple[str, uuid.UUID, str, uuid.UUID]
        Information tuples for the selected `State`s, containing
        (site name, site UUID, state name, state UUID) when the
        command was issued
    new_hoppings : list[Tuple[Tuple[int, int, int], np.complex128]]
        List of new hoppings to be added to the `hoppings` dictionary
    old_hoppings : list[Tuple[Tuple[int, int, int], np.complex128]]
        List of old hoppings to be removed from the `hoppings` dictionary
    signal : Signal
        Signal to be emitted when the command is executed. The signal
        carries the information about the selected `UnitCell`, `Site`,
        `State`, and the selected pair of `State`s.
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        pair_selection: list[Tuple[str, uuid.UUID, str, uuid.UUID]],
        new_hoppings: list[Tuple[Tuple[int, int, int], np.complex128]],
        signal: Signal,
    ):
        """
        Initialize the SaveHoppingsCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Reference to the dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            Reference to the dictionary containing the current selection
        pair_selection : list[Tuple[str, uuid.UUID, str, uuid.UUID]]
            Reference to the list of selected `State`s
            command was issued
        new_hoppings : list[Tuple[Tuple[int, int, int], np.complex128]]
            List of new hoppings to be added to the `hoppings` dictionary
        signal : Signal
            Signal to be emitted when the command is executed. The signal
            carries the information about the selected `UnitCell`, `Site`,
            `State`, and the selected pair of `State`s.
        """
        super().__init__("Modify Hoppings")
        self.unit_cells = unit_cells
        self.selection = selection
        self.uc_id = self.selection.unit_cell
        self.site_id = self.selection.site
        self.state_id = self.selection.state

        # Selected state UUIDs
        self.pair_selection = pair_selection
        self.s1 = pair_selection[0]
        self.s2 = pair_selection[1]

        self.new_hoppings = new_hoppings
        self.old_hoppings = copy.deepcopy(
            self.unit_cells[self.uc_id].hoppings.get(
                (self.s1[3], self.s2[3]), []
            )
        )
        self.signal = signal

    def redo(self):
        # Insert the hoppings into the unit cell model
        if self.new_hoppings == []:
            self.unit_cells[self.uc_id].hoppings.pop(
                (self.s1[3], self.s2[3]), None
            )
        else:
            self.unit_cells[self.uc_id].hoppings[
                (self.s1[3], self.s2[3])
            ] = self.new_hoppings
        self.unit_cells[self.uc_id].bandstructure.reset_bands()
        self.unit_cells[self.uc_id].bz_grid.clear()
        # Emit the signal with appropriate selection parameters
        self.signal.emit(
            self.uc_id, self.site_id, self.state_id, self.s1, self.s2
        )

    def undo(self):
        # Insert the hoppings into the unit cell model
        if self.old_hoppings == []:
            self.unit_cells[self.uc_id].hoppings.pop(
                (self.s1[3], self.s2[3]), None
            )
        else:
            self.unit_cells[self.uc_id].hoppings[
                (self.s1[3], self.s2[3])
            ] = self.old_hoppings
        self.unit_cells[self.uc_id].bandstructure.reset_bands()
        self.unit_cells[self.uc_id].bz_grid.clear()
        # Emit the signal with appropriate selection parameters
        self.signal.emit(
            self.uc_id, self.site_id, self.state_id, self.s1, self.s2
        )
