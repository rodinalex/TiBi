import copy
from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand

from src.tibitypes import UnitCell
from views.computation_view import ComputationView


class AddBZPointCommand(QUndoCommand):
    """
    Add a point to the special points path in the Brillouin zone.

    Attributes
    ----------
    unit_cell : UnitCell
        `UnitCell` to which the point will be addeed
    point : NDArray
        The point to be added
    computation_view : ComputationView
        UI object containing the computation view
    signal : Signal
        Signal to be emitted to trigger a redraw of the BZ path
    """

    def __init__(
        self,
        unit_cell: UnitCell,
        point: NDArray,
        computation_view: ComputationView,
        signal: Signal,
    ):
        """
        Initialize the AddBZPointCommand.

        Parameters
        ----------
        unit_cell : UnitCell
            `UnitCell` to which the point will be addeed
        point : NDArray
            The point to be added
        computation_view : ComputationView
            UI object containing the computation view
        signal : Signal
            Signal to be emitted to trigger a redraw of the BZ path
        """
        super().__init__("Add BZ Path Point")
        self.unit_cell = unit_cell
        self.point = point
        self.computation_view = computation_view
        self.signal = signal

    def redo(self):
        self.unit_cell.bandstructure.special_points.append(self.point)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()

    def undo(self):
        self.unit_cell.bandstructure.special_points.pop(-1)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()


class RemoveBZPointCommand(QUndoCommand):
    """
    Remove the last point from the special points path in the Brillouin zone.

    Attributes
    ----------
    unit_cell : UnitCell
        `UnitCell` from which the point will be removed
    point : NDArray
        The point to be removed
    computation_view : ComputationView
        UI object containing the computation view
    signal : Signal
        Signal to be emitted to trigger a redraw of the BZ path
    """

    def __init__(
        self,
        unit_cell: UnitCell,
        computation_view: ComputationView,
        signal: Signal,
    ):
        """
        Initialize the AddBZPointCommand.

        Parameters
        ----------
        unit_cell : UnitCell
            `UnitCell` from which the point will be removed
        computation_view : ComputationView
            UI object containing the computation view
        signal : Signal
            Signal to be emitted to trigger a redraw of the BZ path
        """
        super().__init__("Add BZ Path Point")
        self.unit_cell = unit_cell
        self.computation_view = computation_view
        self.signal = signal

        self.point = self.unit_cell.bandstructure.special_points[-1]

    def redo(self):
        self.unit_cell.bandstructure.special_points.pop(-1)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()

    def undo(self):
        self.unit_cell.bandstructure.special_points.append(self.point)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()


class ClearBZPointCommand(QUndoCommand):
    """
    Clear the special points path in the Brillouin zone.

    Attributes
    ----------
    unit_cell : UnitCell
        `UnitCell` from which the point will be removed
    bz_path : NDArray
        The path to be cleared
    computation_view : ComputationView
        UI object containing the computation view
    signal : Signal
        Signal to be emitted to trigger a redraw of the BZ path
    """

    def __init__(
        self,
        unit_cell: UnitCell,
        computation_view: ComputationView,
        signal: Signal,
    ):
        """
        Initialize the AddBZPointCommand.

        Parameters
        ----------
        unit_cell : UnitCell
            `UnitCell` from which the point will be removed
        computation_view : ComputationView
            UI object containing the computation view
        signal : Signal
            Signal to be emitted to trigger a redraw of the BZ path
        """
        super().__init__("Add BZ Path Point")
        self.unit_cell = unit_cell
        self.computation_view = computation_view
        self.signal = signal

        self.bz_path = copy.deepcopy(
            self.unit_cell.bandstructure.special_points
        )

    def redo(self):
        self.unit_cell.bandstructure.special_points.clear()
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()

    def undo(self):
        self.unit_cell.bandstructure.special_points.extend(self.bz_path)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()
