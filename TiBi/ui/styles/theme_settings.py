# 97E2F7 PRIMARY FOR MATERIAL DESIGN
def darken_rgb(rgb_tuple, factor=0.1):
    """Darken an RGB tuple by a given factor"""
    r, g, b = rgb_tuple
    return (
        int(r * (1 - factor)),
        int(g * (1 - factor)),
        int(b * (1 - factor)),
    )


def lighten_rgb(rgb_tuple, factor=0.1):
    """Lighten an RGB tuple by a given factor"""
    r, g, b = rgb_tuple
    return (
        min(255, int(r + (255 - r) * factor)),
        min(255, int(g + (255 - g) * factor)),
        min(255, int(b + (255 - b) * factor)),
    )


def rgb_to_string(rgb_tuple):
    """Convert RGB tuple to CSS rgb() string"""
    return f"rgb({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]})"


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        [
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        ]
    )


# COLORS
PRIMARY = "#85d2e7"
ON_PRIMARY = "#003640"
PRIMARY_CONTAINER = "#004e5c"
ON_PRIMARY_CONTAINER = "#acecff"

SECONDARY = "#b2cbd2"
ON_SECONDARY = "#1d343a"
SECONDARY_CONTAINER = "#334a51"
ON_SECONDARY_CONTAINER = "#cee7ef"

TERTIARY = "#bfc4eb"
ON_TERTIARY = "#282e4d"
TERTIARY_CONTAINER = "#3f4565"
ON_TERTIARY_CONTAINER = "#dde1ff"

ERROR = "#ffb4ab"
ON_ERROR = "#690005"
ERROR_CONTAINER = "#93000a"
ON_ERROR_CONTAINER = "#ffdad6"

SURFACE = "#0f1416"
ON_SURFACE = "#dee3e5"
SURFACE_CONTAINER = "#1b2022"
ON_SURFACE_VARIANT = "#bfc8cb"

OUTLINE = "#899295"
OUTLINE_VARIANT = "#3f484b"

# THEME
THEME_SETTINGS = {
    "PRIMARY": rgb_to_string(hex_to_rgb(PRIMARY)),
    "PRIMARY_HEX": PRIMARY,
    "ON_PRIMARY": ON_PRIMARY,
    "PRIMARY_CONTAINER": PRIMARY_CONTAINER,
    "ON_PRIMARY_CONTAINER": ON_PRIMARY_CONTAINER,
    #
    "PRIMARY_HOVER": rgb_to_string(darken_rgb(hex_to_rgb(PRIMARY), 0.1)),
    "PRIMARY_PRESSED": rgb_to_string(darken_rgb(hex_to_rgb(PRIMARY), 0.15)),
    ####
    "SECONDARY": SECONDARY,
    "ON_SECONDARY": ON_SECONDARY,
    "SECONDARY_CONTAINER": SECONDARY_CONTAINER,
    "ON_SECONDARY_CONTAINER": ON_SECONDARY_CONTAINER,
    ####
    "TERTIARY": TERTIARY,
    "ON_TERTIARY": ON_TERTIARY,
    "TERTIARY_CONTAINER": TERTIARY_CONTAINER,
    "ON_TERTIARY_CONTAINER": ON_TERTIARY_CONTAINER,
    ####
    "ERROR": ERROR,
    "ON_ERROR": ON_ERROR,
    "ERROR_CONTAINER": ERROR_CONTAINER,
    "ON_ERROR_CONTAINER": ON_ERROR_CONTAINER,
    ####
    "SURFACE": SURFACE,
    "ON_SURFACE": ON_SURFACE,
    "SURFACE_CONTAINER": SURFACE_CONTAINER,
    "ON_SURFACE_VARIANT": ON_SURFACE_VARIANT,
    ####
    "OUTLINE": OUTLINE,
    "OUTLINE_VARIANT": OUTLINE_VARIANT,
}
