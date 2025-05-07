from PySide6.QtGui import QUndoCommand
import random
from resources.constants import (
    default_site_size,
    mk_new_unit_cell,
    mk_new_site,
    mk_new_state,
)


class AddUnitCellCommand(QUndoCommand):
    def __init__(self, controller):
        super().__init__("Add Unit Cell")
        self.controller = controller
        self.unit_cell = mk_new_unit_cell()

    def redo(self):
        self.controller.unit_cells[self.unit_cell.id] = self.unit_cell
        self.controller._add_tree_item(self.unit_cell.id)

    def undo(self):
        self.controller._delete_item(self.unit_cell.id)


class AddSiteCommand(QUndoCommand):
    def __init__(self, controller):
        super().__init__("Add Site")
        self.controller = controller
        self.uc_id = self.controller.selection["unit_cell"]
        self.site = mk_new_site()

    def redo(self):
        unit_cell = self.controller.unit_cells[self.uc_id]
        unit_cell.sites[self.site.id] = self.site
        unit_cell.site_colors[self.site.id] = (
            random.uniform(0, 1),
            random.uniform(0, 1),
            random.uniform(0, 1),
            1.0,
        )
        unit_cell.site_sizes[self.site.id] = default_site_size

        self.controller._add_tree_item(self.uc_id, self.site.id)

    def undo(self):
        self.controller._delete_item(self.uc_id, self.site.id)


class AddStateCommand(QUndoCommand):
    def __init__(self, controller):
        super().__init__("Add State")
        self.controller = controller
        self.uc_id = self.controller.selection["unit_cell"]
        self.site_id = self.controller.selection["site"]
        self.state = mk_new_state()

    def redo(self):
        unit_cell = self.controller.unit_cells[self.uc_id]
        site = unit_cell.sites[self.site_id]
        site.states[self.state.id] = self.state
        self.controller._add_tree_item(self.uc_id, self.site_id, self.state.id)

    def undo(self):
        self.controller._delete_item(self.uc_id, self.site_id, self.state.id)
