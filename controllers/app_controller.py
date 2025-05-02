from PySide6.QtCore import QObject


class AppController(QObject):
    """
    Main application controller that orchestrates interactions between components.

    This controller serves as a high-level coordinator in the application, handling
    communication between different subsystems. It connects signals from various
    controllers and routes requests to appropriate handlers, ensuring that components
    remain decoupled from each other.
    """

    def __init__(self, models, controllers):
        """
        Initialize the application controller.

        Args:
            models: Dictionary of data models used in the application
            controllers: Dictionary of controllers for different application components
        """
        super().__init__()
        self.models = models
        self.controllers = controllers

        # Connect signals

        self.controllers["uc"].plot_update_requested.connect(
            self._handle_plot_update_requested
        )

        self.controllers["hopping"].hopping_segments_requested.connect(
            self._handle_hopping_segments_requested
        )

        self.controllers["uc"].item_changed.connect(self._handle_item_changed)

        self.controllers["computation"].status_updated.connect(self._relay_status)

        # Toolbar signals

        self.controllers["main_ui"].project_refresh_requested.connect(
            self._handle_project_refresh_requested
        )

        self.controllers["main_ui"].toolbar.n1_spinbox.valueChanged.connect(
            self._handle_plot_update_requested
        )
        self.controllers["main_ui"].toolbar.n2_spinbox.valueChanged.connect(
            self._handle_plot_update_requested
        )
        self.controllers["main_ui"].toolbar.n3_spinbox.valueChanged.connect(
            self._handle_plot_update_requested
        )

        # Action signals
        self.controllers["main_ui"].wireframe_toggled.connect(
            self._handle_wireframe_toggled
        )

    def _relay_status(self, msg):
        """
        Relaying function that sends status updates from various controllers to the main_ui
        controller to be displayed in the status bar.
        """
        self.controllers["main_ui"].update_status(msg)

    def _handle_plot_update_requested(self):
        """
        Handle requests to update unit cell and Brollouin zone plots.

        This method is triggered when either a new unit cell is selected or when
        a currently-selected unit cell is modified. Because the plotting controllers
        have access to the unit_cells dictionary and the selection, no information needs
        to be passed.
        """

        # Depending on the dimensionality, update the unit cell spinners in the toolbar

        uc_id = self.models["selection"].get("unit_cell")
        if uc_id is not None:
            unit_cell = self.models["unit_cells"][uc_id]

            # Check which vectors of the unit cell are periodic and activate the UC spinners if they are
            if unit_cell.v1.is_periodic == True:
                self.controllers["main_ui"].toolbar.n1_spinbox.setEnabled(True)
            else:
                self.controllers["main_ui"].toolbar.n1_spinbox.setEnabled(False)

            if unit_cell.v2.is_periodic == True:
                self.controllers["main_ui"].toolbar.n2_spinbox.setEnabled(True)
            else:
                self.controllers["main_ui"].toolbar.n2_spinbox.setEnabled(False)

            if unit_cell.v3.is_periodic == True:
                self.controllers["main_ui"].toolbar.n3_spinbox.setEnabled(True)
            else:
                self.controllers["main_ui"].toolbar.n3_spinbox.setEnabled(False)
        else:
            self.controllers["main_ui"].toolbar.n1_spinbox.setEnabled(False)
            self.controllers["main_ui"].toolbar.n2_spinbox.setEnabled(False)
            self.controllers["main_ui"].toolbar.n3_spinbox.setEnabled(False)

        n1, n2, n3 = [
            spinbox.value() if spinbox.isEnabled() else 1
            for spinbox in (
                self.controllers["main_ui"].toolbar.n1_spinbox,
                self.controllers["main_ui"].toolbar.n2_spinbox,
                self.controllers["main_ui"].toolbar.n3_spinbox,
            )
        ]
        wireframe_shown = (
            self.controllers["main_ui"]
            .action_manager.unit_cell_actions["wireframe"]
            .isChecked()
        )
        self.controllers["uc_plot"].update_unit_cell(wireframe_shown, n1, n2, n3)
        self.controllers["bz_plot"].update_brillouin_zone()

    def _handle_wireframe_toggled(self, status):
        """
        Handle the toggling of the wireframe button in the toolbar.

        Extract the number of unit cells to be plotted along each direction from the
        corresponding spinboxes, check whether the wireframe is toggled on or off,
        and call the update_unit_cell function with the relevant parameters.
        """
        n1, n2, n3 = [
            spinbox.value() if spinbox.isEnabled() else 1
            for spinbox in (
                self.controllers["main_ui"].toolbar.n1_spinbox,
                self.controllers["main_ui"].toolbar.n2_spinbox,
                self.controllers["main_ui"].toolbar.n3_spinbox,
            )
        ]
        self.controllers["uc_plot"].update_unit_cell(status, n1, n2, n3)

    def _handle_hopping_segments_requested(self):
        """
        Handle the request to draw hopping segments after a pair of states
        is selected from the hopping button matrix.

        The function obtains the states selected by the button click and passes
        them to the update_hopping_segments function to draw the lines
        connecting the source state with the destination ones.
        """
        pair_selection = self.controllers["hopping"].pair_selection
        self.controllers["uc_plot"].update_hopping_segments(pair_selection)

    def _handle_item_changed(self):
        """
        Handle the change in the name of the tree items.

        This function is necessary to make sure that the label names in the
        hopping matrix and hopping table accurately reflect the item names.
        """
        self.controllers["hopping"]._update_unit_cell()

    def _handle_project_refresh_requested(self):
        """
        Handle a project refresh request. The unit cell dictionary and the project path have already been updated.
        Here, the models and the views are refreshed.
        """
        # Current selection state (tracks which items are selected in the UI)
        self.models["selection"].update(
            {"unit_cell": None, "site": None, "state": None}
        )

        # Form data for the currently selected unit cell
        self.models["unit_cell_data"].update(
            {
                "name": "",
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
            }
        )

        # Form data for the currently selected site
        self.models["site_data"].update({"name": "", "c1": 0.0, "c2": 0.0, "c3": 0.0})

        # Form data for the currently selected state
        self.models["state_data"].update({"name": ""})

        # Band structure calculation results
        # Uses AlwaysNotifyDataModel to ensure UI updates on every change
        self.models["band_structure"].update(
            {"k_path": None, "bands": None, "special_points": None}
        )

        self.controllers["uc"].refresh_tree()
        self._handle_plot_update_requested()
