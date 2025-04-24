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
        unit_cell = self.models["unit_cells"][uc_id]

        # Call computation controller
        self.controllers["computation"].compute_bands(unit_cell, path, num_points)

    def _handle_plotUpdateBandsRequested(self):
        self.controllers["uc_plot"]._update_schedule()
        self.controllers["bz_plot"]._update_schedule()
