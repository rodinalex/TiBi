from PySide6.QtGui import QUndoCommand
from resources.constants import mk_new_unit_cell
import copy


class AddUnitCellCommand(QUndoCommand):
    def __init__(self, controller):
        super().__init__("Add Unit Cell")
        self.controller = controller
        self.selection = controller.selection
        self.unit_cell = mk_new_unit_cell()

    def redo(self):
        self.controller._add_unit_cell(self.unit_cell)

    def undo(self):
        self.controller.selection = copy.copy(self.selection)
        self.controller._delete_item()
