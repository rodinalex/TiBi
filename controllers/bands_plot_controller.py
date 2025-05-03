from PySide6.QtCore import QObject
from models.data_models import AlwaysNotifyDataModel
import numpy as np

from views.bands_plot_view import BandStructurePlotView


class BandStructurePlotController(QObject):
    """
    Controller for the band structure plotting view.

    This controller manages the visualization of electronic band structures.
    It observes the band structure data model and updates the plot view
    whenever the data changes. The plotting logic is contained here,
    keeping the view focused solely on UI elements.
    """

    def __init__(
        self,
        band_structure: AlwaysNotifyDataModel,
        band_plot_view: BandStructurePlotView,
    ):
        """
        Initialize the band structure plot controller.

        Args:
            band_structure: Data model containing band structure calculation results
            band_plot_view: View that displays the band structure plot
        """
        super().__init__()
        self.band_structure = band_structure
        self.band_plot_view = band_plot_view

        # Connect to model updates
        self.band_structure.signals.updated.connect(self._update_plot)

    def _update_plot(self):
        """
        Update the band structure plot with current data.

        This method is called whenever the band structure data model changes.
        It retrieves the current k-path and band data, transforms them into
        a format suitable for plotting, and updates the matplotlib figure.
        """

        k_path = self.band_structure.get("k_path")
        bands = self.band_structure.get("bands")

        self.band_plot_view.ax.clear()
        # Set labels and grid
        self.band_plot_view.ax.set_xlabel("k-vector")
        self.band_plot_view.ax.set_ylabel("Energy")
        self.band_plot_view.ax.grid(True)

        if k_path is not None and bands is not None:
            # Get the positions along the path reflecting the point spacing
            step = np.linalg.norm(np.diff(k_path, axis=0), axis=1)
            pos = np.hstack((0, np.cumsum(step)))

            for band_idx in range(bands.shape[1]):
                self.band_plot_view.ax.plot(pos, bands[:, band_idx], "b-")

        # Draw the canvas
        self.band_plot_view.canvas.draw()


# Future enhancement: Add special point labels and vertical lines
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
