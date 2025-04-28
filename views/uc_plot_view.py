import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
)
from PySide6.QtCore import Signal, Qt, QSize
import pyqtgraph.opengl as gl

# from itertools import product
from resources.colors import CF_vermillion, CF_yellow, CF_green, CF_sky, CF_blue


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
    - Controls for displaying periodic repetitions of the unit cell

    This view is purely presentational and contains no business logic,
    following the MVC pattern. The controller is responsible for updating
    the visualization based on model changes.
    """

    # Signals for interacting with other components
    site_selected = Signal(object)  # Emits site ID when a site is selected

    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(400, 400))

        # Colors
        self.axis_colors = [
            CF_vermillion,
            CF_green,
            CF_blue,
        ]  # R, G, B for x, y, z
        self.cell_color = (0.8, 0.8, 0.8, 0.3)  # Light gray, semi-transparent
        self.site_color = CF_sky
        self.selected_site_color = CF_yellow

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

        # Settings panel
        self.control_panel = QHBoxLayout()
        # View adjusting panel
        self.lattice_view_control = QVBoxLayout()
        self.lattice_view_control_label = QLabel("Number of unit cells to show")
        self.lattice_view_control_label.setAlignment(Qt.AlignCenter)
        self.lattice_view_control_spinners = QHBoxLayout()

        # Unit cell view number
        self.n1_spinner = QSpinBox()
        self.n2_spinner = QSpinBox()
        self.n3_spinner = QSpinBox()

        for x in [self.n1_spinner, self.n2_spinner, self.n3_spinner]:
            x.setFixedWidth(40)
            x.setRange(1, 10)
            x.setEnabled(False)

        # Create row layouts with labels on the left and spin boxes on the right
        spinner1 = QHBoxLayout()
        spinner1.addWidget(QLabel("n<sub>1</sub>:"))
        spinner1.addWidget(self.n1_spinner)

        spinner2 = QHBoxLayout()
        spinner2.addWidget(QLabel("n<sub>2</sub>:"))
        spinner2.addWidget(self.n2_spinner)

        spinner3 = QHBoxLayout()
        spinner3.addWidget(QLabel("n<sub>3</sub>:"))
        spinner3.addWidget(self.n3_spinner)

        # Add spinners to the main form layout
        self.lattice_view_control_spinners.addLayout(spinner1)
        self.lattice_view_control_spinners.addLayout(spinner2)
        self.lattice_view_control_spinners.addLayout(spinner3)

        self.lattice_view_control.addWidget(self.lattice_view_control_label)
        self.lattice_view_control.addLayout(self.lattice_view_control_spinners)

        # Assemble control panel

        self.control_panel.addLayout(self.lattice_view_control, stretch=1)

        # Assemble the full panel

        layout.addWidget(self.view, stretch=5)
        layout.addLayout(self.control_panel, stretch=1)
