import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QSpinBox,
    QGridLayout,
)
from PySide6.QtCore import QSize, Qt
import pyqtgraph.opengl as gl
from resources.colors import CF_red, CF_vermillion, CF_yellow, CF_green, CF_sky, CF_blue


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
            CF_blue,
        ]  # R, G, B for x, y, z
        self.point_color = CF_sky
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

        # Selection panel
        self.control_panel = QVBoxLayout()
        self.selection_grid = QGridLayout()
        self.control_panel.addLayout(self.selection_grid)

        selection_form_layout = QFormLayout()
        selection_form_layout.setVerticalSpacing(2)

        # Gamma point controls (Γ - origin of reciprocal space)
        self.add_gamma_btn = QPushButton("Γ")
        gamma_label = QLabel("Brillouin Zone Path")
        gamma_label.setAlignment(Qt.AlignCenter)
        self.selection_grid.addWidget(gamma_label, 0, 0, 1, 3)
        self.selection_grid.addWidget(self.add_gamma_btn, 1, 1)

        # Vertex selection controls
        self.prev_vertex_btn = QPushButton("←")
        self.next_vertex_btn = QPushButton("→")
        self.add_vertex_btn = QPushButton("V")
        self.selection_grid.addWidget(self.prev_vertex_btn, 2, 0)
        self.selection_grid.addWidget(self.add_vertex_btn, 2, 1)
        self.selection_grid.addWidget(self.next_vertex_btn, 2, 2)

        # Edge midpoint selection controls
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("E")
        self.selection_grid.addWidget(self.prev_edge_btn, 3, 0)
        self.selection_grid.addWidget(self.add_edge_btn, 3, 1)
        self.selection_grid.addWidget(self.next_edge_btn, 3, 2)

        # Face center selection controls
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("F")
        self.selection_grid.addWidget(self.prev_face_btn, 4, 0)
        self.selection_grid.addWidget(self.add_face_btn, 4, 1)
        self.selection_grid.addWidget(self.next_face_btn, 4, 2)

        self.selection_grid.setVerticalSpacing(2)
        self.selection_grid.setHorizontalSpacing(2)

        # Path controls
        remove_clear_layout = QHBoxLayout()
        self.control_panel.addLayout(remove_clear_layout)

        computation_control_layout = QHBoxLayout()
        self.control_panel.addLayout(computation_control_layout)

        self.remove_last_btn = QPushButton("Undo")
        self.remove_last_btn.setEnabled(False)  # Disabled until path has points

        self.clear_path_btn = QPushButton("Clear")
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        remove_clear_layout.addWidget(self.remove_last_btn)
        remove_clear_layout.addWidget(self.clear_path_btn)
        # Calculation controls
        self.n_points_spinbox = QSpinBox()
        self.n_points_spinbox.setRange(1, 10000)
        self.n_points_spinbox.setValue(100)
        self.n_points_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        self.compute_bands_btn = QPushButton("Compute")
        self.compute_bands_btn.setEnabled(
            False
        )  # Disabled until path has at least two points

        computation_control_layout.addWidget(QLabel("K Points:"))
        computation_control_layout.addWidget(self.n_points_spinbox)
        # computation_control_layout.addWidget(self.compute_bands_btn)

        # Initially disable all selection buttons
        btns = [
            self.add_gamma_btn,
            self.prev_vertex_btn,
            self.next_vertex_btn,
            self.add_vertex_btn,
            self.prev_edge_btn,
            self.next_edge_btn,
            self.add_edge_btn,
            self.prev_face_btn,
            self.next_face_btn,
            self.add_face_btn,
        ]
        for btn in btns:
            btn.setEnabled(False)

        # Group buttons by type for easier controller access
        self.vertex_btns = [
            self.prev_vertex_btn,
            self.next_vertex_btn,
            self.add_vertex_btn,
        ]
        self.edge_btns = [self.prev_edge_btn, self.next_edge_btn, self.add_edge_btn]
        self.face_btns = [self.prev_face_btn, self.next_face_btn, self.add_face_btn]
        self.control_panel.addWidget(self.compute_bands_btn)
        self.control_panel.setSpacing(3)

        # Assemble the full layout
        layout.addWidget(self.view, stretch=2)
        layout.addLayout(self.control_panel, stretch=1)
