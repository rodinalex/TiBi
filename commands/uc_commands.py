import copy
from PySide6.QtGui import QUndoCommand
import random
from resources.constants import (
    default_site_size,
    mk_new_unit_cell,
    mk_new_site,
    mk_new_state,
)


class AddUnitCellCommand(QUndoCommand):
    """
    Create a new unit cell with default properties and add it to the model.

    Creates a unit cell with orthogonal basis vectors along
    the x, y, and z axes, adds it to the unit_cells dictionary
    and to the tree view.

    The default unit cell has:
    - Name: "New Unit Cell"
    - Three orthogonal unit vectors along the x, y, and z axes
    - No periodicity (0D system)
    - No sites or states initially

    After creation, the tree view is updated and the new unit cell is
    automatically selected so the user can immediately edit its properties.
    """

    def __init__(self, controller):
        super().__init__("Add Unit Cell")
        self.controller = controller
        self.unit_cell = mk_new_unit_cell()

    # Add the newly-created unit cell to the dictionary and create a tree item
    def redo(self):
        self.controller.unit_cells[self.unit_cell.id] = self.unit_cell
        self.controller.tree_view._add_tree_item(
            self.unit_cell.name, self.unit_cell.id
        )

    # Remove the unit cell from the dictionary and the tree using its id
    def undo(self):
        del self.controller.unit_cells[self.unit_cell.id]
        self.controller.tree_view._remove_tree_item(self.unit_cell.id)


class AddSiteCommand(QUndoCommand):
    """
    Create a new site in the currently selected unit cell.

    Creates a site with default name and coordinates (0,0,0), adds it to
    the sites dictionary of the selected unit cell and to the tree.

    The default site has:
    - Name: "New Site"
    - Coordinates (0,0,0)
    - No states initially
    - Default radius
    - Random color
    """

    def __init__(self, controller):
        super().__init__("Add Site")
        self.controller = controller
        self.uc_id = self.controller.selection["unit_cell"]
        self.site = mk_new_site()

    # Add the newly-created site to the dictionary and create a tree item
    # Add entries to the size and colors dictionaries for the site
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
        self.controller.tree_view._add_tree_item(
            self.site.name, self.uc_id, self.site.id
        )

    # Remove the unit cell from the dictionary and the tree using its id
    # Remove the color and size entries
    def undo(self):
        del self.controller.unit_cells[self.uc_id].sites[self.site.id]
        del self.controller.unit_cells[self.uc_id].site_colors[self.site.id]
        del self.controller.unit_cells[self.uc_id].site_sizes[self.site.id]
        self.controller.tree_view._remove_tree_item(self.uc_id, self.site.id)


class AddStateCommand(QUndoCommand):
    """
    Create a new state in the currently selected site.

    Creates a state with default name, adds it to the
    states dictionary of the selected site and to the tree.

    The default state has:
    - Name: "New State"
    """

    def __init__(self, controller):
        super().__init__("Add State")
        self.controller = controller
        self.uc_id = self.controller.selection["unit_cell"]
        self.site_id = self.controller.selection["site"]
        self.state = mk_new_state()

    # Add the newly-created state to the dictionary and create a tree item
    def redo(self):
        unit_cell = self.controller.unit_cells[self.uc_id]
        site = unit_cell.sites[self.site_id]
        site.states[self.state.id] = self.state
        self.controller.tree_view._add_tree_item(
            self.state.name, self.uc_id, self.site_id, self.state.id
        )

    # Remove the site from the dictionary and the tree using its id
    def undo(self):
        del (
            self.controller.unit_cells[self.uc_id]
            .sites[self.site_id]
            .states[self.state.id]
        )
        self.controller.tree_view._remove_tree_item(
            self.uc_id, self.site_id, self.state.id
        )


class DeleteItemCommand(QUndoCommand):
    """
    Delete the currently selected item from the model.

    This command handles deletion of unit cells, sites, and states based on
    the current selection. It updates both the data model and
    the tree view to reflect the deletion, and ensures that
    the selection is updated appropriately.

    The deletion follows the containment hierarchy:
    - Deleting a unit cell also removes all its sites and states
    - Deleting a site also removes all its states
    - Deleting a state only removes that specific state

    After deletion, the parent item is selected
    (or nothing if a unit cell was deleted).
    """

    def __init__(self, controller):
        super().__init__("Add State")
        self.controller = controller
        self.uc_id = self.controller.selection.get("unit_cell", None)
        self.site_id = self.controller.selection.get("site", None)
        self.state_id = self.controller.selection.get("state", None)

    # Determine what item type is being deleted and save its deep copy.
    # For Sites, also save their color and radius
    # Delete the item after
    def redo(self):
        if self.state_id:
            self.item = copy.deepcopy(
                self.controller.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
            )
            # Delete the selected state from the site
            del (
                self.controller.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
            )
        # No state selected, therefore remove the site from the unit cell
        elif self.site_id:
            self.item = copy.deepcopy(
                self.controller.unit_cells[self.uc_id].sites[self.site_id]
            )
            self.color = self.controller.unit_cells[self.uc_id].site_colors[
                self.site.id
            ]
            self.size = self.controller.unit_cells[self.uc_id].site_sizes[
                self.site.id
            ]

            del self.controller.unit_cells[self.uc_id].sites[self.site_id]
            del self.controller.unit_cells[self.uc_id].site_colors[
                self.site.id
            ]
            del self.controller.unit_cells[self.uc_id].site_sizes[self.site.id]
        # No site selected, therefore remove the unit cell from the model
        elif self.uc_id:
            self.item = copy.deepcopy(self.controller.unit_cells[self.uc_id])
            del self.controller.unit_cells[self.uc_id]

        self.controller._remove_tree_item(
            self.uc_id, self.site_id, self.state_id
        )

    def undo(self):
        if self.state_id:
            unit_cell = self.controller.unit_cells[self.uc_id]
            site = unit_cell.sites[self.site_id]
            site.states[self.item.id] = self.item
            self.controller._add_tree_item(
                self.uc_id, self.site_id, self.item.id
            )

        elif self.site_id:
            unit_cell = self.controller.unit_cells[self.uc_id]
            unit_cell.sites[self.item.id] = self.item
            self.controller.unit_cells[self.uc_id].site_colors[
                self.site.id
            ] = self.color
            self.controller.unit_cells[self.uc_id].site_sizes[
                self.site.id
            ] = self.size

            self.controller._add_tree_item(self.uc_id, self.item.id)

        elif self.uc_id:
            self.controller.unit_cells[self.item.id] = self.item
            self.controller._add_tree_item(self.item.id)
