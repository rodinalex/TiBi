import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Signal, QSize
import pyqtgraph.opengl as gl

# from itertools import product
from resources.colors import CF_vermillion, CF_green, CF_sky


class UnitCellPlotView(QWidget):
    """
    A 3D visualization panel for Unit Cells using PyQtGraph's OpenGL support.

    Displays a unit cell as a wireframe parallelepiped with sites (atoms) as spheres.
    The visualization supports rotation, zooming, and site selection. The coordinate
    system shows the unit cell basis vectors and a reference grid.

    Features:
    - Interactive 3D visualization with mouse rotation and zooming
    - Colored axes representing the Cartesian coordinate system
    - Unit cell visualization with wireframe parallelepiped
    - Sites displayed as colored spheres at their fractional positions
    - Selected sites highlighted with an increased size

    This view is purely presentational and contains no business logic,
    following the MVC pattern. The controller is responsible for updating
    the visualization based on model changes.
    """

    # Signals for interacting with other components
    site_selected = Signal(object)  # Emits site ID when a site is selected

    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(350, 350))

        # Colors
        self.axis_colors = [
            CF_vermillion,
            CF_green,
            CF_sky,
        ]  # R, G, B for x, y, z
        self.cell_color = (0.8, 0.8, 0.8, 0.3)  # Light gray, semi-transparent

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
        for ii, color in enumerate(self.axis_colors):
            self.view.addItem(
                gl.GLLinePlotItem(pos=axes[ii], color=color, width=5, antialias=True)
            )

        layout.addWidget(self.view)
