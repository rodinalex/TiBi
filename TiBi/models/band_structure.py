from dataclasses import dataclass, field
import numpy as np
from numpy.typing import NDArray


@dataclass
class BandStructure:
    """
    An object containing a system's band structure.

    Attributes
    ----------
    path : list[NDArray[np.float64]]
        A list of point coordinates along which the bands are calculated.
    special_points : list[NDArray[np.float64]]
        A list of high-symmetry point coordinates used for the path.
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
        Reset the band structure to the initial state.
    reset_bands()
        Reset the band structure by clearing the path, eigenvalues, and
        eigenvectors.
    add_point(point: NDArray[np.float64])
        Add a point to the special points path. Reset all other fields.
    remove_point()
        Remove the last point from the special points path. Reset all other
        fields.
    """

    path: list[NDArray[np.float64]] = field(default_factory=list)
    special_points: list[NDArray[np.float64]] = field(default_factory=list)
    eigenvalues: list[NDArray[np.float64]] = field(default_factory=list)
    eigenvectors: list[NDArray[np.float64]] = field(default_factory=list)

    def clear(self):
        """Reset the band structure to the initial state."""
        self.special_points.clear()
        self.reset_bands()

    def reset_bands(self):
        """
        Reset the band structure by clearing the path, eigenvalues, and
        eigenvectors.
        """
        self.path.clear()
        self.eigenvalues.clear()
        self.eigenvectors.clear()

    def add_point(self, point: NDArray[np.float64]):
        """
        Add a point to the special points path. Reset all other fields.

        Parameters
        ----------
        point : NDArray[np.float64]
            The point to be added to the special points path.
        """
        self.reset_bands()
        self.special_points.append(point)

    def remove_point(self):
        """
        Remove the last point from the special points path. Reset all other
        fields.
        """
        if self.special_points:
            self.special_points.pop(-1)
            self.reset_bands()
