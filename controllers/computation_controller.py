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
        Model tracking the currently selected unit cell, site, and state
    computation_view : ComputationView
        UI object containing the computation view
    hopping_controller : HoppingController
        Child controller in charge of the hopping panel of the computation UI
    bands_controller : BandsController
        Child controller in charge of the bands panel of the computation UI

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
    bands_plot_requested
        Request bands plot.
        Re-emitting signal from `BandsController`
    dos_plot_requested
        Request bands plot.
        Re-emitting signal from `BandsController`
    hopping_segments_requested
        Signal requesting the plotting of hopping segments in the
        unit cell plot. Re-emitting signal for the `HoppingController`
        when the user selects a pair of sites from the hopping matrix.
    selection_requested
        Signal requesting a programmatic selection. Re-emitting signal for
        the `HoppingController`.
    """

    status_updated = Signal(str)

    # Hopping controller signals to relay
    hopping_segments_requested = Signal()
    selection_requested = Signal(object, object, object)
    # Band controller signals to relay
    bands_plot_requested = Signal()
    dos_plot_requested = Signal()

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
            Model tracking the currently selected unit cell, site, and state
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
        self.bands_controller.bands_plot_requested.connect(
            self.bands_plot_requested.emit
        )
        self.bands_controller.dos_plot_requested.connect(
            self.dos_plot_requested.emit
        )
        self.bands_controller.status_updated.connect(self.status_updated.emit)

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
        Redraw the hoppings UI panel.

        This method is called when the user renames a tree item to make sure
        that the matrix table contains the correct item names.
        """
        self.hopping_controller.update_unit_cell()

    def update_bands_panel(self):
        """
        Update the bands UI panel.
        """
        self.bands_controller.update_bands_panel()

    def update_projection_combo(self):
        """
        Update the projection combo.
        """
        self.bands_controller.update_combo()

    def get_projection_indices(self):
        """
        Get the projection indices from the projection combo.
        """
        return self.bands_controller.get_projection_indices()

    def get_dos_properties(self):
        """
        Get the DOS properties for the plots.

        Returns
        -------
        tuple[int, int]
            Number of bins/points to be used in the plot and the plot type
            (0 for a histogram, 1 for Lorentzian)
        """
        return self.bands_controller.get_dos_properties()
