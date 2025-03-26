from dataclasses import dataclass, field
import uuid


@dataclass
class BasisVector:
    x: float
    y: float
    z: float


@dataclass
class State:
    name: str
    energy: float
    id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)


@dataclass
class Site:
    name: str
    c1: float
    c2: float
    c3: float
    states: dict[uuid.UUID, State] = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)


@dataclass
class UnitCell:
    name: str
    v1: BasisVector
    v2: BasisVector
    v3: BasisVector
    sites: dict[uuid.UUID, Site] = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
