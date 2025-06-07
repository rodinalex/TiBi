import numpy as np
import pyqtgraph.opengl as gl
from PySide6.QtWidgets import QVBoxLayout, QWidget

from TiBi.ui import CF_VERMILLION, CF_GREEN, CF_SKY


class UnitCellPlotView(QWidget):
    """
    A 3D visualization panel for Unit Cells using PyQtGraph's OpenGL support.

    Displays a unit cell as a wireframe parallelepiped with sites as spheres.
    The visualization supports rotation and zooming.

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

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)

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

        layout.addWidget(self.view)
