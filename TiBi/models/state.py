from dataclasses import dataclass, field
import uuid


@dataclass
class State:
    """
    A quantum state (orbital) within a `Site`.

    Each `State` has a `name` and belongs to a `Site` in the `UnitCell`.
    `State`s are the fundamental entities between which hopping can occur.

    Attributes
    ----------
    name : str
        Name of the `State` (e.g., "s", "px", "py", etc.)
    id : uuid.UUID
        Unique identifier for the `State`
    """

    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
