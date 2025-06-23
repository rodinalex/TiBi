from dataclasses import dataclass, field
import numpy as np
from numpy.typing import NDArray


@dataclass
class BrillouinZoneGrid:
    """
    A `UnitCell` attribute containing a system's computed Brillouin zone grid.

    Attributes
    ----------
    is_gamma_centered : bool
        A boolean marking whether the grid is Gamma centered or Monkhorst-Pack
    grid_divs : tuple[int, int, int]
        Number of divisions along each reciprocal basis vector
    k_points : list[NDArray[np.float64]]
        The coordinates of the grid points.
    eigenvalues : list[NDArray[np.float64]]
        A list of arrays, where each array contains eigenvalues (energies)
        corresponding to each grid point.
    eigenvectors : list[NDArray[np.float64]]
        A list of square 2D arrays, where each array contains the eigenvectors
        corresponding to each grid point. The
        eigenvectors are the columns of the 2D arrays.

    Methods
    -------
    clear()
        Reset the grid to the initial state.
    """

    is_gamma_centered: bool = True
    grid_divs: tuple[int, int, int] = (30, 30, 30)
    k_points: list[NDArray[np.float64]] = field(default_factory=list)
    eigenvalues: list[NDArray[np.float64]] = field(default_factory=list)
    eigenvectors: list[NDArray[np.float64]] = field(default_factory=list)

    def clear(self):
        """
        Reset the grid to the initial state.

        The k points, eigenvalues, and eigenvectors are cleared,
        while the gamma-centered flag and the grid divisions remain unchanged.
        """
        self.k_points.clear()
        self.eigenvalues.clear()
        self.eigenvectors.clear()
