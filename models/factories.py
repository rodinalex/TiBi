import random
from models import BasisVector, State, Site, UnitCell
from ui.constants import DEFAULT_SITE_SIZE


# Model initialization factories.
def bz_point_selection_init():
    return {
        "vertex": None,
        "edge": None,
        "face": None,
    }  # Indices of the selected high-symmetry points in the BZ


def bz_point_lists_init():
    return {
        "vertex": [],
        "edge": [],
        "face": [],
    }  # Lists of the high-symmetry points in the BZ, grouped by type


def mk_new_unit_cell():
    """
    Create a new unit cell with default values.

    Returns
    -------
    UnitCell
        A new `UnitCell` object with default values.
    """
    name = "New Unit Cell"
    v1 = BasisVector(1, 0, 0)  # Unit vector along x-axis
    v2 = BasisVector(0, 1, 0)  # Unit vector along y-axis
    v3 = BasisVector(0, 0, 1)  # Unit vector along z-axis

    return UnitCell(name, v1, v2, v3)


def mk_new_site():
    """
    Create a new site with default values.

    Returns
    -------
    Site
        A new `Site` object with default values.
    """
    name = "New Site"
    c1 = 0  # Fractional coordinate along first basis vector
    c2 = 0  # Fractional coordinate along second basis vector
    c3 = 0  # Fractional coordinate along third basis vector
    R = DEFAULT_SITE_SIZE
    color = (
        random.uniform(0, 1),
        random.uniform(0, 1),
        random.uniform(0, 1),
        1.0,
    )
    return Site(name, c1, c2, c3, R, color)


def mk_new_state():
    """
    Create a new state with default values.

    Returns
    -------
    State
        A new `State` object with default values.
    """
    name = "New State"
    return State(name)
