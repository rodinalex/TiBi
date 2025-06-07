from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray


@dataclass
class BasisVector:
    """
    A basis vector in 3D space for a crystalline unit cell.

    Attributes
    ----------
    x : float
        x-component in Cartesian coordinates
    y : float
        y-component in Cartesian coordinates
    z : float
        z-component in Cartesian coordinates
    is_periodic : bool
        Flag denoting whether the crystal repeats in this direction

    Methods
    -------
    as_array()
       Convert the `BasisVector` to a NumPy array with 3 elements.
    """

    x: float
    y: float
    z: float
    is_periodic: bool = False

    def as_array(self) -> NDArray[np.float64]:
        """
        Convert the `BasisVector` to a NumPy array.

        Returns
        -------
        NDArray[np.float64]
            3D vector as a NumPy array [x, y, z]
        """
        return np.array([self.x, self.y, self.z], dtype=np.float64)
