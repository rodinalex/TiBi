from dataclasses import dataclass, field
import itertools
import numpy as np
from numpy.typing import NDArray
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DM
from scipy.spatial import Voronoi
import uuid

from .band_structure import BandStructure
from .basis_vector import BasisVector
from .bz_grid import BrillouinZoneGrid
from .site import Site


@dataclass
class UnitCell:
    """
    The funtamental object describing a crystal.

    The `UnitCell` is defined by three `BasisVector`s and contains `Site`s
    and hopping terms between `State`s. Additionally, `UnitCell` carries
    the calculated `BandStructure` and `BrillouinZoneGrid` objects.

    Attributes
    ----------
    name : str
        Name of the unit cell
    v1, v2, v3 : BasisVector
        Basis vectors
    sites : dict[uuid.UUID, Site]
        Dictionary mapping site UUIDs to `Site` objects
    hoppings : dict[tuple[uuid.UUID, uuid.UUID], \
        list[tuple[tuple[int, int, int], np.complex128]]]
        Dictionary of hopping terms between states.
        Keys are pairs of state UUIDs (destination_state_id,
        source_state_id).
        Values are lists of (displacement, amplitude) pairs where:

        - displacement is a tuple of three integers (n1,n2,n3) indicating
        which periodic image of the unit cell is involved
        (0,0,0 means within the same unit cell)
        - amplitude is a complex number
    bandstructure : BandStructure
        Band structure object for the `UnitCell`
    bz_grid: BrillouinZoneGrid
        Grid of points in the Brillouin zone
    id : uuid.UUID
        Unique identifier for the `UnitCell`

    Methods
    -------
    volume()
        Compute the volume of the `UnitCell` using the scalar triple
        product.
    is_hermitian()
        Check whether the hoppings are Hermitian.
    reciprocal_vectors()
        Compute the reciprocal lattice vectors for the periodic directions.
    reduced_basis()
        Return a reduced set of periodic `BasisVector`s using LLL
        algorithm.
    get_states()
        Extract all `State`s from a `UnitCell` along with their identifying
        information.
    get_BZ()
        Compute the Brillouin zone vertices and faces.
    get_hamiltonian_function()
        Generate a function that computes the Hamiltonian matrix
        for a given k-point.
    """

    name: str
    v1: BasisVector
    v2: BasisVector
    v3: BasisVector
    sites: dict[uuid.UUID, Site] = field(default_factory=dict)
    hoppings: dict[
        tuple[uuid.UUID, uuid.UUID],
        list[tuple[tuple[int, int, int], np.complex128]],
    ] = field(default_factory=dict)
    bandstructure: BandStructure = field(default_factory=BandStructure)
    bz_grid: BrillouinZoneGrid = field(default_factory=BrillouinZoneGrid)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def volume(self) -> np.float64:
        """
        Compute the volume of the `UnitCell` using the scalar triple product.

        Returns
        -------
        np.float64
            Volume of the unit cell in arbitrary units
        """
        a1, a2, a3 = [v.as_array() for v in [self.v1, self.v2, self.v3]]
        return np.abs(np.dot(a1, np.cross(a2, a3)))

    def is_hermitian(self) -> bool:
        """
        Check whether the hoppings are Hermitian.

        For each key (destination_state_id, source_state_id) in the
        hoppings dictionary, check if there is a key
        (source_state_id, destination_state_id). If so, check that the entries
        are related by Hermitian conjugation.

        Returns
        -------
        bool
            `True` if Hermitian; `False` if not.
        """
        hermitian = True

        for key, val in self.hoppings.items():
            s1 = key[0]
            s2 = key[1]

            hop = set(val)
            hop_transpose = set(self.hoppings.get((s2, s1), []))

            hop_neg_conj = set(
                ((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop
            )

            if hop_neg_conj != hop_transpose:
                hermitian = False
                break
        return hermitian

    def reciprocal_vectors(self) -> list[NDArray[np.float64]]:
        """
        Compute the reciprocal lattice vectors for the periodic directions.

        Calculates the reciprocal lattice vectors corresponding to the
        periodic directions in the `UnitCell`.
        The number of reciprocal vectors depends on the number of
        periodic dimensions (0-3).

        Returns
        -------
        list[NDArray[np.float64]]
            List of 3D reciprocal vectors (0 to 3 items depending on
            periodicity)
        """
        basis_vectors = [
            v for v in [self.v1, self.v2, self.v3] if v.is_periodic
        ]
        num_periodic = len(basis_vectors)

        if num_periodic == 0:
            return []

        elif num_periodic == 1:
            a1 = basis_vectors[0].as_array()
            g1 = 2 * np.pi * a1 / np.dot(a1, a1)
            return [g1]

        elif num_periodic == 2:
            a1, a2 = [v.as_array() for v in basis_vectors]
            normal = np.cross(a1, a2)
            g1 = (
                2
                * np.pi
                * np.cross(normal, a2)
                / np.dot(a1, np.cross(a2, normal))
            )
            g2 = (
                2
                * np.pi
                * np.cross(a1, normal)
                / np.dot(a2, np.cross(normal, a1))
            )
            return [g1, g2]

        elif num_periodic == 3:
            a1, a2, a3 = [v.as_array() for v in basis_vectors]
            volume = np.dot(a1, np.cross(a2, a3))
            g1 = 2 * np.pi * np.cross(a2, a3) / volume
            g2 = 2 * np.pi * np.cross(a3, a1) / volume
            g3 = 2 * np.pi * np.cross(a1, a2) / volume
            return [g1, g2, g3]

        else:
            raise ValueError("Invalid number of periodic vectors.")

    def reduced_basis(self, scale: float = 1e6) -> list[BasisVector]:
        """
        Return a reduced set of periodic `BasisVector`s using LLL algorithm.

        Applies the Lenstra-Lenstra-Lovász (LLL) lattice reduction algorithm
        to find a more orthogonal set of basis vectors that spans the same
        lattice.

        Only the periodic `BasisVector`s are reduced.
        Non-periodic vectors are left unchanged.

        Parameters
        ----------
        scale : float = 1e6
            A float to scale the vectors for integer reduction.
            Used because the LLL algorithm works with integer matrices.

        Returns
        -------
        list[BasisVector]
            A list of BasisVector objects representing the reduced basis
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

        # If there are fewer than 2 periodic vectors,
        # LLL reduction isn't meaningful
        if len(periodic_vectors) < 2:
            return vs  # Return unchanged

        # Reduced vectors
        reduced = DM(periodic_vectors, ZZ).lll().to_list()
        # Rebuild full list with reduced periodic vectors in original order
        reduced_basis = []
        # Rescale
        reduced_vectors = [
            np.array(vec, dtype=float) / scale for vec in reduced
        ]

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
        Extract all `State`s and their information from a `UnitCell` .

        This is a helper function used by UI components to get a flattened
        list of all states in the unit cell, regardless of which site they
        belong to. It makes it easier to display states in UI components
        like dropdown menus or lists.

        Returns
        -------
        tuple[list[State], list[tuple[str, uuid.UUID, str, uuid.UUID]]]
            A tuple containing a list of `State` objects and a list of
            tuples (site_name, site_id, state_name, state_id)
            providing context for each state (which site it belongs to).
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

        Returns
        -------
        tuple[NDArray[NDArray[np.float64]],\
            NDArray[NDArray[NDArray[np.float64]]]]
            The first element of the tuple gives the BZ vertex coordinates.
            The second element gives a list of faces, where each face is
            defined by vertex points. In 2D, the "faces" are edges.
        """
        n_neighbors = (
            1  # Number of neighboring reciprocal lattice points to consider
        )
        ranges = range(-n_neighbors, n_neighbors + 1)

        reciprocal_vectors = self.reciprocal_vectors()
        dim = len(reciprocal_vectors)

        if dim == 0:
            bz_vertices = np.array([])
            bz_faces = np.array([])

        elif dim == 1:
            g1 = reciprocal_vectors[0]
            bz_vertices = np.array([[g1[0] / 2], [-g1[0] / 2]])
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
            # The first Brillouin zone is the Voronoi cell around
            # the origin (index 0)
            origin_region = vor.point_region[
                0
            ]  # Tells which Voronoi cell corresponds to origin point
            vertex_indices = vor.regions[
                origin_region
            ]  # Tells which vertices defining Voronoi cell bound the region

            # Extract vertices
            bz_vertices = vor.vertices[
                vertex_indices
            ]  # Get the coordinates of the vertices

            # Next, get a list of lists that defines the faces of the BZ
            bz_faces = []
            # ridge_points is a list of tuples corresponding to
            # pairs of elements of all_points that are separated by
            # a Voronoi boundary
            for num, p in enumerate(vor.ridge_points):
                # If one of the elements in the pair is the origin (index 0),
                # this ridge separates the BZ from its neighbors
                if p[0] == 0 or p[1] == 0:
                    # ridge_vertices[num] contains the indices of the vertices
                    # bounding the ridge
                    ridge_vertices = vor.ridge_vertices[num]
                    # finally, get the coordinates of the ridge vertices from
                    # their indices
                    face = vor.vertices[ridge_vertices]
                    bz_faces.append(face)
            # bz_faces = np.array(bz_faces)
        return bz_vertices, bz_faces

    def get_hamiltonian_function(self):
        """
        Generate a function that computes the Hamiltonian matrix.

        This method creates a closure that precomputes all k-independent
        data needed for the Hamiltonian, and returns a function that builds
        the Hamiltonian matrix for any k-point in the Brillouin zone.

        The dimension of the k-point must match the number of periodic
        dimensions in the unit cell (1D, 2D, or 3D).

        Returns
        -------
        function
            A function that takes k-points (numpy array) and returns a
            complex Hamiltonian matrix.
        """
        # Get the list of all states in the unit cell for
        # determining the Hamiltonian size
        states, state_info = self.get_states()

        # Get the reciprocal lattice vectors
        reciprocal_vectors = self.reciprocal_vectors()
        num_periodic = len(reciprocal_vectors)

        # Create a mapping from state IDs to indices in the Hamiltonian matrix
        # state_id identifies the state, idx is its index in the Hamiltonian
        # matrix (to keep track of rows/columns)
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

            This function constructs the Hamiltonian matrix in k-space
            according to the tight-binding model defined by the `UnitCell`
            and its hopping parameters.
            The matrix elements include phase factors exp(-i k·R) for hoppings
            between different unit cells, as required by Bloch's theorem.

            Parameters
            ----------
            k : NDArray[np.float64]
                k-point vector in the basis of reciprocal lattice vectors
                If the system has n periodic directions, k should be an
                n-dimensional vector

            Returns
            -------
            NDArray[np.float64]
                Complex Hamiltonian matrix of size (n_states, n_states)
            """
            # Validate the k-point dimension matches the number of
            # periodic directions
            if len(k) != num_periodic:
                raise ValueError("Momentum does not match system periodicity")

            # Initialize the Hamiltonian matrix with zeros
            H = np.zeros((n_states, n_states), dtype=np.complex128)

            # Fill the Hamiltonian matrix
            for (dest_id, source_id), hoppings in self.hoppings.items():
                dest_idx = state_to_idx[dest_id]  # Destination state index
                source_idx = state_to_idx[source_id]  # Source state index

                for displacement, amplitude in hoppings:
                    d1, d2, d3 = displacement

                    # Calculate the real-space displacement vector
                    # This is the sum of the periodic vectors scaled by
                    # the displacement
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
