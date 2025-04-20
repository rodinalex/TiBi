import numpy as np
from scipy.linalg import eigh
from typing import Callable, List, Tuple


def calculate_bands_along_path(
    hamiltonian_function: Callable,
    path_points: List[np.ndarray],
    num_points: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate the band structure along a path in k-space.
    
    Args:
        hamiltonian_function: Function that generates a Hamiltonian matrix for a given k-point
        path_points: List of k-points defining the path vertices in the Brillouin zone
        num_points: Total number of points to sample along the entire path
    
    Returns:
        Tuple containing:
        - k_points: 1D array of distance along the path for each sampled point
        - bands: 2D array of eigenvalues for each band at each k-point
                (shape: num_bands × num_points)
    """
    if len(path_points) < 2:
        raise ValueError("Path must contain at least 2 points")
    
    # Calculate segment lengths to distribute points proportionally
    segments = []
    total_length = 0
    
    for i in range(len(path_points) - 1):
        p1 = np.array(path_points[i])
        p2 = np.array(path_points[i+1])
        segment_length = np.linalg.norm(p2 - p1)
        segments.append((p1, p2, segment_length))
        total_length += segment_length
    
    # Allocate points to segments proportionally to their length
    k_points = []
    k_distances = []
    current_distance = 0
    
    # Calculate how many points to use for each segment (proportional to length)
    remaining_points = num_points
    allocated_points = []
    
    for _, _, length in segments:
        # Proportional allocation (at least 2 points per segment)
        segment_points = max(2, int(round(length / total_length * num_points)))
        # Ensure we don't exceed total points
        if sum(allocated_points) + segment_points > num_points:
            segment_points = num_points - sum(allocated_points)
        allocated_points.append(segment_points)
    
    # Adjust last segment to make sure we use exactly num_points
    difference = num_points - sum(allocated_points)
    allocated_points[-1] += difference
    
    # Generate points along each segment
    bands = None
    current_distance = 0
    
    for i, ((p1, p2, _), segment_points) in enumerate(zip(segments, allocated_points)):
        # Create points along this segment
        for j in range(segment_points):
            # Last point of segment
            if j == segment_points - 1 and i < len(segments) - 1:
                alpha = 1.0
            else:
                alpha = j / (segment_points - 1) if segment_points > 1 else 0
            
            # Interpolate between segment endpoints
            k = p1 * (1 - alpha) + p2 * alpha
            
            # Calculate distance along path
            if j > 0:
                current_distance += np.linalg.norm(k - prev_k)
            
            # Store k-point and its distance
            k_points.append(k)
            k_distances.append(current_distance)
            prev_k = k
            
            # Calculate eigenvalues at this k-point
            H = hamiltonian_function(k)
            eigenvalues, _ = eigh(H)
            
            # Initialize bands array if first point
            if bands is None:
                bands = np.zeros((len(eigenvalues), num_points))
            
            # Store eigenvalues
            bands[:, len(k_distances) - 1] = eigenvalues
    
    return np.array(k_distances), bands


def get_special_points(unit_cell, bz_path):
    """
    Process the BZ path points from the UI to get k-points
    in the reciprocal basis for band structure calculation.
    
    Args:
        unit_cell: UnitCell object with reciprocal vectors
        bz_path: List of points in Cartesian coordinates from BZ path selection
        
    Returns:
        Tuple containing:
        - k_points: List of k-points in reciprocal basis
        - special_points: Indices of the special points in the path
    """
    # Get reciprocal vectors
    reciprocal_vectors = unit_cell.reciprocal_vectors()
    num_periodic = len(reciprocal_vectors)
    
    if num_periodic == 0:
        raise ValueError("Unit cell has no periodic directions")
    
    # Matrix of reciprocal vectors
    G_matrix = np.array(reciprocal_vectors)
    
    # Convert Cartesian coordinates to reciprocal basis
    k_points = []
    
    for point in bz_path:
        # Ensure point has correct dimensionality (trim or pad as needed)
        cart_point = np.array(point)
        if len(cart_point) < 3:
            cart_point = np.pad(cart_point, (0, 3 - len(cart_point)))
        elif len(cart_point) > 3:
            cart_point = cart_point[:3]
        
        # Solve for k-point in reciprocal basis
        # We need to solve: cart_point = G_matrix.T @ k_coords
        # For under-determined systems (num_periodic < 3), we use least squares
        if num_periodic == 3:
            k_coords = np.linalg.solve(G_matrix.T, cart_point)
        else:
            # Use least squares for underdetermined systems
            k_coords, _, _, _ = np.linalg.lstsq(G_matrix.T, cart_point, rcond=None)
            
        # Only keep the coordinates along periodic directions
        k_coords = k_coords[:num_periodic]
        k_points.append(k_coords)
    
    # Indices of special points are just the endpoints of the path
    special_points = list(range(len(bz_path)))
    
    return k_points, special_points