from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QSize, Qt

import numpy as np
import matplotlib.figure as mpl_fig
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# from src.band_structure import calculate_bands_along_path, get_special_points


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

        # Matplotlib Figure
        self.figure = mpl_fig.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Add widgets to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("k-vector")
        self.ax.set_ylabel("Energy")
        self.ax.grid(True)

        # Initial draw
        self.canvas.draw()

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
