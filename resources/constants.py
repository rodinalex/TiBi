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


# Model initialization values.
def unit_cell_data_init():
    return {
        "unit_cell_name": "",
        "v1x": 1.0,
        "v1y": 0.0,
        "v1z": 0.0,
        "v2x": 0.0,
        "v2y": 1.0,
        "v2z": 0.0,
        "v3x": 0.0,
        "v3y": 0.0,
        "v3z": 1.0,
        "v1periodic": False,
        "v2periodic": False,
        "v3periodic": False,
        "site_name": "",
        "c1": 0.0,
        "c2": 0.0,
        "c3": 0.0,
        "state_name": "",
    }  # Values for the unit cell panel


def selection_init():
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
