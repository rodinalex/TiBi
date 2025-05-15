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

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
    ):
        """
        Initialize the command.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: Dictionary containing the current selection
            tree_view: UI object containing the tree view
        """
        super().__init__("Add Site")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.uc_id = self.selection["unit_cell"]
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
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
    ):
        """
        Initialize the command.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: Dictionary containing the current selection
            tree_view: UI object containing the tree view
        """
        super().__init__("Add State")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.uc_id = self.selection["unit_cell"]
        self.site_id = self.selection["site"]
        self.state = mk_new_state()

    # Add the newly-created state to the dictionary and create a tree item
    def redo(self):
        unit_cell = self.unit_cells[self.uc_id]
        site = unit_cell.sites[self.site_id]
        site.states[self.state.id] = self.state
        self.tree_view.add_tree_item(
            self.state.name, self.uc_id, self.site_id, self.state.id
        )

    # Remove the site from the dictionary and the tree using its id
    def undo(self):
        del (
            self.unit_cells[self.uc_id]
            .sites[self.site_id]
            .states[self.state.id]
        )
        self.tree_view.remove_tree_item(
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
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
    ):
        """
        Initialize the command.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: Dictionary containing the current selection
            tree_view: UI object containing the tree view
        """
        super().__init__("Delete Item")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view

        self.uc_id = self.selection.get("unit_cell", None)
        self.site_id = self.selection.get("site", None)
        self.state_id = self.selection.get("state", None)

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
            # Delete the selected state from the site
            del (
                self.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
            )
        # No state selected, therefore remove the site from the unit cell
        elif self.site_id:
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

        elif self.site_id:
            unit_cell = self.unit_cells[self.uc_id]
            unit_cell.sites[self.item.id] = self.item

        elif self.uc_id:
            self.unit_cells[self.item.id] = self.item

        # Refresh the tree and select the item
        self.tree_view.refresh_tree(self.unit_cells)
        index = self.tree_view.find_item_by_id(self.item.id).index()
        self.tree_view.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.ClearAndSelect
        )


class RenameTreeItemCommand(QUndoCommand):
    """
    Change the name of the selected item by double-clicking on it in
    the tree view. Update the data and save it.
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
        signal: Signal,
        item: QStandardItem,
    ):
        super().__init__("Rename Tree Item")

        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view
        self.item_changed = signal
        self.new_name = item.text()

        self.uc_id = self.selection.get("unit_cell", None)
        self.site_id = self.selection.get("site", None)
        self.state_id = self.selection.get("state", None)

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
        item.setText(self.new_name)
        self.item_changed.emit()

    def undo(self):
        item = self.tree_view.find_item_by_id(
            self.uc_id, self.site_id, self.state_id
        )
        item.setText(self.old_name)
        self.item_changed.emit()


class UpdateUnitCellParameterCommand(QUndoCommand):
    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        vector: str,
        coordinate: str,
        spinbox: QDoubleSpinBox,
        signal: Signal,
    ):
        super().__init__("Update Unit Cell Parameter")
        self.unit_cells = unit_cells
        self.selection = selection
        self.vector = vector
        self.coordinate = coordinate
        self.spinbox = spinbox
        self.signal = signal
        self.new_value = self.spinbox.value()

        self.uc_id = self.selection.get("unit_cell", None)

        self.old_value = getattr(
            getattr(self.unit_cells[self.uc_id], self.vector),
            self.coordinate,
        )

    def redo(self):
        setattr(
            getattr(self.unit_cells[self.uc_id], self.vector),
            self.coordinate,
            self.new_value,
        )
        self.spinbox.setValue(self.new_value)
        self.signal.emit()

    def undo(self):
        setattr(
            getattr(self.unit_cells[self.uc_id], self.vector),
            self.coordinate,
            self.old_value,
        )
        self.spinbox.setValue(self.old_value)
        self.signal.emit()


class ReduceBasisCommand(QUndoCommand):
    """
    Reduce the basis vectors of the selected unit cell.

    This method applies the Lenstra-Lenstra-Lovász (LLL) lattice
    reduction algorithm to find a more orthogonal set of basis
    vectors that spans the same lattice.
    This is useful for finding a 'nicer' representation of the unit cell
    with basis vectors that are shorter and more orthogonal to each other.

    The method only affects the periodic directions of the unit cell. After
    reduction, the UI is updated to reflect the new basis vectors.
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        unit_cell_view: UnitCellView,
        signal: Signal,
    ):
        super().__init__("Update Site Parameter")
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_view = unit_cell_view
        self.signal = signal

        self.uc_id = self.selection.get("unit_cell", None)

        if self.uc_id:
            uc = self.unit_cells[self.uc_id]
            self.old_basis = [uc.v1, uc.v2, uc.v3]
            self.new_basis = uc.reduced_basis()

    def redo(self):
        if self.uc_id:
            uc = self.unit_cells[self.uc_id]
            uc.v1 = self.new_basis[0]
            uc.v2 = self.new_basis[1]
            uc.v3 = self.new_basis[2]

            self.unit_cell_view.unit_cell_panel.set_basis_vectors(
                uc.v1, uc.v2, uc.v3
            )
            self.signal.emit()

    def undo(self):
        if self.uc_id:
            uc = self.unit_cells[self.uc_id]
            uc.v1 = self.old_basis[0]
            uc.v2 = self.old_basis[1]
            uc.v3 = self.old_basis[2]

            self.unit_cell_view.unit_cell_panel.set_basis_vectors(
                uc.v1, uc.v2, uc.v3
            )
            self.signal.emit()


class ChangeDimensionalityCommand(QUndoCommand):
    """
    Handle changes in the dimensionality selection (0D, 1D, 2D, 3D).

    This method is called when the user selects a different dimensionality
    radio button.
    It updates the unit cell's periodicity flags and enables/disables
    appropriate basis vector components based on
    the selected dimensionality.

    For example:
    - 0D: All directions are non-periodic (isolated system)
    - 1D: First direction is periodic, others are not
    - 2D: First and second directions are periodic, third is not
    - 3D: All directions are periodic (fully periodic crystal)
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        unit_cell_view: UnitCellView,
        signal: Signal,
        dim: int,
        buttons: list[QRadioButton],
    ):
        super().__init__("Change dimensionality")
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_view = unit_cell_view
        self.signal = signal
        self.new_dim = dim
        self.buttons = buttons

        self.uc_id = self.selection.get("unit_cell", None)
        uc = self.unit_cells[self.uc_id]
        self.old_v1 = uc.v1
        self.old_v2 = uc.v2
        self.old_v3 = uc.v3
        self.old_dim = (
            uc.v1.is_periodic + uc.v2.is_periodic + uc.v3.is_periodic
        )

        if dim == 0:
            self.new_v1 = BasisVector(1, 0, 0, False)
            self.new_v2 = BasisVector(0, 1, 0, False)
            self.new_v3 = BasisVector(0, 0, 1, False)

        elif dim == 1:
            self.new_v1 = BasisVector(self.old_v1.x, 0, 0, True)
            self.new_v2 = BasisVector(0, self.old_v2.y, 0, False)
            self.new_v3 = BasisVector(0, 0, self.old_v3.z, False)

        elif dim == 2:
            self.new_v1 = BasisVector(self.old_v1.x, self.old_v1.y, 0, True)
            self.new_v2 = BasisVector(self.old_v2.x, self.old_v2.y, 0, True)
            self.new_v3 = BasisVector(0, 0, self.old_v3.z, False)

        else:
            self.new_v1 = BasisVector(
                self.old_v1.x, self.old_v1.y, self.old_v1.z, True
            )
            self.new_v2 = BasisVector(
                self.old_v2.x, self.old_v2.y, self.old_v2.z, True
            )
            self.new_v3 = BasisVector(
                self.old_v3.x, self.old_v3.y, self.old_v3.z, True
            )

    def redo(self):

        self._set_vector_enables(self.new_dim)

        uc = self.unit_cells[self.uc_id]
        uc.v1 = self.new_v1
        uc.v2 = self.new_v2
        uc.v3 = self.new_v3

        self.unit_cell_view.unit_cell_panel.set_basis_vectors(
            uc.v1, uc.v2, uc.v3
        )

        self._set_checked_button(self.new_dim)
        self.signal.emit()

    def undo(self):

        self._set_vector_enables(self.old_dim)

        uc = self.unit_cells[self.uc_id]
        uc.v1 = self.old_v1
        uc.v2 = self.old_v2
        uc.v3 = self.old_v3

        self.unit_cell_view.unit_cell_panel.set_basis_vectors(
            uc.v1, uc.v2, uc.v3
        )

        self._set_checked_button(self.old_dim)
        self.signal.emit()

    def _set_vector_enables(self, dim):
        self.unit_cell_view.unit_cell_panel.v1[0].setEnabled(True)
        self.unit_cell_view.unit_cell_panel.v1[1].setEnabled(dim > 1)
        self.unit_cell_view.unit_cell_panel.v1[2].setEnabled(dim > 2)

        self.unit_cell_view.unit_cell_panel.v2[0].setEnabled(dim > 1)
        self.unit_cell_view.unit_cell_panel.v2[1].setEnabled(True)
        self.unit_cell_view.unit_cell_panel.v2[2].setEnabled(dim > 2)

        self.unit_cell_view.unit_cell_panel.v3[0].setEnabled(dim > 2)
        self.unit_cell_view.unit_cell_panel.v3[1].setEnabled(dim > 2)
        self.unit_cell_view.unit_cell_panel.v3[2].setEnabled(True)

    def _set_checked_button(self, dim):
        for btn in self.buttons:
            btn.blockSignals(True)
        self.buttons[dim].setChecked(True)
        for btn in self.buttons:
            btn.blockSignals(False)


class UpdateSiteParameterCommand(QUndoCommand):
    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        param: str,
        spinbox: QDoubleSpinBox,
        signal: Signal,
    ):
        super().__init__("Update Site Parameter")
        self.unit_cells = unit_cells
        self.selection = selection
        self.param = param
        self.spinbox = spinbox
        self.signal = signal
        self.new_value = self.spinbox.value()

        self.uc_id = self.selection.get("unit_cell", None)
        self.site_id = self.selection.get("site", None)

        self.old_value = getattr(
            self.unit_cells[self.uc_id].sites[self.site_id],
            self.param,
        )

    def redo(self):
        setattr(
            self.unit_cells[self.uc_id].sites[self.site_id],
            self.param,
            self.new_value,
        )
        self.spinbox.setValue(self.new_value)
        self.signal.emit()

    def undo(self):
        setattr(
            self.unit_cells[self.uc_id].sites[self.site_id],
            self.param,
            self.old_value,
        )
        self.spinbox.setValue(self.old_value)
        self.signal.emit()


class ChangeSiteColorCommand(QUndoCommand):
    """
    Use a color dialog to choose a color for the selected site to be used
    in the UC plot.
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        new_color: QColor,
        old_color: QColor,
        unit_cell_view: UnitCellView,
        signal: Signal,
    ):
        super().__init__("Update Site Parameter")
        self.unit_cells = unit_cells
        self.selection = selection
        self.new_color = new_color
        self.old_color = old_color
        self.unit_cell_view = unit_cell_view
        self.signal = signal

    def redo(self):
        self._set_color(self.new_color)
        self.signal.emit()

    def undo(self):
        self._set_color(self.old_color)
        self.signal.emit()

    def _set_color(self, color):
        rgba = (
            f"rgba({color.red()}, "
            f"{color.green()}, "
            f"{color.blue()}, "
            f"{color.alpha()})"
        )
        self.unit_cell_view.site_panel.color_picker_btn.setStyleSheet(
            f"background-color: {rgba};"
        )

        # Update the color in the dictionary (0-1 scale)
        self.unit_cells[self.selection["unit_cell"]].sites[
            self.selection["site"]
        ].color = (
            color.redF(),
            color.greenF(),
            color.blueF(),
            color.alphaF(),
        )
