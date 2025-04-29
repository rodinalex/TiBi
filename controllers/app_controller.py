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
        self.controllers["bz_plot"].compute_bands_requested.connect(
            self._handle_compute_bands_requested
        )
        self.controllers["uc"].plot_update_requested.connect(
            self._handle_plot_update_requested
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

    def _handle_compute_bands_requested(self, path, num_points):
        """
        Handle requests to compute band structures.

        This method is triggered when the Brillouin zone plot controller
        emits a compute_bands_requested signal. It retrieves the currently
        selected unit cell and delegates the band structure calculation
        to the computation controller.

        Args:
            path: List of k-points defining the path in reciprocal space
            num_points: Number of points to compute along the path
        """
        # Get the selected unit cell
        uc_id = self.models["selection"]["unit_cell"]
        if uc_id is None:
            # Update status bar if no unit cell is selected
            self.controllers["main_ui"].update_status("No unit cell selected")
            return

        unit_cell = self.models["unit_cells"][uc_id]

        # Update status bar
        self.controllers["main_ui"].update_status("Computing bands...")

        # Call computation controller
        self.controllers["computation"].compute_bands(unit_cell, path, num_points)

        # Update status when complete
        self.controllers["main_ui"].update_status("Ready")

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

        self.controllers["uc_plot"].update_unit_cell(n1, n2, n3)
        self.controllers["bz_plot"].update_brillouin_zone()
