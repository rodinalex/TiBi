from PySide6.QtCore import QObject
import numpy as np
import uuid

from models import Selection, UnitCell
from ui.constants import CF_BLUE, CF_SKY, CF_VERMILLION, DEFAULT_SCATTER_RADIUS
from views.plot_view import PlotView


class PlotController(QObject):
    """
    Controller for the 2D plot view.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
    plot_view : PlotView
        2D plot for displaying computed results.
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        plot_view: PlotView,
    ):
        """
        Initialize the band structure plot controller.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
        plot_view : PlotView
            2D plot for displaying computed results.
        """
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.plot_view = plot_view

    def plot_band_structure(self, states: list[int]):
        """
        Plot the band structure.

        Parameters
        ----------
        states : list[int]
            List of integers denoting onto which states
            the bands need to be projected.
        """

        self.plot_view.ax.clear()

        uc_id = self.selection.unit_cell
        if uc_id:
            bandstructure = self.unit_cells[uc_id].bandstructure
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
                pos_special_points = np.hstack(
                    (0, np.cumsum(step_special_points))
                )
                pos_special_points = (
                    pos_special_points / pos_special_points[-1]
                )
                # Compute projection magnitude squared for each k-point
                projections = np.sum(
                    np.abs(eigenvectors[:, states, :]) ** 2, axis=1
                )
                for band_idx in range(bands.shape[1]):
                    sizes = DEFAULT_SCATTER_RADIUS * projections[:, band_idx]

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

    def plot_dos(self, num_bins, states, plot_type, broadening):
        """
        Plot the density of states using the Brillouin zone grid.

        Parameters
        ----------
        num_bins : int
            Number of histogram bins
        states : list[int]
            List of integers denoting onto which states
            the bands need to be projected.
        plot_type : int
            Histogram (0) or Lorentzian (1)
        broadening : np.float64
            Broadening parameter for the Lorentzian DOS
        """
        self.plot_view.ax.clear()

        uc_id = self.selection.unit_cell

        if uc_id and self.unit_cells[uc_id].bz_grid.eigenvalues:
            bz_grid = self.unit_cells[uc_id].bz_grid

            # Set labels and grid
            self.plot_view.ax.set_xlabel("Energy")
            self.plot_view.ax.set_ylabel("DOS")

            # Extract the relevant qantities
            eigenvectors = np.array(
                bz_grid.eigenvectors
            )  # Array of 2D arrays of eigenvectors. Eigenvectors are columns
            # Create a single array of energies
            energies = np.concatenate(bz_grid.eigenvalues)
            # For each k-point and each eigenstate, keep only the selected
            # basis states. Sum over the squared amplitudes of the selected
            # basis states for each state

            # eigenvectors: shape (num_kpts, num_states, num_basis),
            # where num_states = num_basis
            # eigenvectors[:, states, :] selects the desired basis projections
            projections = np.concatenate(
                np.sum(np.abs(eigenvectors[:, states, :]) ** 2, axis=1), axis=0
            )

            bin_edges = np.histogram_bin_edges(energies, bins=num_bins)
            # Histogram or Lorentzian:
            if plot_type == 0:  # Histogram
                # Construct a histogram using the selected states' probability
                # for each eigenvalue as the weight
                hist, _ = np.histogram(
                    energies, bins=bin_edges, weights=projections
                )
                # Get the bind centers and normalize the histogram
                bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
                bin_width = bin_edges[1] - bin_edges[0]

                dos = hist / len(bz_grid.k_points)
                self.plot_view.ax.bar(
                    bin_centers,
                    dos,
                    width=bin_width,
                    color=CF_SKY,
                    edgecolor=CF_BLUE,
                )
            else:
                # Get pairwise differences between the energy grid
                # and the centers of the Lorentzians
                delta = energies[:, None] - bin_edges[None, :]
                lorentzians = (broadening / np.pi) / (delta**2 + broadening**2)
                dos = projections @ lorentzians / len(bz_grid.k_points)
                self.plot_view.ax.plot(
                    bin_edges, dos, linestyle="-", color=CF_SKY
                )

            # Draw the canvas
            self.plot_view.canvas.draw()
