from PySide6.QtCore import QObject
from ui.uc_plot import UnitCellPlot
from ui.bz_plot import BrillouinZonePlot
from ui.uc import UnitCellUI
from ui.hopping import HoppingPanel
from ui.band_plot import BandStructurePlot
import numpy as np
from src.band_structure import interpolate_k_path, band_compute


class AppController(QObject):

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

        # Connect UI signals to appropriate handler methods

        # Connect signals to update the plots after tree selection
        self.uc.selection.signals.updated.connect(self.update_plot)
        self.uc.selection.signals.updated.connect(self.update_BZ)

        # Connect signals to update the plot after the model for the unit cell or site changes
        self.uc.unit_cell_model.signals.updated.connect(self.update_plot)
        self.uc.unit_cell_model.signals.updated.connect(self.update_BZ)
        self.uc.site_model.signals.updated.connect(self.update_plot)

        # Conenct signals to calculate bands
        self.bz_plot.compute_bands_btn.clicked.connect(self.update_bands_plot)

        # Notify the hopping block when the selection changes
        self.uc.selection.signals.updated.connect(
            lambda: self.hopping.set_uc_id(self.uc.selection["unit_cell"])
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
        stores them in the data model, and passes them to both BZ plots for visualization.
        """
        try:
            uc = self.uc.unit_cells[self.uc.selection["unit_cell"]]
            bz_vertices, bz_faces = uc.get_BZ()
            self.uc.bz["bz_vertices"] = bz_vertices
            self.uc.bz["bz_faces"] = bz_faces

            # Pass BZ data to both plot widgets for visualization
            self.bz_plot.set_BZ(self.uc.bz)

            # Clear the band plot path when BZ changes
            # self.band_plot.set_path([])
        except Exception as e:
            print(f"Error updating Brillouin zone: {e}")

    def update_bands_plot(self):
        unit_cell_id = self.uc.selection.get("unit_cell", None)
        if unit_cell_id not in self.uc.unit_cells:
            print("No unit cell selected")
            return
        unit_cell = self.uc.unit_cells[unit_cell_id]
        hamiltonian = unit_cell.get_hamiltonian_function()
        # Get path
        path = [np.copy(p) for p in self.bz_plot.bz_path]
        # Interpolate the path
        k_path = interpolate_k_path(path, self.bz_plot.n_points_spinbox.value())
        bands = band_compute(hamiltonian, k_path)
        # Get the positions along the path reflecting the point spacing
        step = np.linalg.norm(np.diff(k_path, axis=0), axis=1)
        pos = np.hstack((0, np.cumsum(step)))

        self.band_plot._plot_bands(pos, bands)
