import copy
from PySide6.QtCore import QItemSelectionModel, Signal
from PySide6.QtGui import QStandardItem, QUndoCommand
import uuid

from TiBi.models import Selection, UnitCell
from TiBi.models.factories import (
    mk_new_unit_cell,
    mk_new_site,
    mk_new_state,
)
from TiBi.views.widgets import SystemTree


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

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    tree_view : SystemTree
        UI object containing the tree view
    unit_cell : UnitCell
        Newly created `UnitCell`
    """

    def __init__(
        self, unit_cells: dict[uuid.UUID, UnitCell], tree_view: SystemTree
    ):
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

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : Selection
        Dictionary containing the current selection
    tree_view : SystemTree
        UI object containing the tree view
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site : Site
        Newly created `Site`
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        tree_view: SystemTree,
    ):
        super().__init__("Add Site")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.uc_id = self.selection.unit_cell
        self.site = mk_new_site()

    # Add the newly-created site to the dictionary and create a tree item
    # Add entries to the size and colors dictionaries for the site
    def redo(self):
        unit_cell = self.unit_cells[self.uc_id]
        unit_cell.sites[self.site.id] = self.site
        self.tree_view.add_tree_item(self.site.name, self.uc_id, self.site.id)

    # Remove the unit cell from the dictionary and the tree using its id
    # Remove the color and size entries
    def undo(self):
        del self.unit_cells[self.uc_id].sites[self.site.id]
        self.tree_view.remove_tree_item(self.uc_id, self.site.id)


class AddStateCommand(QUndoCommand):
    """
    Create a new state in the currently selected site.

    Creates a state with default name, adds it to the
    states dictionary of the selected site and to the tree.

    The default state has:
    - Name: "New State"

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : Selection
        Model containing the current selection
    tree_view : SystemTree
        UI object containing the tree view
    signal : Signal
        Signal emitted when the state is added/removed
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site_id : uuid.UUID
        UUID of the selected `Site` when the command was issued
    state : State
        Newly created `State`
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        tree_view: SystemTree,
        signal: Signal,
    ):
        super().__init__("Add State")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.signal = signal
        self.uc_id = self.selection.unit_cell
        self.site_id = self.selection.site
        self.state = mk_new_state()

    # Add the newly-created state to the dictionary and create a tree item
    def redo(self):
        unit_cell = self.unit_cells[self.uc_id]
        site = unit_cell.sites[self.site_id]
        site.states[self.state.id] = self.state
        unit_cell.bandstructure.reset_bands()
        unit_cell.bz_grid.clear()
        self.tree_view.add_tree_item(
            self.state.name, self.uc_id, self.site_id, self.state.id
        )
        self.signal.emit()

    # Remove the site from the dictionary and the tree using its id
    def undo(self):
        del (
            self.unit_cells[self.uc_id]
            .sites[self.site_id]
            .states[self.state.id]
        )
        self.unit_cells[self.uc_id].bandstructure.reset_bands()
        self.unit_cells[self.uc_id].bz_grid.clear()
        self.tree_view.remove_tree_item(
            self.uc_id, self.site_id, self.state.id
        )
        self.signal.emit()


class DeleteItemCommand(QUndoCommand):
    """
    Delete the currently selected item from the model.

    This command handles deletion of `UnitCell`s, `Site`s, and `State`s
    based on the current selection. It updates both the data model and
    the tree view to reflect the deletion, and ensures that
    the selection is updated appropriately.

    The deletion follows the containment hierarchy:
    - Deleting a `UnitCell` also removes all its `Site`s and `State`s
    - Deleting a `Site` also removes all its `State`s
    - Deleting a `State` only removes that specific `State`

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : Selection
        Dictionary containing the current selection
    tree_view : SystemTree
        UI object containing the tree view
    signal : Signal
        Signal emitted when a state is added/removed
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site_id : uuid.UUID
        UUID of the selected `Site` when the command was issued
    state_id : uuid.UUID
        UUID of the selected `State` when the command was issued
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        tree_view: SystemTree,
        signal: Signal,
    ):
        super().__init__("Delete Item")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.signal = signal

        self.uc_id = self.selection.unit_cell
        self.site_id = self.selection.site
        self.state_id = self.selection.state

        # Save the item to be deleted for undo
        if self.state_id:
            self.item = copy.deepcopy(
                self.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
            )
        # No state selected, therefore remove the site from the unit cell
        elif self.site_id:
            self.item = copy.deepcopy(
                self.unit_cells[self.uc_id].sites[self.site_id]
            )

        # No site selected, therefore remove the unit cell from the model
        elif self.uc_id:
            self.item = copy.deepcopy(self.unit_cells[self.uc_id])

    # Delete the item
    def redo(self):
        if self.state_id:
            # Get the hoppings involving the states, remove them
            # from the hopping dictionary and store them to be used
            # in the undo method
            self.removed_hoppings = {}
            kept_hoppings = {}
            for k, v in self.unit_cells[self.uc_id].hoppings.items():
                if self.state_id in k:
                    self.removed_hoppings[k] = v
                else:
                    kept_hoppings[k] = v
            self.unit_cells[self.uc_id].hoppings = kept_hoppings
            self.unit_cells[self.uc_id].bandstructure.reset_bands()
            self.unit_cells[self.uc_id].bz_grid.clear()
            # Delete the selected state from the site
            del (
                self.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
            )
            self.signal.emit()

        # No state selected, therefore remove the site from the unit cell
        elif self.site_id:
            self.removed_hoppings = {}
            kept_hoppings = {}
            for state in (
                self.unit_cells[self.uc_id].sites[self.site_id].states.values()
            ):
                for k, v in self.unit_cells[self.uc_id].hoppings.items():
                    if state.id in k:
                        self.removed_hoppings[k] = v
                    else:
                        kept_hoppings[k] = v
            self.unit_cells[self.uc_id].hoppings = kept_hoppings
            if self.removed_hoppings:
                self.unit_cells[self.uc_id].bandstructure.reset_bands()
                self.unit_cells[self.uc_id].bz_grid.clear()
            # If the site has states, request a redraw of the hopping matrix
            if self.unit_cells[self.uc_id].sites[self.site_id].states:
                del self.unit_cells[self.uc_id].sites[self.site_id]
                self.signal.emit()
            else:
                del self.unit_cells[self.uc_id].sites[self.site_id]
        # No site selected, therefore remove the unit cell from the model
        elif self.uc_id:
            del self.unit_cells[self.uc_id]

        self.tree_view.remove_tree_item(
            self.uc_id, self.site_id, self.state_id
        )

    def undo(self):
        # Reinsert the item into the model
        if self.state_id:
            unit_cell = self.unit_cells[self.uc_id]
            site = unit_cell.sites[self.site_id]
            site.states[self.item.id] = self.item
            unit_cell.bandstructure.reset_bands()
            unit_cell.bz_grid.clear()
            unit_cell.hoppings.update(self.removed_hoppings)
            self.signal.emit()

        elif self.site_id:
            unit_cell = self.unit_cells[self.uc_id]
            unit_cell.sites[self.item.id] = self.item
            if self.removed_hoppings:
                unit_cell.bandstructure.reset_bands()
                unit_cell.bz_grid.clear()
            unit_cell.hoppings.update(self.removed_hoppings)
            # If the site has states, request a redraw of the hopping matrix
            if self.unit_cells[self.uc_id].sites[self.site_id].states:
                self.signal.emit()
        elif self.uc_id:
            self.unit_cells[self.item.id] = self.item

        # Refresh the tree and select the item
        self.tree_view.refresh_tree(self.unit_cells)
        index = self.tree_view.find_item_by_id(
            uc_id=self.uc_id, site_id=self.site_id, state_id=self.state_id
        ).index()
        self.tree_view.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.ClearAndSelect
        )


class RenameTreeItemCommand(QUndoCommand):
    """
    Change the name of a tree item in the unit cells model.

    The name is changed by double-clicking on an item in the tree view.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : Selection
        Dictionary containing the current selection
    tree_view : SystemTree
        UI object containing the tree view
    signal : Signal
        Signal to be emitted when the command is executed
    item : QStandardItem
        The item in the tree view that was changed
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site_id : uuid.UUID
        UUID of the selected `Site` when the command was issued
    state_id : uuid.UUID
        UUID of the selected `State` when the command was issued
    old_name : str
        The old name of the item before the change
    new_name : str
        The new name of the item after the change
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        tree_view: SystemTree,
        signal: Signal,
        item: QStandardItem,
    ):
        super().__init__("Rename Tree Item")

        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.signal = signal
        self.new_name = item.text()

        self.uc_id = self.selection.unit_cell
        self.site_id = self.selection.site
        self.state_id = self.selection.state

        # Get the old name
        if self.state_id:
            self.old_name = (
                self.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
                .name
            )
        elif self.site_id:
            self.old_name = (
                self.unit_cells[self.uc_id].sites[self.site_id].name
            )
        else:
            self.old_name = self.unit_cells[self.uc_id].name

    def redo(self):
        item = self.tree_view.find_item_by_id(
            self.uc_id, self.site_id, self.state_id
        )
        if self.state_id:
            self.unit_cells[self.uc_id].sites[self.site_id].states[
                self.state_id
            ].name = self.new_name

        elif self.site_id:
            self.unit_cells[self.uc_id].sites[
                self.site_id
            ].name = self.new_name
        else:
            self.unit_cells[self.uc_id].name = self.new_name

        item.setText(self.new_name)
        self.signal.emit()

    def undo(self):
        item = self.tree_view.find_item_by_id(
            self.uc_id, self.site_id, self.state_id
        )
        if self.state_id:
            self.unit_cells[self.uc_id].sites[self.site_id].states[
                self.state_id
            ].name = self.old_name

        elif self.site_id:
            self.unit_cells[self.uc_id].sites[
                self.site_id
            ].name = self.old_name
        else:
            self.unit_cells[self.uc_id].name = self.old_name

        item.setText(self.old_name)
        self.signal.emit()
