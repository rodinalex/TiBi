import random
from models import BasisVector, State, Site, UnitCell

"""
Constants used by the application. These include style options, as well as
model initialization values.
"""

# Colorblind friendly colors introduced in B. Wong, Color blindness,
# Nature Methods 8, 441 (2011).
CF_red = (204 / 255, 121 / 255, 167 / 255, 1.0)
CF_vermillion = (213 / 255, 94 / 255, 0, 1.0)
CF_orange = (230 / 255, 159 / 255, 0, 1.0)
CF_yellow = (240 / 255, 228 / 255, 66 / 255, 1.0)
CF_green = (0, 158 / 255, 115 / 255, 1.0)
CF_sky = (86 / 255, 180 / 255, 233 / 255, 1.0)
CF_blue = (0, 114 / 255, 178 / 255, 1.0)

# Constants for plotting sites in the 3D unit cell plot
default_site_size = 0.1  # Default size of the sphere
default_site_scaling = 1.5  # Default scaling of the sphere for selected sites


# Model initialization factories.
def selection_init():
    """
    Initialize the selection model with default values.

    Returns
    -------
    dict
        A dictionary containing the initial values for the selection model.
    """
    return {
        "unit_cell": None,
        "site": None,
        "state": None,
    }  # Item selection from the tree


def active_band_structure_init():
    return {
        "k_path": None,
        "bands": None,
        "special_points": None,
    }  # Active band structure used for plotting


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
    R = default_site_size
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
