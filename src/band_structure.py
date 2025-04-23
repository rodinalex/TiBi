import numpy as np


def interpolate_k_path(points, n_total):
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

    return np.array(k_path)


def band_compute(hamiltonian, k_path):
    # Interpolate the path
    bands = []

    for k in k_path:
        H = hamiltonian(k)
        eigenvalues = np.linalg.eigh(H)[0]  # Only eigenvalues
        bands.append(eigenvalues)

    bands = np.array(bands)
    return bands
