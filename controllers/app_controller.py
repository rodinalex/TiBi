from PySide6.QtCore import QObject


class AppController(QObject):

    def __init__(self, models, controllers):
        super().__init__()
        self.models = models
        self.controllers = controllers

        # Connect signals
        self.controllers["bz_plot"].compute_bands_request.connect(
            self.handle_compute_bands_request
        )

    def handle_compute_bands_request(self, path, num_points):
        # Get the selected unit cell
        uc_id = self.models["selection"]["unit_cell"]
        unit_cell = self.models["unit_cells"][uc_id]

        # Call computation controller
        self.controllers["computation"].compute_bands(unit_cell, path, num_points)
