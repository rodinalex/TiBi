from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QUndoCommand
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QRadioButton
import uuid

from models import BasisVector, Selection, UnitCell
from views.uc_view import UnitCellView


class UpdateUnitCellParameterCommand(QUndoCommand):
    """
    Update a parameter of the selected `UnitCell`.

    This command is used to update the basis vectors of the unit cell
    when the user types in the spinbox.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to `UnitCell` objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
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
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
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
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
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

        self.uc_id = self.selection.unit_cell

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
        self.unit_cells[self.uc_id].bandstructure.clear()
        self.signal.emit()

    def undo(self):
        setattr(
            getattr(self.unit_cells[self.uc_id], self.vector),
            self.coordinate,
            self.old_value,
        )
        self.spinbox.setValue(self.old_value)
        self.unit_cells[self.uc_id].bandstructure.clear()
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
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
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
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        unit_cell_view: UnitCellView,
        signal: Signal,
    ):
        """
        Initialize the ReduceBasisCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
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

        self.uc_id = self.selection.unit_cell

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

            # Clear focus to avoid conflicts with programmatic
            # filling of the boxes
            focused_widget = QApplication.focusWidget()
            if focused_widget:
                focused_widget.clearFocus()
            QApplication.processEvents()

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

            # Clear focus to avoid conflicts with programmatic
            # filling of the boxes
            focused_widget = QApplication.focusWidget()
            if focused_widget:
                focused_widget.clearFocus()
            QApplication.processEvents()

            self.unit_cell_view.unit_cell_panel.set_basis_vectors(
                uc.v1, uc.v2, uc.v3
            )
            self.unit_cells[self.uc_id].bandstructure.clear()
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
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
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
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        unit_cell_view: UnitCellView,
        signal: Signal,
        dim: int,
        buttons: list[QRadioButton],
    ):
        """
        Initialize the ChangeDimensionalityCommand.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to `UnitCell` objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
        param : str
            The parameter to be updated (radius, color, etc.)
        unit_cell_view : UnitCellView
            Unit cell editing panel
        signal : Signal
            Signal to be emitted when the command is executed,
            requesting a plot update
        dim : int
            New dimensionality
        buttons : list[QRadioButton]
            Dimensionality radio buttons
        """
        super().__init__("Change dimensionality")
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_view = unit_cell_view
        self.signal = signal
        self.new_dim = dim
        self.buttons = buttons

        self.uc_id = self.selection.unit_cell
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
        self.unit_cells[self.uc_id].bandstructure.clear()
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
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
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
        selection: Selection,
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
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
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

        self.uc_id = self.selection.unit_cell
        self.site_id = self.selection.site

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
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
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
        selection: Selection,
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
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
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
        self.unit_cells[self.selection.unit_cell].sites[
            self.selection.site
        ].color = (
            color.redF(),
            color.greenF(),
            color.blueF(),
            color.alphaF(),
        )
