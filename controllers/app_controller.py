from PySide6.QtCore import QObject
import uuid

from .bz_plot_controller import BrillouinZonePlotController
from .computation_controller import ComputationController
from .main_ui_controller import MainUIController
from models import Selection, UnitCell
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
        `Selection` tracking the current selection
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
        selection : DataModel
            `DataModel` tracking the current selection
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

        # Extract the relevant models and controllers
        self.bz_plot_controller = bz_plot_controller
        self.computation_controller = computation_controller
        self.main_ui_controller = main_ui_controller
        self.plot_controller = plot_controller
        self.uc_controller = uc_controller
        self.uc_plot_controller = uc_plot_controller

        # Connect signals
        self.selection.unit_cell_updated.connect(self._update_panels)

        # bz_plot_controller
        # When the path is updated, the bandstructure is cleared.
        # Clear the bandstructure plot
        self.bz_plot_controller.bz_path_updated.connect(
            lambda: self.plot_controller.plot_band_structure(
                self.unit_cells[self.selection["unit_cell"]].bandstructure
            )
        )
        # computation_controller
        self.computation_controller.status_updated.connect(self._relay_status)
        self.computation_controller.bands_computed.connect(
            self._handle_bands_computed
        )
        # Handle the programmatic selection of an item in the tree
        # due to undo/redo in the hopping controller
        self.computation_controller.selection_requested.connect(
            self._handle_selection_requested
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
        # When an item in the tree view is renamed, refresh the hopping matrix
        # and table to reflect the correct names
        self.uc_controller.item_renamed.connect(self._handle_item_renamed)
        # Refresh the plots after unit cell selection or parameter change
        self.uc_controller.parameter_changed.connect(self._update_panels)

    def _relay_status(self, msg):
        """
        Send a message to the status bar.
        """
        self.main_ui_controller.update_status(msg)

    def _update_panels(self):
        """
        Handle requests to update plots and panels.

        Takes place when system parameters or the selection change.
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

            # Plot the band structure (if available)
            self.plot_controller.plot_band_structure(unit_cell.bandstructure)
            self.computation_controller.set_dimensionality(
                unit_cell.v1.is_periodic
                + unit_cell.v2.is_periodic
                + unit_cell.v3.is_periodic
            )

        # Deactivate the spinners
        else:
            self.main_ui_controller.set_spinbox_status(False, False, False)
            self.computation_controller.set_dimensionality(0)

        # Update the 3D plots for BZ and UC
        self._update_unit_cell_plot()
        self.bz_plot_controller.update_brillouin_zone()

        # Update the hopping panel
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

    def _handle_item_renamed(self):
        """
        Handle the change in the name of the tree items.

        This function is necessary to make sure that the label names in the
        hopping matrix, hopping table, and projection drop box
        accurately reflect the item names.
        """
        self.computation_controller.update_hopping_panel()

    def _handle_project_refresh_requested(self):
        """
        Handle a project refresh request.

        The unit cell dictionary and
        the project path have already been updated.
        Here, only the selection and views are refreshed.
        """
        # Current selection state (tracks which items are selected in the UI)
        self.selection.set_selection(uc_id=None, site_id=None, state_id=None)
        self.uc_controller.tree_view.refresh_tree(self.unit_cells)
        self._update_panels()

    def _handle_selection_requested(self, uc_id, site_id, state_id):
        """Programmatically select an item in the tree view."""
        self.uc_controller.tree_view._select_item_by_id(
            uc_id, site_id, state_id
        )

    def _handle_bands_computed(self):
        # FOR NOW, THE BAND STRUCTURE IS PLOTTED
        # WE NEED TO ACCESS THE COMBO BOX TO GET THE PROJECTION
        uc_id = self.selection.unit_cell
        unit_cell = self.unit_cells[uc_id]
        self.plot_controller.plot_band_structure(unit_cell.bandstructure)

    def _update_unit_cell_plot(self):
        n1, n2, n3, wireframe_shown = (
            self.main_ui_controller.get_uc_plot_properties()
        )
        self.uc_plot_controller.update_unit_cell(wireframe_shown, n1, n2, n3)
        # If a pair of states is selected, also plot the hopping segments
        pair_selection = self.computation_controller.get_pair_selection()
        if pair_selection[0] is not None and pair_selection[1] is not None:
            self.uc_plot_controller.update_hopping_segments(pair_selection)
