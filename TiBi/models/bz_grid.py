from dataclasses import dataclass, field
import numpy as np
from numpy.typing import NDArray


@dataclass
class BrillouinZoneGrid:
    """
    An object containing a system's computed Brillouin zone grid.

    Attributes
    ----------
    is_gamma_centered : bool
        A boolean marking whether the grid is Gamma centered or Monkhorst-Pack
    grid_divs : tuple[int, int, int]
        Number of divisions along each reciprocal basis vector
    k_points : list[NDArray[np.float64]]
        The coordinates of the grid points.
    eigenvalues : list[NDArray[np.float64]]
        A list of arrays, where each array contains eigenvalues
        corresponding to each point on the path.
    eigenvectors : list[NDArray[np.float64]]
        A list of 2D arrays, where each array contains the eigenvectors
        corresponding to each point on the path. The dimensionality of
        the square 2D arrays is given by the number of states in the unit cell.

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
        """Reset the band structure to the initial state."""
        self.k_points.clear()
        self.eigenvalues.clear()
        self.eigenvectors.clear()
