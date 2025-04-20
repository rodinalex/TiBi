import sys
import numpy as np

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from ui.uc_plot import UnitCellPlot
from ui.bz_plot import BrillouinZonePlot
from ui.uc import UnitCellUI
from ui.hopping import HoppingPanel
from ui.band_plot import BandStructurePlot
from ui.placeholder import PlaceholderWidget


class MainWindow(QMainWindow):
    """
    Main application window that sets up the overall UI layout and coordinates interactions
    between different components.

    The layout consists of three columns:
    - Left column: Unit cell hierarchy tree view and property panels
    - Middle column: 3D visualization and hopping matrix
    - Right column: Computation options and band structure visualization
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1500, 900))

        # Hamiltonian
        self.hamiltonian = None

        # Initialize UI panels
        self.uc = UnitCellUI()

        # Initialize the plots
        self.unit_cell_plot = UnitCellPlot()
        self.bz_plot = BrillouinZonePlot()
        self.band_plot = BandStructurePlot()

        # Initialize the hopping panel
        self.hopping = HoppingPanel(self.uc.unit_cells)

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left column for hierarchical view and form panels
        left_layout.addWidget(self.uc, stretch=1)
        left_layout.addWidget(self.hopping, stretch=2)

        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=1)
        mid_layout.addWidget(self.bz_plot, stretch=1)
        mid_layout.addWidget(PlaceholderWidget("SPOT"), stretch=1)

        # Right column for computation options and band structure
        right_layout.addWidget(self.band_plot, stretch=1)
        right_layout.addWidget(PlaceholderWidget("BAND"), stretch=1)

        # Connect signals to update the plot after tree selection
        self.uc.selection.signals.updated.connect(self.update_plot)
        self.uc.selection.signals.updated.connect(self.update_BZ)
        # Connect signals to update the plot after the model for the unit cell or site changes
        self.uc.unit_cell_model.signals.updated.connect(self.update_plot)
        self.uc.unit_cell_model.signals.updated.connect(self.update_BZ)
        self.uc.site_model.signals.updated.connect(self.update_plot)
        # Conenct signals to calculate bands
        self.bz_plot.compute_bands_btn.clicked.connect(self.band_compute)

        # Notify the hopping block when the selection changes
        self.uc.selection.signals.updated.connect(
            lambda: self.hopping.set_uc_id(self.uc.selection["unit_cell"])
        )

        # Update the band structure plot when a unit cell is selected
        self.uc.selection.signals.updated.connect(self.update_band_plot_unit_cell)

        # When the Calculate button is clicked, refresh the path from BZ plot
        # self.band_plot.calculate_btn.clicked.connect(self.prepare_band_calculation)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(mid_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=2)

        self.setCentralWidget(main_view)

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

    def update_band_plot_unit_cell(self):
        """
        Update the band structure plot with the current unit cell.
        """
        unit_cell_id = self.uc.selection.get("unit_cell", None)
        # if unit_cell_id in self.uc.unit_cells:
        #     unit_cell = self.uc.unit_cells[unit_cell_id]
        #     self.band_plot.set_unit_cell(unit_cell)
        # else:
        #     self.band_plot.set_unit_cell(None)

    def prepare_band_calculation(self):
        """
        Prepare the band structure calculation by passing the current BZ path to the band plot.
        This method is called when the user clicks the Calculate Bands button.
        """
        print("\n============ PREPARING BAND CALCULATION ============")
        # Get the current unit cell and pass it to the band plot
        unit_cell_id = self.uc.selection.get("unit_cell", None)
        if unit_cell_id not in self.uc.unit_cells:
            print("No unit cell selected")
            return

        unit_cell = self.uc.unit_cells[unit_cell_id]

        # Basic unit cell checks
        print(f"Unit cell: {unit_cell.name}")
        print(
            f"Periodic directions: {[v.is_periodic for v in [unit_cell.v1, unit_cell.v2, unit_cell.v3]]}"
        )
        states, _ = unit_cell.get_states()
        print(f"Number of states: {len(states)}")
        print(f"Reciprocal vectors: {unit_cell.reciprocal_vectors()}")

        # Update the band plot with the unit cell
        print("Setting unit cell in band plot")
        self.band_plot.set_unit_cell(unit_cell)

        # Get the current BZ path (make a deep copy to avoid reference issues)
        path = [np.copy(p) for p in self.bz_plot.bz_path]
        print(
            f"BZ path in BZ plot: {self.bz_plot.bz_path}, length: {len(self.bz_plot.bz_path)}"
        )
        if not path or len(path) < 2:
            print(f"Path too short: {len(path)}")
            return

        # Generate labels (Γ for origin, high-symmetry points for others)
        labels = []
        for i, point in enumerate(path):
            if np.allclose(point, 0):
                labels.append("Γ")
            else:
                labels.append(f"P{i}")

        print(f"Preparing band calculation with path: {path}")
        print(f"Path labels: {labels}")

        # Update the band structure plot with the path
        print("Setting path in band plot")
        self.band_plot.set_path(path, labels)

    def band_compute(self):
        unit_cell_id = self.uc.selection.get("unit_cell", None)
        if unit_cell_id not in self.uc.unit_cells:
            print("No unit cell selected")
            return
        unit_cell = self.uc.unit_cells[unit_cell_id]
        hamiltonian = unit_cell.get_hamiltonian_function()
        # Get path
        path = [np.copy(p) for p in self.bz_plot.bz_path]
        # print(path)
        # print(self.bz_plot.n_points_spinbox.value())
        # Interpolate the path
        k_path = self.interpolate_k_path(path, self.bz_plot.n_points_spinbox.value())
        bands = []
        print(hamiltonian(k_path[0]))

        for k in k_path:
            H = hamiltonian(k)
            eigenvalues = np.linalg.eigh(H)[0]  # Only eigenvalues
            bands.append(eigenvalues)
        print(bands)

        bands = np.array(bands)
        self.band_plot._plot_bands(bands)

    # _plot_bands(self, bands)
    # print(hamiltonian([0]))

    def interpolate_k_path(self, points, n_total):
        points = np.array(points)
        distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
        total_distance = np.sum(distances)

        # Allocate number of points per segment
        n_segments = len(points) - 1
        fractions = distances / total_distance
        n_points_each = [max(2, int(round(f * n_total))) for f in fractions]

        # Build the full path
        k_path = []
        for i in range(n_segments):
            start = points[i]
            end = points[i + 1]
            n_pts = n_points_each[i]
            segment = np.linspace(start, end, n_pts, endpoint=False)
            k_path.extend(segment)

        # Add the final high-symmetry point
        k_path.append(points[-1])

        return np.array(k_path)


app = QApplication(sys.argv)
window = MainWindow()

window.show()
app.exec()
