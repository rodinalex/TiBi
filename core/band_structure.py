import numpy as np
from numpy.typing import NDArray


def interpolate_k_path(points: list[NDArray[np.float64]], n_total: int):
    """
    Interpolate a path through k-space special points.

    The path has the special points distributed along
    segments proportionally to their lengths in reciprocal space.

    Parameters
    ----------
        points : list[NDArray[np.float64]]
            List or array of k-points defining the path
        n_total : int
            Total number of points to distribute along the entire path

    Returns
    -------
        NDArray[NDArray[np.float64]]
            Array of interpolated k-points along the path
    """
    points = np.array(points)
    # Get the distances between consecutive points
    distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
    # Get the total distance of the path in the reciprocal space
    total_distance = np.sum(distances)

    # Allocate number of points per segment
    n_segments = len(points) - 1
    fractions = distances / total_distance
    n_points_segment = [max(2, int(round(f * n_total))) for f in fractions]

    # Build the full path
    k_path = []
    for ii in range(n_segments):
        start = points[ii]
        end = points[ii + 1]
        n_pts = n_points_segment[ii]
        segment = np.linspace(start, end, n_pts, endpoint=False)
        k_path.extend(segment)

    # Add the final high-symmetry point
    k_path.append(points[-1])

    return k_path


def diagonalize_hamitonian(hamiltonian, points):
    """
    Compute electronic for the collection of points.

    Parameters
    ----------
        hamiltonian
            Function that generates a Hamiltonian matrix for a given k-point
        points : NDArray[NDArray[np.float64]]
            Array of k-points along which to calculate bands

    Returns
    -------
        eigenvalues : list[NDArray[np.float64]]
            Array of shape (n_kpoints, n_bands) containing the energy
            eigenvalues at each k-point
        eigenvectors : list[NDArray[np.float64]]
            Array of shape (n_kpoints, n_bands, n_bands) containing the
            eigenvectors at each k-point
    """
    eigenvalues = []
    eigenvectors = []

    for k in points:
        H = hamiltonian(k)
        solution = np.linalg.eigh(H)
        eigenvalues.append(solution[0])
        eigenvectors.append(solution[1])
    return eigenvalues, eigenvectors
