from PySide6.QtCore import QObject
import numpy as np

from src.tibitypes import BandStructure
from views.plot_view import PlotView


class PlotController(QObject):
    """
    Controller for the band structure plotting view.

    This controller manages the visualization of electronic band structures.
    It observes the band structure data model and updates the plot view
    whenever the data changes. The plotting logic is contained here,
    keeping the view focused solely on UI elements.

    Attributes
    ----------
    plot_view : PlotView
        2D plot for displaying computed results.
    """

    def __init__(
        self,
        plot_view: PlotView,
    ):
        """
        Initialize the band structure plot controller.

        Parameters
        ----------
        plot_view : PlotView
            2D plot for displaying computed results.
        """
        super().__init__()
        self.plot_view = plot_view

    def plot_band_structure(self, bandstructure: BandStructure):
        """
        Plot the band structure.

        Parameters
        ----------
        bandstructure : BandStructure
            The band structure data to be plotted.
        """

        self.plot_view.ax.clear()
        # Set labels and grid
        self.plot_view.ax.set_xlabel("k-vector")
        self.plot_view.ax.set_ylabel("Energy")
        self.plot_view.ax.set_xticks([])  # hide x-axis ticks
        self.plot_view.ax.grid(True, axis="y")  # grid only on y-axis
        path = np.array(bandstructure.path)
        bands = np.array(bandstructure.eigenvalues)
        special_points = np.array(bandstructure.special_points)
        if len(path) > 0 and len(bands) > 0:
            # Get the positions along the path reflecting the point spacing
            step = np.linalg.norm(np.diff(path, axis=0), axis=1)
            pos = np.hstack((0, np.cumsum(step)))

            pos = pos / pos[-1]  # Normalize the path length to 1

            # Repeat the same for special points
            step_special_points = np.linalg.norm(
                np.diff(special_points, axis=0), axis=1
            )
            pos_special_points = np.hstack((0, np.cumsum(step_special_points)))
            pos_special_points = pos_special_points / pos_special_points[-1]
            # Plot the bands
            for band_idx in range(bands.shape[1]):
                self.plot_view.ax.plot(pos, bands[:, band_idx], "b-")

            # Plot vertical lines at special points
            for x in pos_special_points:
                self.plot_view.ax.axvline(
                    x=x, color="gray", linestyle="--", linewidth=0.8
                )
        # Draw the canvas
        self.plot_view.canvas.draw()
