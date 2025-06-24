import copy
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand

from TiBi.models import UnitCell
from TiBi.views.computation_view import ComputationView


class AddBZPointCommand(QUndoCommand):
    """
    Add a point to the special points path in the Brillouin zone.

    Because this action would invalidate the already-calculated bands,
    the band structure is reset.

    Attributes
    ----------
    unit_cell : UnitCell
        `UnitCell` to which the point will be addeed
    point : NDArray[np.float64]
        The point to be added
    computation_view : ComputationView
        UI object containing the computation view
    signal : Signal
        Signal to be emitted to trigger a redraw of the BZ path
    """

    def __init__(
        self,
        unit_cell: UnitCell,
        point: NDArray[np.float64],
        computation_view: ComputationView,
        signal: Signal,
    ):
        super().__init__("Add BZ Path Point")
        self.unit_cell = unit_cell
        self.point = point
        self.computation_view = computation_view
        self.signal = signal

    def redo(self):

        self.unit_cell.bandstructure.add_point(self.point)
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

        self.unit_cell.bandstructure.remove_point()
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

    Because this action would invalidate the already-calculated bands,
    the band structure is reset.

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
        super().__init__("Remove BZ Path Point")
        self.unit_cell = unit_cell
        self.computation_view = computation_view
        self.signal = signal

        self.point = copy.deepcopy(
            self.unit_cell.bandstructure.special_points[-1]
        )

    def redo(self):
        self.unit_cell.bandstructure.remove_point()
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
        self.unit_cell.bandstructure.add_point(self.point)
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


class ClearBZPathCommand(QUndoCommand):
    """
    Clear the special points path in the Brillouin zone.

    Because this action would invalidate the already-calculated bands,
    the band structure is reset.

    Attributes
    ----------
    unit_cell : UnitCell
        `UnitCell` whose path will be cleared
    special_points : list[NDArray[np.float64]]
        List of special points before clearing the path
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
        super().__init__("Add BZ Path Point")
        self.unit_cell = unit_cell
        self.computation_view = computation_view
        self.signal = signal

        self.special_points = copy.deepcopy(
            self.unit_cell.bandstructure.special_points
        )

    def redo(self):
        self.unit_cell.bandstructure.clear()
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
        self.unit_cell.bandstructure.clear()
        self.unit_cell.bandstructure.special_points = copy.deepcopy(
            self.special_points
        )
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
