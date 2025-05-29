from PySide6.QtCore import QObject
import numpy as np

from models import BandStructure
from ui.constants import CF_VERMILLION, CF_SKY, DEFAULT_SCATTER_RADIUS
from views.plot_view import PlotView


class PlotController(QObject):
    """
    Controller for the 2D plot view.

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

    def plot_band_structure(
        self, bandstructure: BandStructure, states: list[int]
    ):
        """
        Plot the band structure.

        Parameters
        ----------
        bandstructure : BandStructure
            The band structure data to be plotted.
        states : list[int]
            List of integers denoting which onto which states
            the bands need to be projected
        """

        self.plot_view.ax.clear()
        # Set labels and grid
        self.plot_view.ax.set_xlabel("k-vector")
        self.plot_view.ax.set_ylabel("Energy")
        # Hide x-axis tick and keep the grid only for y-axis
        self.plot_view.ax.set_xticks([])
        self.plot_view.ax.grid(True, axis="y")
        # Extract the band structure quantities
        path = np.array(
            bandstructure.path
        )  # Array of momenta for which the bands were computed
        special_points = np.array(
            bandstructure.special_points
        )  # High symmetry points used to construct the BZ path
        bands = np.array(
            bandstructure.eigenvalues
        )  # Array of arrays of computed eigenvalues
        eigenvectors = np.array(
            bandstructure.eigenvectors
        )  # Array of 2D arrays of eigenvectors. Eigenvectors are columns

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

            for band_idx in range(bands.shape[1]):
                # Compute projection magnitude squared for each k-point
                projections = (
                    np.abs(eigenvectors[:, states, band_idx]) ** 2
                )  # shape (n_k, len(states))
                sizes = DEFAULT_SCATTER_RADIUS * np.sum(
                    projections, axis=1
                )  # shape (n_k,)

                # Plot the bands as lines
                self.plot_view.ax.plot(
                    pos, bands[:, band_idx], linestyle="-", color=CF_SKY
                )
                # Plot the bands as scatterplots
                self.plot_view.ax.scatter(
                    pos,
                    bands[:, band_idx],
                    s=sizes,
                    color=CF_VERMILLION,
                    alpha=0.6,
                )

            # Plot vertical lines at special points
            for x in pos_special_points:
                self.plot_view.ax.axvline(
                    x=x, color="gray", linestyle="--", linewidth=0.8
                )
        # Draw the canvas
        self.plot_view.canvas.draw()
