from dataclasses import dataclass, field
import uuid
from typing import Tuple, List, Dict, Any
import numpy as np
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DM
from scipy.spatial import Voronoi
import itertools


@dataclass
class BasisVector:
    """
    Represents a basis vector in 3D space for a crystalline unit cell.

    A unit cell is defined by three basis vectors that form a parallelepiped.
    The is_periodic flag indicates whether the crystal repeats along this direction.
    A non-periodic direction represents a finite dimension of the system.

    Attributes:
        x: x-component in Cartesian coordinates
        y: y-component in Cartesian coordinates
        z: z-component in Cartesian coordinates
        is_periodic: Whether the crystal repeats in this direction
    """

    x: float  # x-component in Cartesian coordinates
    y: float  # y-component in Cartesian coordinates
    z: float  # z-component in Cartesian coordinates
    is_periodic: bool = False  # Whether the crystal repeats in this direction

    def as_array(self) -> np.ndarray:
        """
        Convert the basis vector to a NumPy array.

        Returns:
            numpy.ndarray: 3D vector as a NumPy array [x, y, z]
        """
        return np.array([self.x, self.y, self.z])


@dataclass
class State:
    """
    Represents a quantum state (like an orbital) within a site.

    Each state has a name and belongs to a specific site in the unit cell.
    States are the fundamental entities between which hopping can occur.
    They represent electronic quantum states like atomic orbitals or bands.

    Attributes:
        name: Name of the state (e.g., "s", "px", "py", etc.)
        id: Unique identifier for the state (UUID)
    """

    name: str  # Name of the state (e.g., "s", "px", "py", etc.)
    id: uuid.UUID = field(default_factory=uuid.uuid4)  # Unique identifier


@dataclass
class Site:
    """
    Represents a physical site (like an atom) within a unit cell.

    Sites are positioned using fractional coordinates relative to the unit cell's
    basis vectors. Each site can contain multiple quantum states (orbitals).
    The position is specified using fractional coordinates within the unit cell,
    where each coordinate ranges from 0 to 1.

    Attributes:
        name: Name of the site (e.g., atom name like "C", "Fe", etc.)
        c1: Fractional coordinate along the first basis vector (0-1)
        c2: Fractional coordinate along the second basis vector (0-1)
        c3: Fractional coordinate along the third basis vector (0-1)
        states: Dictionary mapping state UUIDs to State objects
        id: Unique identifier for the site (UUID)
    """

    name: str  # Name of the site (e.g., atom name like "C", "Fe", etc.)
    c1: float  # Fractional coordinate along the first basis vector (0-1)
    c2: float  # Fractional coordinate along the second basis vector (0-1)
    c3: float  # Fractional coordinate along the third basis vector (0-1)
    states: dict[uuid.UUID, State] = field(default_factory=dict)  # States at this site
    id: uuid.UUID = field(default_factory=uuid.uuid4)  # Unique identifier


@dataclass
class UnitCell:
    """
    Represents a crystalline unit cell with sites, states, and hopping parameters.

    The unit cell is defined by three basis vectors and contains sites (atoms).
    Each site can have multiple states (orbitals). Hopping terms define how electrons
    can move between states, both within the unit cell and between periodic images.

    The hopping dictionary has a complex structure:
    - Keys are pairs of state UUIDs (destination_state_id, source_state_id)
    - Values are lists of (displacement, amplitude) pairs where:
      - displacement is a tuple of three integers (n1,n2,n3) indicating which periodic
        image of the unit cell is involved (0,0,0 means within the same unit cell)
      - amplitude is a complex number representing the hopping strength and phase

    Attributes:
        name: Name of the unit cell
        v1: First basis vector
        v2: Second basis vector
        v3: Third basis vector
        sites: Dictionary mapping site UUIDs to Site objects
        hoppings: Dictionary of hopping terms between states
        id: Unique identifier for the unit cell (UUID)
    """

    name: str  # Name of the unit cell
    v1: BasisVector  # First basis vector
    v2: BasisVector  # Second basis vector
    v3: BasisVector  # Third basis vector
    sites: dict[uuid.UUID, Site] = field(
        default_factory=dict
    )  # Sites in this unit cell
    hoppings: dict[
        Tuple[uuid.UUID, uuid.UUID],  # (destination_state_id, source_state_id)
        list[
            Tuple[Tuple[int, int, int], np.complex128]
        ],  # [(displacement, amplitude), ...]
    ] = field(default_factory=dict)
    site_colors: dict[uuid.UUID] = field(
        default_factory=dict
    )  # Site colors to be used for plotting
    site_sizes: dict[uuid.UUID, float] = field(
        default_factory=dict
    )  # Radii of the site spheres to be used for plotting
    id: uuid.UUID = field(default_factory=uuid.uuid4)  # Unique identifier

    def volume(self) -> float:
        """
        Compute the volume of the unit cell using the scalar triple product.

        Calculates the volume of the parallelepiped defined by the three basis vectors
        using the formula V = a1·(a2×a3), where a1, a2, and a3 are the basis vectors.

        Returns:
            float: Volume of the unit cell in cubic Angstroms (or whatever units the basis vectors use)
        """
        a1, a2, a3 = [v.as_array() for v in [self.v1, self.v2, self.v3]]
        return np.dot(a1, np.cross(a2, a3))

    def reciprocal_vectors(self) -> list[np.ndarray]:
        """
        Compute the reciprocal lattice vectors for the periodic directions.

        Calculates the reciprocal lattice vectors corresponding to the periodic directions
        in the unit cell. The number of reciprocal vectors depends on the number of
        periodic dimensions (0-3). The reciprocal vectors satisfy the orthogonality
        condition: G_i · a_j = 2π δ_ij, where G_i are reciprocal vectors and a_j are
        real-space basis vectors.

        Returns:
            list[np.ndarray]: List of 3D reciprocal vectors (0 to 3 items depending on periodicity)
        """
        basis_vectors = [v for v in [self.v1, self.v2, self.v3] if v.is_periodic]
        num_periodic = len(basis_vectors)

        if num_periodic == 0:
            return []

        elif num_periodic == 1:
            a1 = basis_vectors[0].as_array()
            G1 = 2 * np.pi * a1 / np.dot(a1, a1)
            return [G1]

        elif num_periodic == 2:
            a1, a2 = [v.as_array() for v in basis_vectors]
            normal = np.cross(a1, a2)
            G1 = 2 * np.pi * np.cross(normal, a2) / np.dot(a1, np.cross(a2, normal))
            G2 = 2 * np.pi * np.cross(a1, normal) / np.dot(a2, np.cross(normal, a1))
            return [G1, G2]

        elif num_periodic == 3:
            a1, a2, a3 = [v.as_array() for v in basis_vectors]
            volume = np.dot(a1, np.cross(a2, a3))
            G1 = 2 * np.pi * np.cross(a2, a3) / volume
            G2 = 2 * np.pi * np.cross(a3, a1) / volume
            G3 = 2 * np.pi * np.cross(a1, a2) / volume
            return [G1, G2, G3]

        else:
            raise ValueError("Invalid number of periodic vectors.")

    def reduced_basis(self, scale: float = 1e6) -> list[BasisVector]:
        """
        Return a reduced set of periodic basis vectors using LLL algorithm.

        Applies the Lenstra-Lenstra-Lovász (LLL) lattice reduction algorithm to find
        a more orthogonal set of basis vectors that spans the same lattice. This is
        useful for finding a "nicer" representation of the unit cell, with basis vectors
        that are shorter and more orthogonal to each other.

        Only the periodic vectors are reduced. Non-periodic vectors are left unchanged.

        Args:
            scale: A float to scale the vectors for integer reduction (default: 1e6)
                  Used because the LLL algorithm works with integer matrices.

        Returns:
            list[BasisVector]: A list of BasisVector objects representing the reduced basis
        """
        vs = [self.v1, self.v2, self.v3]
        # Determine which vectors are periodic
        periodic_flags = [v.is_periodic for v in vs]
        # Extract the periodic vectors. Scale them to be used in reduction
        periodic_vectors = [
            np.round(scale * vs[ii].as_array()).astype(int)
            for ii in range(3)
            if periodic_flags[ii]
        ]

        # If there are fewer than 2 periodic vectors, LLL reduction isn't meaningful
        if len(periodic_vectors) < 2:
            return vs  # Return unchanged

        # Reduced vectors
        reduced = DM(periodic_vectors, ZZ).lll().to_list()
        # Rebuild full list with reduced periodic vectors in original order
        reduced_basis = []
        # Rescale
        reduced_vectors = [np.array(vec, dtype=float) / scale for vec in reduced]

        jj = 0  # Index for reduced_vectors
        for ii in range(3):
            if periodic_flags[ii]:
                vec = reduced_vectors[jj]
                reduced_basis.append(BasisVector(*vec, is_periodic=True))
                jj += 1
            else:
                reduced_basis.append(vs[ii])  # Unchanged
        return reduced_basis

    def get_states(self):
        """
        Extract all states from a unit cell along with their identifying information.

        This is a helper function used by UI components to get a flattened list of all
        states in the unit cell, regardless of which site they belong to. It makes it
        easier to display states in UI components like dropdown menus or lists.

        Returns:
            tuple: A tuple containing:
                - states (list): List of State objects
                - state_info (list): List of tuples (site_name, site_id, state_name, state_id)
                  that provides context for each state (which site it belongs to)
        """
        states = []
        state_info = []
        for site_id, site in self.sites.items():
            for state_id, state in site.states.items():
                states.append(state)
                state_info.append((site.name, site_id, state.name, state_id))
        return (states, state_info)

    def get_BZ(self):
        """
        Compute the Brillouin zone vertices and faces.

        The Brillouin zone is the Wigner-Seitz cell of the reciprocal lattice.
        This method calculates the vertices and faces of the Brillouin zone
        using Voronoi construction. The dimensionality of the BZ depends on
        the number of periodic dimensions in the unit cell (0-3).

        For 1D, bz_vertices contains two points defining the BZ boundary.
        For 2D, bz_faces contains the edges of the 2D BZ polygon.
        For 3D, bz_faces contains the polygonal faces of the 3D BZ polyhedron.

        Returns:
            tuple: A tuple containing:
                - bz_vertices (numpy.ndarray): Array of Brillouin zone vertex coordinates
                - bz_faces (list): List where each element contains coordinates of points
                  defining a BZ boundary (edge in 2D, face in 3D)
        """
        n_neighbors = 1  # Number of neighboring reciprocal lattice points to consider
        ranges = range(-n_neighbors, n_neighbors + 1)

        reciprocal_vectors = self.reciprocal_vectors()
        dim = len(reciprocal_vectors)

        if dim == 0:
            bz_vertices = np.array([])
            bz_faces = np.array([])

        elif dim == 1:
            G1 = reciprocal_vectors[0]
            bz_vertices = np.array([[G1[0] / 2], [-G1[0] / 2]])
            bz_faces = np.array([])

        else:

            if dim == 2:
                g1 = reciprocal_vectors[0][0:2]
                g2 = reciprocal_vectors[1][0:2]
                points = [
                    ii * g1 + jj * g2
                    for ii, jj in itertools.product(ranges, ranges)
                    if (ii != 0 or jj != 0)
                ]
                all_points = np.vstack([np.zeros(2), points])
            else:
                g1 = reciprocal_vectors[0]
                g2 = reciprocal_vectors[1]
                g3 = reciprocal_vectors[2]
                points = [
                    ii * g1 + jj * g2 + kk * g3
                    for ii, jj, kk in itertools.product(ranges, ranges, ranges)
                    if (ii != 0 or jj != 0 or kk != 0)
                ]
                all_points = np.vstack([np.zeros(3), points])

            vor = Voronoi(all_points)

            # Start by getting the vertices of the Brillouin zone
            # The first Brillouin zone is the Voronoi cell around the origin (index 0)
            origin_region = vor.point_region[
                0
            ]  # Tells which Voronoi cell corresponds to the point at the origin
            vertex_indices = vor.regions[
                origin_region
            ]  # Tells which vertices defining Voronoi cell bound the relevant region

            # Extract vertices
            bz_vertices = vor.vertices[
                vertex_indices
            ]  # Get the actual coordinates of the vertices of the points bounding the region

            # Next, get a list of lists that defines the faces of the Brillouin zone
            bz_faces = []
            # bz_faces = np.array([])
            # ridge_points is a list of tuples corresponding to
            # pairs of elements of all_points that are separated by a Voronoi boundary
            for num, p in enumerate(vor.ridge_points):
                # If one of the elements in the pair is the origin (index 0),
                # this ridge separates the BZ from its neighbors
                if p[0] == 0 or p[1] == 0:
                    # ridge_vertices[num] contains the indices of the vertices bounding the ridge
                    ridge_vertices = vor.ridge_vertices[num]
                    # finally, get the coordinates of the ridge vertices from their indices
                    face = vor.vertices[ridge_vertices]
                    bz_faces.append(face)

        return bz_vertices, bz_faces

    def get_hamiltonian_function(self):
        """
        Generate a function that computes the Hamiltonian matrix for a given k-point.

        This method creates a closure that precomputes all k-independent data needed for
        the Hamiltonian, and returns a function that efficiently builds the Hamiltonian
        matrix for any k-point in the Brillouin zone.

        The returned function implements Bloch's theorem by transforming the real-space
        Hamiltonian (with hopping terms potentially spanning multiple unit cells) into
        k-space. This allows band structure calculations along arbitrary paths in k-space.

        The dimension of the k-point must match the number of periodic dimensions in
        the unit cell (1D, 2D, or 3D).

        Returns:
            function: A function that takes k-points (numpy array) and returns a
                     complex Hamiltonian matrix (numpy array of shape [n_states, n_states])
        """
        # Get the list of all states in the unit cell for determining the Hamiltonian size
        states, state_info = self.get_states()

        # Get the reciprocal lattice vectors
        reciprocal_vectors = self.reciprocal_vectors()
        num_periodic = len(reciprocal_vectors)

        # Create a mapping from state IDs to indices in the Hamiltonian matrix
        # state_id identifies the state, idx is its index in the Hamiltonian matrix (to keep track of rows/columns)
        state_to_idx = {
            state_id: idx for idx, (_, _, _, state_id) in enumerate(state_info)
        }

        # Store the total number of states for matrix size
        n_states = len(states)
        # Basis vectors as arrays
        v1 = self.v1.as_array() if self.v1.is_periodic else np.zeros(3)
        v2 = self.v2.as_array() if self.v2.is_periodic else np.zeros(3)
        v3 = self.v3.as_array() if self.v3.is_periodic else np.zeros(3)

        # Define the Hamiltonian function that will be returned
        def hamiltonian(k):
            """
            Compute the Hamiltonian matrix for a given k-point.

            This function constructs the Hamiltonian matrix in k-space according to the
            tight-binding model defined by the unit cell and its hopping parameters.
            The matrix elements include phase factors exp(-i k·R) for hoppings between
            different unit cells, as required by Bloch's theorem.

            Args:
                k: k-point vector in the basis of reciprocal lattice vectors
                   If the system has n periodic directions, k should be an n-dimensional vector

            Returns:
                numpy.ndarray: Complex Hamiltonian matrix of size (n_states, n_states)
                              The eigenvalues of this matrix give the energy bands at k
            """
            # Validate the k-point dimension matches the number of periodic directions
            if len(k) != num_periodic:
                raise ValueError(
                    f"k-point dimension ({len(k)}) does not match number of periodic directions ({num_periodic})"
                )

            # Initialize the Hamiltonian matrix with zeros
            H = np.zeros((n_states, n_states), dtype=np.complex128)

            # Fill the Hamiltonian matrix
            for (dest_id, source_id), hoppings in self.hoppings.items():
                dest_idx = state_to_idx[dest_id]  # Destination state index
                source_idx = state_to_idx[source_id]  # Source state index

                for displacement, amplitude in hoppings:
                    d1, d2, d3 = displacement

                    # Calculate the real-space displacement vector
                    # This is the sum of the periodic vectors scaled by the displacement
                    R = d1 * v1 + d2 * v2 + d3 * v3

                    # Apply Bloch phase factor: exp(-i k·R)
                    if num_periodic == 0:
                        phase = 1.0
                    else:
                        phase = np.exp(1j * np.dot(k, R[0:num_periodic]))

                    # Add the term to the Hamiltonian
                    H[dest_idx, source_idx] += amplitude * phase

            return H

        return hamiltonian
