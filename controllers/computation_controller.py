from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack
import uuid

from .bands_controller import BandsController
from .hopping_controller import HoppingController
from models import DataModel, UnitCell
from views.computation_view import ComputationView


class ComputationController(QObject):
    """
    Controller responsible for physics calculations within the application.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : DataModel
        `DataModel` tracking the current selection
    computation_view : ComputationView
        UI object containing the computation view


    Signals
    -------
    status_updated
        Signal emitted to update the status of the computation
    band_computation_completed
        Signal notifying that the data can be plotted
    """

    status_updated = Signal(str)
    band_computation_completed = Signal()
    projection_selection_changed = Signal(object)

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        computation_view: ComputationView,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the computation controller.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : DataModel
            `DataModel` tracking the current selection
        computation_view : ComputationView
            UI object containing the computation view
        undo_stack : QUndoStack
            `QUndoStack` to hold "undo-able" commands
        """
        super().__init__()
        self.computation_view = computation_view
        self.undo_stack = undo_stack

        self.unit_cells = unit_cells
        self.selection = selection
        # Component controllers
        self.hopping_controller = HoppingController(
            self.unit_cells,
            self.selection,
            self.computation_view.hopping_panel,
            self.undo_stack,
        )
        self.bands_controller = BandsController(
            self.computation_view.bands_panel
        )
        # Connect the signals

    #     self.selection.signals.updated.connect(self._handle_selection_changed)
    #     self.computation_view.bands_panel.select_all_btn.clicked.connect(
    #         self.computation_view.bands_panel.proj_combo.select_all
    #     )
    #     self.computation_view.bands_panel.clear_all_btn.clicked.connect(
    #         self.computation_view.bands_panel.proj_combo.clear_selection
    #     )
    #     self.computation_view.bands_panel.proj_combo.selection_changed.connect(
    #         self.projection_selection_changed.emit
    #     )

    # def _handle_selection_changed(self):
    #     """
    #     Update the state projection box when the selection changes.

    #     In addition to usual selection change by click,
    #     the selection can change when items are added or removed to/from
    #     the tree.
    #     """
    #     uc_id = self.selection["unit_cell"]
    #     if uc_id:
    #         unit_cell = self.unit_cells[uc_id]
    #         _, state_info = unit_cell.get_states()
    #         state_info_strings = [f"{x[0]} : {x[2]}" for x in state_info]
    #         self.computation_view.bands_panel.proj_combo.refresh_combo(
    #             state_info_strings
    #         )
