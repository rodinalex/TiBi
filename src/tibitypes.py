from dataclasses import dataclass, field
import uuid
from typing import Tuple
import numpy as np

# from models.uc_models import StateCoupling


@dataclass
class BasisVector:
    x: float
    y: float
    z: float
    is_periodic: bool = False


@dataclass
class State:
    name: str
    energy: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Hopping:
    s1: State
    s2: State
    displacement: Tuple[int, int, int]
    amplitude: np.complex128


@dataclass
class Site:
    name: str
    c1: float
    c2: float
    c3: float
    states: dict[uuid.UUID, State] = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class UnitCell:
    name: str
    v1: BasisVector
    v2: BasisVector
    v3: BasisVector
    sites: dict[uuid.UUID, Site] = field(default_factory=dict)
    # couplings: StateCoupling = field(default_factory=StateCoupling)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


def get_states(uc: UnitCell):
    all_sites = list(uc.sites.values())
    res = []
    for s in all_sites:
        res += list(s.states.values())
    return res
