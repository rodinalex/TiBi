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
        """
        Initialize the AddUnitCellCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        tree_view : SystemTree
            UI object containing the tree view
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

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
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
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
    ):
        """
        Initialize the AddSiteCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        tree_view : SystemTree
            UI object containing the tree view
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

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    tree_view : SystemTree
        UI object containing the tree view
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
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
    ):
        """
        Initialize the AddStateCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        tree_view : SystemTree
            UI object containing the tree view
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
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    tree_view : SystemTree
        UI object containing the tree view
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site_id : uuid.UUID
        UUID of the selected `Site` when the command was issued
    state_id : uuid.UUID
        UUID of the selected `State` when the command was issued
    bandstructure : BandStructure
        The band structure of the unit cell before the change
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
    ):
        """
        Initialize the DeleteItemCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
                Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        tree_view : SystemTree
            UI object containing the tree view
        """
        super().__init__("Delete Item")
        self.unit_cells = unit_cells
        self.selection = selection
        self.tree_view = tree_view

        self.uc_id = self.selection.get("unit_cell", None)
        self.site_id = self.selection.get("site", None)
        self.state_id = self.selection.get("state", None)

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

        self.bandstructure = copy.deepcopy(
            self.unit_cells[self.uc_id].bandstructure
        )

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
            # If some of the hoppings were removed, reset the band structure
            if self.removed_hoppings:
                self.unit_cells[self.uc_id].bandstructure.reset_bands()
            else:
                self.unit_cells[self.uc_id].bandstructure = copy.deepcopy(
                    self.bandstructure
                )
            # Delete the selected state from the site
            del (
                self.unit_cells[self.uc_id]
                .sites[self.site_id]
                .states[self.state_id]
            )
        # No state selected, therefore remove the site from the unit cell
        elif self.site_id:
            self.bandstructure = self.unit_cells[self.uc_id].bandstructure
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
            # If some of the hoppings were removed, reset the band structure
            if self.removed_hoppings:
                self.unit_cells[self.uc_id].bandstructure.reset_bands()
            else:
                self.unit_cells[self.uc_id].bandstructure = copy.deepcopy(
                    self.bandstructure
                )
            # Delete the selected site from the unit cell
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
            unit_cell.hoppings.update(self.removed_hoppings)
            unit_cell.bandstructure = copy.deepcopy(self.bandstructure)

        elif self.site_id:
            unit_cell = self.unit_cells[self.uc_id]
            unit_cell.sites[self.item.id] = self.item
            unit_cell.hoppings.update(self.removed_hoppings)
            unit_cell.bandstructure = copy.deepcopy(self.bandstructure)

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
    Change the name of a tree item in the unit cells model.

    The name is changed by double-clicking on an item in the tree view.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
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
        selection: dict[str, uuid.UUID],
        tree_view: SystemTree,
        signal: Signal,
        item: QStandardItem,
    ):
        """
        Initialize the RenameTreeItemCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        tree_view : SystemTree
            UI object containing the tree view
        signal : Signal
            Signal to be emitted when the command is executed
        item : QStandardItem
            The item in the tree view that was changed
        """
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
        self.item_changed.emit()

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
        self.item_changed.emit()


class UpdateUnitCellParameterCommand(QUndoCommand):
    """
    Update a parameter of the selected `UnitCell`.

    This command is used to update the basis vectors of the unit cell
    when the user types in the spinbox.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    vector : str
        The vector to be updated (v1, v2, or v3)
    coordinate : str
        The coordinate to be updated (x, y, or z)
    spinbox : QDoubleSpinBox
        The spinbox widget used to input the new value
    signal : Signal
        Signal to be emitted when the command is executed,
        requesting a plot update
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    old_value : float
        The old value of the parameter before the change
    new_value : float
        The new value of the parameter after the change
    bandstructure : BandStructure
        The band structure of the unit cell before the change
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        vector: str,
        coordinate: str,
        spinbox: QDoubleSpinBox,
        signal: Signal,
    ):
        """
        Initialize the UpdateUnitCellParameterCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        vector : str
            The vector to be updated (v1, v2, or v3)
        coordinate : str
            The coordinate to be updated (x, y, or z)
        spinbox : QDoubleSpinBox
            The spinbox widget used to input the new value
        signal : Signal
            Signal to be emitted when the command is executed,
            requesting a plot update
        """
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
        self.bandstructure = copy.deepcopy(
            self.unit_cells[self.uc_id].bandstructure
        )

    def redo(self):
        setattr(
            getattr(self.unit_cells[self.uc_id], self.vector),
            self.coordinate,
            self.new_value,
        )
        self.spinbox.setValue(self.new_value)
        self.unit_cells[self.uc_id].bandstructure.clear()
        self.signal.emit()

    def undo(self):
        setattr(
            getattr(self.unit_cells[self.uc_id], self.vector),
            self.coordinate,
            self.old_value,
        )
        self.spinbox.setValue(self.old_value)
        self.unit_cells[self.uc_id].bandstructure = copy.deepcopy(
            self.bandstructure
        )
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

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    unit_cell_view : UnitCellView
        UI object containing the unit cell view
    signal : Signal
        Signal to be emitted when the command is executed,
        requesting a plot update
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    old_basis : list[BasisVector]
        The old basis vectors of the unit cell before reduction
    new_basis : list[BasisVector]
        The new basis vectors of the unit cell after reduction
    bandstructure : BandStructure
        The band structure of the unit cell before the change
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        unit_cell_view: UnitCellView,
        signal: Signal,
    ):
        """
        Initialize the ReduceBasisCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        unit_cell_view : UnitCellView
            UI object containing the unit cell view
        signal : Signal
            Signal to be emitted when the command is executed,
            requesting a plot update
        """
        super().__init__("Reduce Basis")
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_view = unit_cell_view
        self.signal = signal

        self.uc_id = self.selection.get("unit_cell", None)

        if self.uc_id:
            uc = self.unit_cells[self.uc_id]
            self.old_basis = [uc.v1, uc.v2, uc.v3]
            self.new_basis = uc.reduced_basis()
            self.bandstructure = copy.deepcopy(
                self.unit_cells[self.uc_id].bandstructure
            )

    def redo(self):
        if self.uc_id:
            uc = self.unit_cells[self.uc_id]
            uc.v1 = self.new_basis[0]
            uc.v2 = self.new_basis[1]
            uc.v3 = self.new_basis[2]

            self.unit_cell_view.unit_cell_panel.set_basis_vectors(
                uc.v1, uc.v2, uc.v3
            )
            self.unit_cells[self.uc_id].bandstructure.clear()
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
            self.unit_cells[self.uc_id].bandstructure = copy.deepcopy(
                self.bandstructure
            )
            self.signal.emit()


class ChangeDimensionalityCommand(QUndoCommand):
    """
    Change the dimensionality of the selected `UnitCell` (0D, 1D, 2D, 3D).

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

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    unit_cell_view : UnitCellView
        UI object containing the unit cell view
    signal : Signal
        Signal to be emitted when the command is executed,
        requesting a plot update
    dim : int
        The new dimensionality of the unit cell (0, 1, 2, or 3)
    buttons : list[QRadioButton]
        List of radio buttons corresponding to the dimensionality
        options in the UI
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    old_v1 : BasisVector
        The old basis vector 1 of the unit cell before the change
    old_v2 : BasisVector
        The old basis vector 2 of the unit cell before the change
    old_v3 : BasisVector
        The old basis vector 3 of the unit cell before the change
    old_dim : int
        The old dimensionality of the unit cell before the change
    new_v1 : BasisVector
        The new basis vector 1 of the unit cell after the change
    new_v2 : BasisVector
        The new basis vector 2 of the unit cell after the change
    new_v3 : BasisVector
        The new basis vector 3 of the unit cell after the change
    bandstructure : BandStructure
        The band structure of the unit cell before the change
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
        self.bandstructure = copy.deepcopy(
            self.unit_cells[self.uc_id].bandstructure
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
        self.unit_cells[self.uc_id].bandstructure.clear()

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
        self.unit_cells[self.uc_id].bandstructure = copy.deepcopy(
            self.bandstructure
        )

        self.signal.emit()

    def _set_vector_enables(self, dim):
        """
        Enable or disable the basis vector components.

        The enabling/disabling is based on the
        dimensionality of the unit cell.

        Parameters
        ----------
        dim : int
            The new dimensionality of the unit cell (0, 1, 2, or 3)
        """
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
        """
        Set the radio button corresponding to the dimensionality.

        The radio button is checked and all others are unchecked.
        This is done by blocking signals to avoid triggering
        the button's clicked signal when setting the checked state.

        Parameters
        ----------
        dim : int
            The new dimensionality of the unit cell (0, 1, 2, or 3)
        """
        for btn in self.buttons:
            btn.blockSignals(True)
        self.buttons[dim].setChecked(True)
        for btn in self.buttons:
            btn.blockSignals(False)


class UpdateSiteParameterCommand(QUndoCommand):
    """
    Update a parameter of the selected `Site`.

    This command is used to update the basis vectors of the site
    when the user types in the spinbox.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    param : str
        The parameter to be updated (radius, color, etc.)
    spinbox : QDoubleSpinBox
        The spinbox widget used to input the new value
    signal : Signal
        Signal to be emitted when the command is executed,
        requesting a plot update
    uc_id : uuid.UUID
        UUID of the selected `UnitCell` when the command was issued
    site_id : uuid.UUID
        UUID of the selected `Site` when the command was issued
    old_value : float
        The old value of the parameter before the change
    new_value : float
        The new value of the parameter after the change
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: dict[str, uuid.UUID],
        param: str,
        spinbox: QDoubleSpinBox,
        signal: Signal,
    ):
        """
        Initialize the UpdateSiteParameterCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        param : str
            The parameter to be updated (radius, color, etc.)
        spinbox : QDoubleSpinBox
            The spinbox widget used to input the new value
        signal : Signal
            Signal to be emitted when the command is executed,
            requesting a plot update
        """
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
    Change the color of the selected `Site`.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : dict[str, uuid.UUID]
        Dictionary containing the current selection
    new_color : QColor
        The new color to be set for the site
    old_color : QColor
        The old color of the site before the change
    unit_cell_view : UnitCellView
        UI object containing the unit cell view
    signal : Signal
        Signal to be emitted when the command is executed,
        requesting a plot update
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
        """
        Initialize the ChangeSiteColorCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : dict[str, uuid.UUID]
            Dictionary containing the current selection
        new_color : QColor
            The new color to be set for the site
        old_color : QColor
            The old color of the site before the change
        unit_cell_view : UnitCellView
            UI object containing the unit cell view
        signal : Signal
            Signal to be emitted when the command is executed,
            requesting a plot update
        """
        super().__init__("Change Site Color")
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
