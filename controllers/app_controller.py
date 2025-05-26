from PySide6.QtCore import QObject
import uuid

from .bz_plot_controller import BrillouinZonePlotController
from .computation_controller import ComputationController
from .main_ui_controller import MainUIController
from models.factories import selection_init
from models import DataModel, UnitCell
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

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
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
        # self.models = models
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
        self.computation_controller.band_computation_completed.connect(
            self._handle_plot_update_requested
        )
        self.computation_controller.projection_selection_changed.connect(print)
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

        # Update the plots when the number of unit cells to be plotted changes
        self.main_ui_controller.toolbar.n1_spinbox.valueChanged.connect(
            self._handle_plot_update_requested
        )
        self.main_ui_controller.toolbar.n2_spinbox.valueChanged.connect(
            self._handle_plot_update_requested
        )
        self.main_ui_controller.toolbar.n3_spinbox.valueChanged.connect(
            self._handle_plot_update_requested
        )

        # Toggle the wireframe in the unit cell plot
        self.main_ui_controller.wireframe_toggled.connect(
            self._handle_wireframe_toggled
        )

        # plot_controller

        # uc_controller
        # When an item in the tree view is renamed, refresh the hopping matrix
        # and table to reflect the correct names
        self.uc_controller.item_changed.connect(self._handle_item_changed)
        # Refresh the plots after unit cell selection or parameter change
        self.uc_controller.plot_update_requested.connect(
            self._handle_plot_update_requested
        )
        # uc_plot_controller

    def _relay_status(self, msg):
        """
        Send a message to the status bar.
        """
        self.main_ui_controller.update_status(msg)

    def _handle_plot_update_requested(self):
        """
        Handle requests to update unit cell and Brillouin zone plots.

        The signal is emitted by the `UnitCellController` when system
        parameters that impact the visual structure change.
        """
        uc_id = self.selection.get("unit_cell")
        if uc_id is not None:
            unit_cell = self.unit_cells[uc_id]

            # Check which vectors of the unit cell are periodic and activate
            # the UC spinners if they are
            self.main_ui_controller.toolbar.n1_spinbox.setEnabled(
                unit_cell.v1.is_periodic
            )
            self.main_ui_controller.toolbar.n2_spinbox.setEnabled(
                unit_cell.v2.is_periodic
            )
            self.main_ui_controller.toolbar.n3_spinbox.setEnabled(
                unit_cell.v3.is_periodic
            )

            # Plot the band structure (if available)
            self.plot_controller.plot_band_structure(unit_cell.bandstructure)
        # Deactivate the spinners
        else:
            self.main_ui_controller.toolbar.n1_spinbox.setEnabled(False)
            self.main_ui_controller.toolbar.n2_spinbox.setEnabled(False)
            self.main_ui_controller.toolbar.n3_spinbox.setEnabled(False)

        # Get the parameters for the unit cell plot
        n1, n2, n3 = [
            spinbox.value() if spinbox.isEnabled() else 1
            for spinbox in (
                self.main_ui_controller.toolbar.n1_spinbox,
                self.main_ui_controller.toolbar.n2_spinbox,
                self.main_ui_controller.toolbar.n3_spinbox,
            )
        ]
        wireframe_shown = (
            self.main_ui_controller.action_manager.unit_cell_actions[
                "wireframe"
            ].isChecked()
        )

        # Update the 3D plots for BZ and UC
        self.uc_plot_controller.update_unit_cell(wireframe_shown, n1, n2, n3)
        self.bz_plot_controller.update_brillouin_zone()
        # If a pair of states is selected, also plot the hopping segments
        pair_selection = self.computation_controller.get_pair_selection()
        if pair_selection[0] is not None and pair_selection[1] is not None:
            self.uc_plot_controller.update_hopping_segments(pair_selection)

    def _handle_wireframe_toggled(self, status):
        """
        Handle the toggling of the wireframe button in the toolbar.

        Extract the number of unit cells to be plotted along each direction
        from the corresponding spinboxes, check whether the wireframe
        is toggled on or off, and call the `update_unit_cell`
        function with the relevant parameters.

        Parameters
        ----------
        status : bool
            The status of the wireframe toggle button.
        """
        n1, n2, n3 = [
            spinbox.value() if spinbox.isEnabled() else 1
            for spinbox in (
                self.main_ui_controller.toolbar.n1_spinbox,
                self.main_ui_controller.toolbar.n2_spinbox,
                self.main_ui_controller.toolbar.n3_spinbox,
            )
        ]
        self.uc_plot_controller.update_unit_cell(status, n1, n2, n3)
        pair_selection = self.computation_controller.get_pair_selection()
        if pair_selection[0] is not None and pair_selection[1] is not None:
            self.uc_plot_controller.update_hopping_segments(pair_selection)

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

    def _handle_item_changed(self):
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
        self.selection.update(selection_init())
        self.uc_controller.tree_view.refresh_tree(self.unit_cells)
        self._handle_plot_update_requested()

    def _handle_selection_requested(self, uc_id, site_id, state_id):
        """Programmatically select an item in the tree view."""
        self.uc_controller.tree_view._select_item_by_id(
            uc_id, site_id, state_id
        )
