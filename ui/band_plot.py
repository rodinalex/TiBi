from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import QSize, Qt

import numpy as np
import matplotlib.figure as mpl_fig
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.band_structure import calculate_bands_along_path, get_special_points


class BandStructurePlot(QWidget):
    """
    Widget for displaying band structure plots.

    This widget creates a matplotlib figure embedded in a Qt widget to display
    band structure calculations along a path in k-space. It includes controls for
    running calculations and visualization options.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(400, 300))

        # Data
        self.unit_cell = None
        self.bz_path = []
        self.special_point_labels = []
        self.num_points = 100

        # Setup layout
        layout = QVBoxLayout(self)

        # Controls
        # control_layout = QHBoxLayout()

        # self.calculate_btn = QPushButton("Calculate Bands")
        # self.calculate_btn.clicked.connect(self.calculate_and_plot_bands)
        # self.calculate_btn.setEnabled(False)  # Disabled until we have a valid path

        # control_layout.addWidget(self.calculate_btn)
        # control_layout.addStretch()

        # # Status label
        # self.status_label = QLabel("No path selected")
        # self.status_label.setAlignment(Qt.AlignCenter)  # AlignCenter

        # Matplotlib Figure
        self.figure = mpl_fig.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Add widgets to layout
        # layout.addLayout(control_layout)
        # layout.addWidget(self.status_label)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("k-vector")
        self.ax.set_ylabel("Energy")
        self.ax.grid(True)

        # Initial draw
        self.canvas.draw()

    # def set_unit_cell(self, unit_cell):
    #     """Set the unit cell for band structure calculations."""
    #     self.unit_cell = unit_cell
    #     self._update_ui_state()

    # def set_path(self, path, labels=None):
    #     """
    #     Set the k-space path for band structure calculations.

    #     Args:
    #         path: List of k-points in Cartesian coordinates
    #         labels: Optional list of labels for special points (e.g., 'Γ', 'X', etc.)
    #     """
    #     print(f"Setting band plot path: {path}, length: {len(path)}")

    #     # Make a copy of the path to avoid reference issues
    #     self.bz_path = [np.array(p) for p in path] if path else []
    #     print(
    #         f"Band plot path after setting: {self.bz_path}, length: {len(self.bz_path)}"
    #     )

    #     if labels is None:
    #         # If no labels provided, use Γ for origin and numbered points for others
    #         self.special_point_labels = []
    #         for i, point in enumerate(path):
    #             if np.allclose(point, 0):
    #                 self.special_point_labels.append("Γ")
    #             else:
    #                 self.special_point_labels.append(f"P{i}")
    #     else:
    #         self.special_point_labels = labels

    #     # Update status and UI
    #     if len(self.bz_path) >= 2:
    #         path_str = " → ".join(self.special_point_labels)
    #         self.status_label.setText(f"Path: {path_str} ({len(self.bz_path)} points)")
    #     else:
    #         self.status_label.setText(
    #             "Select a path in the Brillouin zone (need at least 2 points)"
    #         )

    #     # Explicitly call update UI state with extra debug info
    #     print("Calling _update_ui_state from set_path")
    #     self._update_ui_state()

    # def _update_ui_state(self):
    #     """Update UI controls based on current state."""
    #     # First, make sure we have a valid unit cell
    #     if self.unit_cell is None:
    #         print("Band plot: Unit cell is None")
    #         self.calculate_btn.setEnabled(False)
    #         return

    #     # Check if we have at least 2 points in the path
    #     if len(self.bz_path) < 2:
    #         print(
    #             f"Band plot: Path has only {len(self.bz_path)} points, need at least 2"
    #         )
    #         self.calculate_btn.setEnabled(False)
    #         return

    #     # Check if the unit cell has any periodic directions
    #     reciprocal_vectors = self.unit_cell.reciprocal_vectors()
    #     if len(reciprocal_vectors) == 0:
    #         print("Band plot: Unit cell has no periodic directions")
    #         self.status_label.setText("Unit cell has no periodic directions")
    #         self.calculate_btn.setEnabled(False)
    #         return

    #     # Check if the unit cell contains any states
    #     try:
    #         states, _ = self.unit_cell.get_states()
    #         if not states:
    #             print("Band plot: Unit cell has no states")
    #             self.status_label.setText(
    #                 "Unit cell has no states, cannot create Hamiltonian"
    #             )
    #             self.calculate_btn.setEnabled(False)
    #             return

    #         # Check if Hamiltonian can be created
    #         self.unit_cell.get_hamiltonian_function()

    #         # If we've reached here, all conditions are met
    #         print("All conditions met, enabling calculate button")
    #         self.calculate_btn.setEnabled(True)

    #     except Exception as e:
    #         print(f"Band plot error: {str(e)}")
    #         self.status_label.setText(f"Error: {str(e)}")
    #         self.calculate_btn.setEnabled(False)

    # def calculate_and_plot_bands(self):
    #     """Calculate and plot the band structure along the current path."""
    #     print("Attempting to calculate bands...")
    #     if not self.unit_cell:
    #         print("Cannot calculate: unit_cell is None")
    #         return
    #     if len(self.bz_path) < 2:
    #         print(f"Cannot calculate: path too short ({len(self.bz_path)} points)")
    #         return

    #     try:
    #         # Get k-points in reciprocal basis
    #         k_points, special_points = get_special_points(self.unit_cell, self.bz_path)

    #         # Get Hamiltonian function
    #         hamiltonian_fn = self.unit_cell.get_hamiltonian_function()

    #         # Calculate bands
    #         distances, bands = calculate_bands_along_path(
    #             hamiltonian_fn, k_points, self.num_points
    #         )

    #         # Plot bands
    #         self._plot_bands(distances, bands, special_points)

    #         # Update status
    #         self.status_label.setText(f"Calculated {bands.shape[0]} bands")

    #     except Exception as e:
    #         self.status_label.setText(f"Error: {str(e)}")

    def _plot_bands(self, bands):
        # def _plot_bands(self, distances, bands, special_points):
        """
        Plot the calculated bands.

        Args:
            distances: Array of distances along the path
            bands: 2D array of band energies (bands × distances)
            special_points: Indices of special points in the path
        """
        # Clear previous plot
        self.ax.clear()

        # Plot each band
        # for band_idx in range(bands.shape[0]):
        #     self.ax.plot(distances, bands[band_idx], "b-")

        for band_idx in range(bands.shape[1]):
            self.ax.plot(bands[:, band_idx])
            # self.ax.plot(distances, bands[band_idx], "b-")

        # # Add vertical lines at special points
        # special_distances = [distances[0]]  # First point

        # # Add intermediate points where path changes direction
        # for i in range(1, len(special_points)):
        #     idx = i * (self.num_points // (len(special_points) - 1))
        #     if idx < len(distances):
        #         special_distances.append(distances[idx])

        # # Add vertical lines at special points
        # for dist in special_distances:
        #     self.ax.axvline(x=dist, color="k", linestyle="--", alpha=0.5)

        # # Set x-ticks at special points with labels
        # self.ax.set_xticks(special_distances)
        # if len(self.special_point_labels) >= len(special_distances):
        #     self.ax.set_xticklabels(self.special_point_labels[: len(special_distances)])

        # # Set labels and grid
        # self.ax.set_xlabel("k-vector")
        # self.ax.set_ylabel("Energy")
        self.ax.grid(True)

        # Draw the canvas
        self.canvas.draw()
