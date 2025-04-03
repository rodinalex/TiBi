from dataclasses import dataclass, field
import uuid
from typing import Tuple
import numpy as np


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
    hoppings: dict[
        Tuple[uuid.UUID, uuid.UUID], list[Tuple[Tuple[int, int, int], np.complex128]]
    ] = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


def get_states(uc: UnitCell):
    states = []
    state_info = []
    for site_id, site in uc.sites.items():
        for state_id, state in site.states.items():
            states.append(state)
            state_info.append((site.name, state.name, state_id))
    return (states, state_info)
