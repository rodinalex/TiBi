from PySide6.QtCore import QObject
import uuid

from .bz_plot_controller import BrillouinZonePlotController
from .computation_controller import ComputationController
from .main_ui_controller import MainUIController
from TiBi.models import Selection, UnitCell
from .plot_controller import PlotController
from .uc_controller import UnitCellController
from .uc_plot_controller import UnitCellPlotController


class AppController(QObject):
    """
    Main application controller.

    This controller serves as a high-level coordinator in the application,
    handling communication between different subsystems.
    It connects signals from various controllers and routes requests to
    appropriate handlers, ensuring that components remain decoupled from
    each other.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
    bz_plot_controller : BrillouinZonePlotController
        Controller of the BZ graphical component
    computation_controller : ComputationController
        Controller orchestrating computations
    main_ui_controller : MainUIController
        Controller in charge of menus and toolbars
    plot_controller : PlotController
        Controller of the results graphical component
    uc_controller : UnitCellController
        Controller in charge of `UnitCell` creation/editing
    uc_plot_controller : UnitCellPlotController
        Controller of the `UnitCell` graphical component
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        bz_plot_controller: BrillouinZonePlotController,
        computation_controller: ComputationController,
        main_ui_controller: MainUIController,
        plot_controller: PlotController,
        uc_controller: UnitCellController,
        uc_plot_controller: UnitCellPlotController,
    ):
        """
        Initialize the application controller.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
        bz_plot_controller : BrillouinZonePlotController
            Controller of the BZ graphical component
        computation_controller : ComputationController
            Controller orchestrating computations
        main_ui_controller : MainUIController
            Controller in charge of menus and toolbars
        plot_controller : PlotController
            Controller of the results graphical component
        uc_controller : UnitCellController
            Controller in charge of `UnitCell` creation/editing
        uc_plot_controller : UnitCellPlotController
            Controller of the `UnitCell` graphical component
        """
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.bz_plot_controller = bz_plot_controller
        self.computation_controller = computation_controller
        self.main_ui_controller = main_ui_controller
        self.plot_controller = plot_controller
        self.uc_controller = uc_controller
        self.uc_plot_controller = uc_plot_controller

        # Connect signals
        # Redraw the panels only when the unit cell selection changes.
        # Selecting inside the unit cell should not cause redraws.
        self.selection.unit_cell_updated.connect(self._update_panels)
        # When a new site is selected, reddraw only the unit cell plot
        self.selection.site_updated.connect(self._update_unit_cell_plot)

        # bz_plot_controller
        # When the path is updated, the bandstructure is cleared.
        # We pass an empty band structure to the plotting function
        # resulting in a cleared plot.
        self.bz_plot_controller.bz_path_updated.connect(self._plot_bands)

        # computation_controller
        self.computation_controller.status_updated.connect(self._relay_status)
        self.computation_controller.bands_plot_requested.connect(
            self._plot_bands
        )
        self.computation_controller.dos_plot_requested.connect(self._plot_dos)
        # Handle the programmatic selection of an item in the tree
        # due to undo/redo in the hopping controller
        self.computation_controller.selection_requested.connect(
            self.uc_controller.select_item
        )

        # Handle the request to draw hopping segments after a pair of states
        # is selected from the hopping button matrix
        self.computation_controller.hopping_segments_requested.connect(
            self._handle_hopping_segments_requested
        )

        # main_ui_controller
        self.main_ui_controller.project_refresh_requested.connect(
            self._handle_project_refresh_requested
        )
        self.main_ui_controller.unit_cell_update_requested.connect(
            self._update_unit_cell_plot
        )
        # uc_controller
        self.uc_controller.hopping_projection_update_requested.connect(
            self._handle_hopping_projection_update
        )
        # If site parameter changes, the change is purely cosmetic,
        # so the only the unit cell plot is redrawn
        self.uc_controller.site_parameter_changed.connect(
            self._update_unit_cell_plot
        )
        # Unit cell parameter changes typically invalidate
        # derived quantities, requiring a full redraw.
        self.uc_controller.unit_cell_parameter_changed.connect(
            self._update_panels
        )

    def _relay_status(self, msg):
        """
        Send a message to the status bar.
        """
        self.main_ui_controller.update_status(msg)

    def _update_panels(self):
        """
        Handle requests to update plots and panels.

        This major update is called when the `UnitCell` selection changes,
        `UnitCell` parameter changes or `Site` parameter changes.
        """
        uc_id = self.selection.unit_cell
        if uc_id is not None:
            unit_cell = self.unit_cells[uc_id]

            # Check which vectors of the unit cell are periodic and activate
            # the UC spinners if they are
            self.main_ui_controller.set_spinbox_status(
                unit_cell.v1.is_periodic,
                unit_cell.v2.is_periodic,
                unit_cell.v3.is_periodic,
            )

        # Deactivate the spinners
        else:
            self.main_ui_controller.set_spinbox_status(False, False, False)

        # Update the 3D plots for BZ and UC
        self._update_unit_cell_plot()
        self.bz_plot_controller.update_brillouin_zone()

        # Update the computation panels
        self.computation_controller.update_bands_panel()
        self.computation_controller.update_hopping_panel()

    def _handle_hopping_segments_requested(self):
        """
        Handle the request to draw hopping segments.

        After a pair of states is selected from the hopping button matrix,
        this function passes them to the update_hopping_segments function
        to draw the lines connecting the source state with the destination
        ones. This approach avoids redrawing the rest of the plot.
        """
        pair_selection = self.computation_controller.get_pair_selection()
        self.uc_plot_controller.update_hopping_segments(pair_selection)

    def _handle_hopping_projection_update(self):
        """
        Redraw the hopping panels and the projection dropbox.

        This function is necessary to make sure that the label names in the
        hopping matrix, hopping table, and projection drop box
        accurately reflect the item names. Additionally, if states are added
        or removed, the hopping matrix needs to be updated.
        """
        self.computation_controller.update_hopping_panel()
        self.computation_controller.update_projection_combo()

    def _handle_project_refresh_requested(self):
        """
        Handle a project refresh request.

        The unit cell dictionary and
        the project path have already been updated.
        Here, only the selection and views are refreshed.
        """
        # Current selection state (tracks which items are selected in the UI)
        self.selection.set_selection(uc_id=None, site_id=None, state_id=None)
        self.uc_controller.refresh_tree()
        self._update_panels()

    def _update_unit_cell_plot(self):
        """
        Redraw the unit cell plot.

        Called during the full panels update or when site parameters change.
        """
        n1, n2, n3, wireframe_shown = (
            self.main_ui_controller.get_uc_plot_properties()
        )
        self.uc_plot_controller.update_unit_cell(wireframe_shown, n1, n2, n3)
        # If a pair of states is selected, also plot the hopping segments
        pair_selection = self.computation_controller.get_pair_selection()
        if pair_selection[0] is not None and pair_selection[1] is not None:
            self.uc_plot_controller.update_hopping_segments(pair_selection)

    def _plot_bands(self):
        """
        Plot the bands for the selected `UnitCell`.
        """
        idx = self.computation_controller.get_projection_indices()
        self.plot_controller.plot_band_structure(idx)

    def _plot_dos(self):
        """
        Plot the dos for the selected `UnitCell`.
        """
        idx = self.computation_controller.get_projection_indices()
        num_bins, plot_type, broadening = (
            self.computation_controller.get_dos_properties()
        )
        self.plot_controller.plot_dos(num_bins, idx, plot_type, broadening)
