from PySide6.QtCore import QObject
from models.data_models import AlwaysNotifyDataModel
import numpy as np

from views.bands_plot_view import BandStructurePlotView


class BandStructurePlotController(QObject):

    def __init__(
        self,
        band_structure: AlwaysNotifyDataModel,
        band_plot_view: BandStructurePlotView,
    ):
        super().__init__()
        self.band_structure = band_structure
        self.band_plot_view = band_plot_view

        # Connect to model updates
        self.band_structure.signals.updated.connect(self._update_plot)

    def _update_plot(self):
        k_path = self.band_structure.get("k_path", [])
        bands = self.band_structure.get("bands", [])
        # Get the positions along the path reflecting the point spacing
        step = np.linalg.norm(np.diff(k_path, axis=0), axis=1)
        pos = np.hstack((0, np.cumsum(step)))

        self.band_plot_view.ax.clear()
        for band_idx in range(bands.shape[1]):
            self.band_plot_view.ax.plot(pos, bands[:, band_idx], "b-")

        # Set labels and grid
        self.band_plot_view.ax.set_xlabel("k-vector")
        self.band_plot_view.ax.set_ylabel("Energy")
        self.band_plot_view.ax.grid(True)
        # Draw the canvas
        self.band_plot_view.canvas.draw()


#     # # Add vertical lines at special points
#     # special_distances = [distances[0]]  # First point

#     # # Add intermediate points where path changes direction
#     # for i in range(1, len(special_points)):
#     #     idx = i * (self.num_points // (len(special_points) - 1))
#     #     if idx < len(distances):
#     #         special_distances.append(distances[idx])

#     # # Add vertical lines at special points
#     # for dist in special_distances:
#     #     self.ax.axvline(x=dist, color="k", linestyle="--", alpha=0.5)

#     # # Set x-ticks at special points with labels
#     # self.ax.set_xticks(special_distances)
#     # if len(self.special_point_labels) >= len(special_distances):
#     #     self.ax.set_xticklabels(self.special_point_labels[: len(special_distances)])


#     # Draw the canvas
#     self.canvas.draw()
