from dataclasses import dataclass, field
import uuid
from typing import Tuple
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
    """

    x: float  # x-component in Cartesian coordinates
    y: float  # y-component in Cartesian coordinates
    z: float  # z-component in Cartesian coordinates
    is_periodic: bool = False  # Whether the crystal repeats in this direction

    def as_array(self) -> np.ndarray:
        """Return the vector as a NumPy array."""
        return np.array([self.x, self.y, self.z])

    def dot(self, other: "BasisVector") -> float:
        """Return the dot product with another basis vector."""
        return float(np.dot(self.as_array(), other.as_array()))

    def cross(self, other: "BasisVector") -> "BasisVector":
        """Return the cross product with another basis vector as a new BasisVector."""
        result = np.cross(self.as_array(), other.as_array())
        return BasisVector(*result)


@dataclass
class State:
    """
    Represents a quantum state (like an orbital) within a site.

    Each state has an energy and belongs to a specific site in the unit cell.
    States are the fundamental entities between which hopping can occur.
    """

    name: str  # Name of the state (e.g., "s", "px", "py", etc.)
    id: uuid.UUID = field(default_factory=uuid.uuid4)  # Unique identifier


@dataclass
class Site:
    """
    Represents a physical site (like an atom) within a unit cell.

    Sites are positioned using fractional coordinates relative to the unit cell's
    basis vectors. Each site can contain multiple quantum states (orbitals).
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
    - Keys are pairs of state UUIDs (source, destination)
    - Values are lists of (displacement, amplitude) pairs where:
      - displacement is a tuple of three integers (n1,n2,n3) indicating which periodic
        image of the unit cell is involved (0,0,0 means within the same unit cell)
      - amplitude is a complex number representing the hopping strength and phase
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
    id: uuid.UUID = field(default_factory=uuid.uuid4)  # Unique identifier

    def volume(self) -> float:
        """Compute the volume of the unit cell using the scalar triple product."""
        return np.dot(self.v1, np.cross(self.v2, self.v3))

    def reciprocal_vectors(self) -> list[np.ndarray]:
        """
        Compute the reciprocal lattice vectors corresponding to the periodic directions
        in the unit cell. Returns a list of 3D reciprocal vectors (0 to 3 items).
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

        Args:
            scale: A float to scale the vectors for integer reduction (default: 1e6)

        Returns:
            A list of BasisVector objects representing the reduced basis.
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
        Extracts all states from a unit cell along with their identifying information.

        This is a helper function used by UI components to get a flattened list of all
        states in the unit cell, regardless of which site they belong to.

        Args:
            self: The unit cell to extract states from

        Returns:
            A tuple of (states, state_info) where:
            - states is a list of State objects
            - state_info is a list of tuples (site_name, state_name, state_id) that
            provides a more displayable form of the state information
        """
        states = []
        state_info = []
        for site_id, site in self.sites.items():
            for state_id, state in site.states.items():
                states.append(state)
                state_info.append((site.name, state.name, state_id))
        return (states, state_info)

    def get_BZ(self):

        n_neighbors = 1
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
