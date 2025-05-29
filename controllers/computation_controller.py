from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack
import uuid

from .bands_controller import BandsController
from .hopping_controller import HoppingController
from models import Selection, UnitCell
from views.computation_view import ComputationView


class ComputationController(QObject):
    """
    Controller responsible for physics calculations within the application.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the current selection
    computation_view : ComputationView
        UI object containing the computation view

    Methods
    -------
    get_pair_selection()
        Get the selected state pair from the hopping matrix, if any.
    update_hopping_panel()
        Redraw the hoppings panel.

    Signals
    -------
    status_updated
        Signal emitted to update the status of the computation
    bands_computed
        Signal notifying that the band computation is done
    """

    status_updated = Signal(str)

    # Hopping controller signals to relay
    hopping_segments_requested = Signal()
    selection_requested = Signal(object, object, object)
    # Band controller signals to relay
    bands_computed = Signal()
    projection_selection_changed = Signal(object)

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        computation_view: ComputationView,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the computation controller.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            `Selection` tracking the current selection
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
            self.unit_cells, self.selection, self.computation_view.bands_panel
        )
        # Connect the signals
        # Hoppings Panel
        self.hopping_controller.hopping_segments_requested.connect(
            self.hopping_segments_requested.emit
        )
        self.hopping_controller.selection_requested.connect(
            self.selection_requested.emit
        )
        # Bands Panel
        self.bands_controller.bands_computed.connect(
            self._handle_bands_computed
        )
        self.bands_controller.status_updated.connect(self.status_updated.emit)
        self.bands_controller.projection_selection_changed.connect(
            self.projection_selection_changed.emit
        )

    def get_pair_selection(self):
        """
        Get the selected state pair from the hopping matrix, if any.

        Returns
        -------
        list[tuple]  | list[None]
            List of selected states, if available, where the elements of
            the list are (site_name, site_id, state_name, state_id).
        """
        return self.hopping_controller.pair_selection

    def update_hopping_panel(self):
        """
        Redraw the hoppings panel.

        This method is called when the user renames a tree item to make sure
        that the matrix table contains the correct item names.
        """
        self.hopping_controller.update_unit_cell()

    def set_dimensionality(self):
        self.bands_controller.update_bands_panel()

    def _handle_bands_computed(self):
        # Update the projection combo box
        self.bands_controller.update_combo()
        self.bands_computed.emit()

    def update_projection_combo(self):
        self.bands_controller.update_combo()

    def get_projection_indices(self):
        return self.bands_controller.get_projection_indices()
