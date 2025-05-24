from dataclasses import dataclass, field
import uuid

from .state import State


@dataclass
class Site:
    """
    A physical site (like an atom) within a `UnitCell`.

    `Site`s are positioned using fractional coordinates relative to
    the `UnitCell`'s basis vectors. Each `Site` can contain multiple `State`s.
    The position is specified using fractional coordinates within
    the `UnitCell`, where each coordinate ranges from 0 to 1.

    Attributes
    ----------
    name : str
        Name of the `Site` (e.g., atom name like "C", "Fe", etc.)
    c1, c2, c3 : float
        Fractional coordinates (0 ≤ c ≤ 1) along the unit cell's `BasisVector`s
    R : float
        `Site` radius used for plotting (in arbitrary units)
    color : tuple[float, float, float, float]
        `Site` color used for plotting
    states : dict[uuid.UUID, State]
        Dictionary mapping state UUIDs to `State` objects
    id : uuid.UUID
        Unique identifier for the `Site`
    """

    name: str
    c1: float
    c2: float
    c3: float
    R: float
    color: tuple[float, float, float, float]
    states: dict[uuid.UUID, State] = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
