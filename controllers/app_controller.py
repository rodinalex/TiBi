from PySide6.QtCore import QObject
import uuid

from controllers.bz_plot_controller import BrillouinZonePlotController
from controllers.computation_controller import ComputationController
from controllers.hopping_controller import HoppingController
from controllers.main_ui_controller import MainUIController
from controllers.plot_controller import PlotController
from controllers.uc_controller import UnitCellController
from controllers.uc_plot_controller import UnitCellPlotController
from src.tibitypes import UnitCell


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
    models : dict
        Dictionary of data models used in the application
    controllers : dict
        Dictionary of controllers for different application components
    """

    def __init__(self, models, controllers):
        """
        Initialize the application controller.

        Parameters
        ----------
        models : dict
            Dictionary of data models used in the application
        controllers : dict
            Dctionary of controllers for different application components
        """
        super().__init__()
        self.models = models
        self.controllers = controllers

        # Extract the relevant models and controllers
        self.bz_plot_controller: BrillouinZonePlotController = (
            self.controllers["bz_plot"]
        )
        self.computation_controller: ComputationController = self.controllers[
            "computation"
        ]
        self.hopping_controller: HoppingController = self.controllers[
            "hopping"
        ]
        self.main_ui_controller: MainUIController = self.controllers["main_ui"]
        self.plot_controller: PlotController = self.controllers["plot"]
        self.uc_controller: UnitCellController = self.controllers["uc"]
        self.uc_plot_controller: UnitCellPlotController = self.controllers[
            "uc_plot"
        ]

        self.selection: dict[str, uuid.UUID] = self.models["selection"]
        self.unit_cells: dict[uuid.UUID, UnitCell] = self.models["unit_cells"]

        # Connect signals

        # When an item in the tree view is renamed, refresh the hopping matrix
        # and table to reflect the correct names
        self.uc_controller.item_changed.connect(self._handle_item_changed)

        # Handle the programmatic selection of an item in the tree
        # due to undo/redo in the hopping controller
        self.hopping_controller.selection_requested.connect(
            self._handle_selection_requested
        )

        # Refresh the plots after unit cell selection or parameter change
        self.uc_controller.plot_update_requested.connect(
            self._handle_plot_update_requested
        )

        # Handle the request to draw hopping segments after a pair of states
        # is selected from the hopping button matrix
        self.hopping_controller.hopping_segments_requested.connect(
            self._handle_hopping_segments_requested
        )
        # Computation controller
        self.computation_controller.status_updated.connect(self._relay_status)
        self.computation_controller.band_computation_completed.connect(
            self._handle_plot_update_requested
        )
        # Toolbar signals

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

    def _relay_status(self, msg):
        """
        Send a message to the status bar.
        """
        self.main_ui_controller.update_status(msg)

    def _handle_plot_update_requested(self):
        """
        Handle requests to update unit cell and Brillouin zone plots.
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
            self.plot_controller.plot_band_structure(unit_cell.bandstructure)

        else:
            self.main_ui_controller.toolbar.n1_spinbox.setEnabled(False)
            self.main_ui_controller.toolbar.n2_spinbox.setEnabled(False)
            self.main_ui_controller.toolbar.n3_spinbox.setEnabled(False)

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
        # band_structure = self.models["band_structures"].get(uc_id)
        # self.models["bz_path"].clear()

        self.uc_plot_controller.update_unit_cell(wireframe_shown, n1, n2, n3)
        self.bz_plot_controller.update_brillouin_zone()

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

    def _handle_hopping_segments_requested(self):
        """
        Handle the request to draw hopping segments.

        After a pair of states is selected from the hopping button matrix,
        this function passes them to the update_hopping_segments function
        to draw the lines connecting the source state with the destination
        ones.
        """
        pair_selection = self.hopping_controller.pair_selection
        self.uc_plot_controller.update_hopping_segments(pair_selection)

    def _handle_item_changed(self):
        """
        Handle the change in the name of the tree items.

        This function is necessary to make sure that the label names in the
        hopping matrix and hopping table accurately reflect the item names.
        The effect is the redrawing of the hopping matrix.
        """
        self.hopping_controller.update_unit_cell()

    def _handle_project_refresh_requested(self):
        """
        Handle a project refresh request. The unit cell dictionary and
        the project path have already been updated.
        Here, the models and the views are refreshed.
        """
        # Current selection state (tracks which items are selected in the UI)
        self.selection.update({"unit_cell": None, "site": None, "state": None})

        # Form data for the currently selected unit cell
        self.models["unit_cell_data"].update(
            {
                "unit_cell_name": "",
                "v1x": 1.0,
                "v1y": 0.0,
                "v1z": 0.0,
                "v2x": 0.0,
                "v2y": 1.0,
                "v2z": 0.0,
                "v3x": 0.0,
                "v3y": 0.0,
                "v3z": 1.0,
                "v1periodic": False,
                "v2periodic": False,
                "v3periodic": False,
                "site_name": "",
                "c1": 0.0,
                "c2": 0.0,
                "c3": 0.0,
                "state_name": "",
            }
        )

        # Band structure calculation results
        # Uses AlwaysNotifyDataModel to ensure UI updates on every change
        self.models["active_band_structure"].update(
            {"k_path": None, "bands": None, "special_points": None}
        )

        self.uc_controller.tree_view.refresh_tree(self.models["unit_cells"])
        self._handle_plot_update_requested()

    def _handle_selection_requested(self, uc_id, site_id, state_id):
        """Programmatically select an item in the tree view."""
        self.uc_controller.tree_view._select_item_by_id(
            uc_id, site_id, state_id
        )
