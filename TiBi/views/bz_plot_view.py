import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph.opengl as gl
from TiBi.ui import (
    CF_VERMILLION,
    CF_YELLOW,
    CF_GREEN,
    CF_SKY,
    CF_BLUE,
)


class BrillouinZonePlotView(QWidget):
    """
    A 3D visualization panel for Brillouin Zone using PyQtGraph's OpenGL.

    Displays a Brillouin zone as a wireframe with vertices shown as small
    spheres. The visualization supports rotation and zooming.

    Features:
    - Interactive 3D visualization with mouse rotation and zooming
    - Colored axes representing the Cartesian coordinate system
    - BZ visualization with wireframe boundaries
    - High-symmetry points displayed as colored spheres
    - Selected high-symmetry points highlighted with a different color

    This view is purely presentational and contains no business logic,
    following the MVC pattern. The controller is responsible for updating
    the visualization based on model changes.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)

        # Colors
        self.point_color = CF_BLUE
        self.selected_point_color = CF_YELLOW

        # Setup layout
        layout = QVBoxLayout(self)
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
        for ii, color in enumerate(
            [
                CF_VERMILLION,
                CF_GREEN,
                CF_SKY,
            ]
        ):
            self.view.addItem(
                gl.GLLinePlotItem(
                    pos=axes[ii], color=color, width=5, antialias=True
                )
            )

        layout.addWidget(self.view, stretch=1)
