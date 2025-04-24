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
        self.controllers["bz_plot"].compute_bands_request.connect(
            self._handle_compute_bands_request
        )
        self.controllers["uc"].plotUpdateRequested.connect(
            self._handle_plotUpdateBandsRequested
        )

    def _handle_compute_bands_request(self, path, num_points):
        """
        Handle requests to compute band structures.

        This method is triggered when the Brillouin zone plot controller
        emits a compute_bands_request signal. It retrieves the currently
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

    def _handle_plotUpdateBandsRequested(self):
        """
        Handle requests to update unit cell and Brollouin zone plots.

        This method is triggered when either a new unit cell is selected or when
        a currently-selected unit cell is modified. Because the plotting controllers
        have access to the unit_cells dictionary and the selection, no information needs
        to be passed.
        """
        self.controllers["uc_plot"].update_unit_cell()
        self.controllers["bz_plot"].update_brillouin_zone()
