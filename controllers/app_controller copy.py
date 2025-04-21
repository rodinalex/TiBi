from PySide6.QtCore import QObject
from ui.uc_plot import UnitCellPlot
from ui.bz_plot import BrillouinZonePlot
from ui.uc import UnitCellUI
from ui.hopping import HoppingPanel
from ui.band_plot import BandStructurePlot
from controllers.hopping_controller import HoppingController
from controllers.bz_controller import BZController
from controllers.computation_controller import ComputationController
import numpy as np


class AppController(QObject):
    """
    Main application controller that coordinates interactions between UI components.
    
    The AppController orchestrates the different parts of the application,
    connecting changes in one part of the UI to updates in other parts.
    It delegates specific functionality to specialized controllers.
    """

    def __init__(
        self,
        uc: UnitCellUI,
        hopping: HoppingPanel,
        unit_cell_plot: UnitCellPlot,
        bz_plot: BrillouinZonePlot,
        band_plot: BandStructurePlot,
    ):

        super().__init__()

        # Store references to UI components and data models
        self.uc = uc
        self.hopping = hopping
        self.unit_cell_plot = unit_cell_plot
        self.bz_plot = bz_plot
        self.band_plot = band_plot
        
        # Initialize sub-controllers
        self.hopping_controller = HoppingController(self.uc.unit_cells, self.hopping)
        self.bz_controller = BZController(self.bz_plot)
        self.computation_controller = ComputationController(
            self.uc.unit_cells, self.bz_controller, self.band_plot
        )

        # Connect UI signals to appropriate handler methods

        # Connect signals to update the plots after tree selection
        self.uc.selection.signals.updated.connect(self.update_plot)
        self.uc.selection.signals.updated.connect(self.update_BZ)

        # Connect signals to update the plot after the model for the unit cell or site changes
        self.uc.unit_cell_model.signals.updated.connect(self.update_plot)
        self.uc.unit_cell_model.signals.updated.connect(self.update_BZ)
        self.uc.site_model.signals.updated.connect(self.update_plot)

        # Connect signals to calculate bands
        self.bz_plot.compute_bands_btn.clicked.connect(self.compute_bands)

        # Notify the controllers when the selection changes
        self.uc.selection.signals.updated.connect(
            lambda: self.hopping_controller.set_unit_cell(self.uc.selection.get("unit_cell", None))
        )
        self.uc.selection.signals.updated.connect(
            lambda: self.computation_controller.set_unit_cell(self.uc.selection.get("unit_cell", None))
        )

    def update_plot(self):
        """
        Update the 3D plot with the selected unit cell.
        Highlight the selected site in the 3D plot.

        This method is called after a selection in the tree view.
        It first updates the plot to show the correct unit cell, then tells
        the plot to highlight the specific site with a different color.

        Args:
            unit_cell_id: UUID of the unit cell containing the site
            site_id: UUID of the site to highlight
            state: UUID of the state from the state selection signal
        """
        unit_cell_id = self.uc.selection.get("unit_cell", None)
        site_id = self.uc.selection.get("site", None)
        if unit_cell_id in self.uc.unit_cells:
            unit_cell = self.uc.unit_cells[unit_cell_id]
            self.unit_cell_plot.set_unit_cell(unit_cell)
        else:
            # Clear the plot if unit cell doesn't exist
            self.unit_cell_plot.set_unit_cell(None)

        try:
            # Always call select_site, even with None, to ensure proper highlighting
            self.unit_cell_plot.select_site(site_id)
        except Exception as e:
            print(f"Error highlighting site: {e}")

    def update_BZ(self):
        """
        Update the Brillouin zone visualization with data from the selected unit cell.

        This method retrieves BZ vertices and faces from the selected unit cell,
        stores them in the data model, and passes them to the BZ controller
        for visualization.
        """
        try:
            uc = self.uc.unit_cells[self.uc.selection["unit_cell"]]
            bz_vertices, bz_faces = uc.get_BZ()
            self.uc.bz["bz_vertices"] = bz_vertices
            self.uc.bz["bz_faces"] = bz_faces

            # Pass BZ data to the controller
            self.bz_controller.set_bz(self.uc.bz)
        except Exception as e:
            print(f"Error updating Brillouin zone: {e}")

    def compute_bands(self):
        """
        Trigger band structure calculation.
        
        Delegates to the computation controller to handle band structure calculations.
        """
        self.computation_controller.compute_bands()
