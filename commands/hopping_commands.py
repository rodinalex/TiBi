import copy
from PySide6.QtCore import QItemSelectionModel, Signal
from PySide6.QtGui import QColor, QStandardItem, QUndoCommand
from PySide6.QtWidgets import QDoubleSpinBox, QRadioButton
from resources.constants import (
    mk_new_unit_cell,
    mk_new_site,
    mk_new_state,
)
import uuid

from resources.ui_elements import SystemTree
from src.tibitypes import BasisVector, UnitCell
from views.uc_view import UnitCellView


# Tree Commands
class SaveHoppingsCommand(QUndoCommand):
    """
    Save the hoppings between two states.

    Creates a unit cell with orthogonal basis vectors along
    the x, y, and z axes, adds it to the unit_cells dictionary
    and to the tree view.

    The default unit cell has:
    - Name: "New Unit Cell"
    - Three orthogonal unit vectors along the x, y, and z axes
    - No periodicity (0D system)
    - No sites or states initially
    """

    def __init__(
        self, unit_cells: dict[uuid.UUID, UnitCell], tree_view: SystemTree
    ):
        """
        Initialize the command.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            tree_view: UI object containing the tree view
        """
        super().__init__("Add Unit Cell")
        self.unit_cells = unit_cells
        self.tree_view = tree_view
        self.unit_cell = mk_new_unit_cell()

    # Add the newly-created unit cell to the dictionary and create a tree item
    def redo(self):
        self.unit_cells[self.unit_cell.id] = self.unit_cell
        self.tree_view.add_tree_item(self.unit_cell.name, self.unit_cell.id)

    # Remove the unit cell from the dictionary and the tree using its id
    def undo(self):
        del self.unit_cells[self.unit_cell.id]
        self.tree_view.remove_tree_item(self.unit_cell.id)
