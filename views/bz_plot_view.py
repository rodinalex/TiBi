import numpy as np
from PySide6.QtWidgets import QWidget, QHBoxLayout

from PySide6.QtCore import QSize
import pyqtgraph.opengl as gl
from resources.colors import CF_vermillion, CF_yellow, CF_green, CF_sky, CF_blue


class BrillouinZonePlotView(QWidget):
    """
    A 3D visualization panel for Brillouin Zone using PyQtGraph's OpenGL support.

    Displays a Brillouin zone as a wireframe with vertices shown as small spheres.
    The visualization supports rotation and zooming. The coordinate system shows
    the reciprocal space axes.

    This view provides UI components for selecting points in the Brillouin zone
    and creating a path for band structure calculations. The actual logic for
    handling selections and path construction is implemented in the
    BrillouinZonePlotController.
    """

    def __init__(self):
        """
        Initialize the Brillouin zone plot view.

        Sets up the 3D visualization area and control panels for selecting
        points in the Brillouin zone and creating paths. The buttons are
        initially disabled and will be enabled by the controller based on
        the dimensionality of the selected unit cell.
        """
        super().__init__()
        self.setMinimumSize(QSize(300, 200))

        # Colors
        self.axis_colors = [
            CF_vermillion,
            CF_green,
            CF_sky,
        ]  # R, G, B for x, y, z
        self.point_color = CF_blue
        self.selected_point_color = CF_yellow

        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create 3D plot widget
        self.view = gl.GLViewWidget()
        # Set almost-orthographic projection
        self.view.opts["distance"] = 2000
        self.view.opts["fov"] = 1  # In degrees
        self.view.setBackgroundColor("k")  # Black background

        # Axes
        axis_limit = 10
        axes = [
            np.array([[-axis_limit, 0, 0], [axis_limit, 0, 0]]),
            np.array([[0, -axis_limit, 0], [0, axis_limit, 0]]),
            np.array([[0, 0, -axis_limit], [0, 0, axis_limit]]),
        ]
        for ii, color in enumerate(self.axis_colors):
            self.view.addItem(
                gl.GLLinePlotItem(pos=axes[ii], color=color, width=5, antialias=True)
            )

        layout.addWidget(self.view, stretch=1)
