import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QSpinBox,
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
    """

    def __init__(self):
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
        self.view.setCameraPosition(distance=20)
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
        self.button_panel = QVBoxLayout()
        self.button_panel_label = QLabel("Create a BZ Path")
        self.button_panel_label.setAlignment(Qt.AlignCenter)

        selection_form_layout = QFormLayout()
        selection_form_layout.setVerticalSpacing(2)

        gamma_pick_layout = QHBoxLayout()
        self.add_gamma_btn = QPushButton("+")
        gamma_pick_layout.addWidget(self.add_gamma_btn)

        #     self.add_gamma_btn.clicked.connect(lambda: self._add_point("gamma"))

        vertex_pick_layout = QHBoxLayout()
        self.prev_vertex_btn = QPushButton("←")
        self.next_vertex_btn = QPushButton("→")
        self.add_vertex_btn = QPushButton("+")
        vertex_pick_layout.addWidget(self.prev_vertex_btn)
        vertex_pick_layout.addWidget(self.next_vertex_btn)
        vertex_pick_layout.addWidget(self.add_vertex_btn)

        edge_pick_layout = QHBoxLayout()
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("+")
        edge_pick_layout.addWidget(self.prev_edge_btn)
        edge_pick_layout.addWidget(self.next_edge_btn)
        edge_pick_layout.addWidget(self.add_edge_btn)

        face_pick_layout = QHBoxLayout()
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("+")
        face_pick_layout.addWidget(self.prev_face_btn)
        face_pick_layout.addWidget(self.next_face_btn)
        face_pick_layout.addWidget(self.add_face_btn)

        # Control buttons
        controls_layout = QVBoxLayout()
        path_controls_layout = QHBoxLayout()  # Holds "Remove Last" and "Clear" buttons
        computation_controls_layout = (
            QHBoxLayout()
        )  # Holds "Number of Points" field and "Compute Bands" button

        self.remove_last_btn = QPushButton("Remove Last")
        self.remove_last_btn.setEnabled(False)  # Disabled until path has points

        self.clear_path_btn = QPushButton("Clear")
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        self.n_points_spinbox = QSpinBox()
        self.n_points_spinbox.setRange(1, 1000000)
        self.n_points_spinbox.setValue(100)
        self.compute_bands_btn = QPushButton("Compute")
        self.compute_bands_btn.setEnabled(
            False
        )  # Disabled unitl path has at least two points

        path_controls_layout.addWidget(self.remove_last_btn)
        path_controls_layout.addWidget(self.clear_path_btn)

        computation_controls_layout.addWidget(QLabel("Points:"))
        computation_controls_layout.addWidget(self.n_points_spinbox)
        computation_controls_layout.addWidget(self.compute_bands_btn)

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

        self.vertex_btns = [
            self.prev_vertex_btn,
            self.next_vertex_btn,
            self.add_vertex_btn,
        ]
        self.edge_btns = [self.prev_edge_btn, self.next_edge_btn, self.add_edge_btn]
        self.face_btns = [self.prev_face_btn, self.next_face_btn, self.add_face_btn]

        # Assemble the point-addition panel
        selection_form_layout.addRow("Γ:", gamma_pick_layout)
        selection_form_layout.addRow("Vertex:", vertex_pick_layout)
        selection_form_layout.addRow("Edge:", edge_pick_layout)
        selection_form_layout.addRow("Face:", face_pick_layout)

        # Add controls to the layout
        controls_layout.addLayout(path_controls_layout)
        controls_layout.addLayout(computation_controls_layout)

        # Assemble buttons panel
        self.button_panel.addWidget(self.button_panel_label)
        self.button_panel.addLayout(selection_form_layout)
        self.button_panel.addLayout(controls_layout)
        self.button_panel.setSpacing(2)
        # Assemble the full layout
        layout.addWidget(self.view, stretch=3)
        layout.addLayout(self.button_panel, stretch=2)
