# import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QSizePolicy,
    QVBoxLayout,
    QLabel,
    # QHBoxLayout,
    # QVBoxLayout,
    # QFormLayout,
    QPushButton,
    QSpinBox,
    QGridLayout,
)
from PySide6.QtCore import Qt
from resources.ui_elements import divider_line
from views.placeholder import PlaceholderWidget


class BandsView(QWidget):
    def __init__(self):
        super().__init__()

        # Selection panel
        layout = QVBoxLayout(self)
        self.selection_grid = QGridLayout()
        layout.addLayout(self.selection_grid, stretch=1)
        layout.addWidget(divider_line())
        layout.addWidget(PlaceholderWidget("BAND PROJECTION"), stretch=1)
        layout.addWidget(divider_line())
        layout.addWidget(PlaceholderWidget("SPOT"), stretch=1)

        # selection_form_layout = QFormLayout()
        # selection_form_layout.setVerticalSpacing(2)

        # Gamma point controls (Γ - origin of reciprocal space)
        self.add_gamma_btn = QPushButton("Γ")
        gamma_label = QLabel("Brillouin Zone Path")
        gamma_label.setAlignment(Qt.AlignCenter)
        self.selection_grid.addWidget(gamma_label, 0, 0, 1, 6)
        self.selection_grid.addWidget(self.add_gamma_btn, 2, 1)

        # Vertex selection controls
        self.prev_vertex_btn = QPushButton("↓")
        self.next_vertex_btn = QPushButton("↑")
        self.add_vertex_btn = QPushButton("V")
        self.selection_grid.addWidget(self.next_vertex_btn, 1, 2)
        self.selection_grid.addWidget(self.add_vertex_btn, 2, 2)
        self.selection_grid.addWidget(self.prev_vertex_btn, 3, 2)

        # Edge midpoint selection controls
        self.prev_edge_btn = QPushButton("↓")
        self.next_edge_btn = QPushButton("↑")
        self.add_edge_btn = QPushButton("E")
        self.selection_grid.addWidget(self.next_edge_btn, 1, 3)
        self.selection_grid.addWidget(self.add_edge_btn, 2, 3)
        self.selection_grid.addWidget(self.prev_edge_btn, 3, 3)

        # Face center selection controls
        self.prev_face_btn = QPushButton("↓")
        self.next_face_btn = QPushButton("↑")
        self.add_face_btn = QPushButton("F")
        self.selection_grid.addWidget(self.next_face_btn, 1, 4)
        self.selection_grid.addWidget(self.add_face_btn, 2, 4)
        self.selection_grid.addWidget(self.prev_face_btn, 3, 4)

        # Path controls
        self.remove_last_btn = QPushButton("Undo")
        self.clear_path_btn = QPushButton("Clear")

        self.n_points_spinbox = QSpinBox()
        self.n_points_spinbox.setRange(1, 10000)
        self.n_points_spinbox.setValue(100)
        self.n_points_spinbox.setButtonSymbols(QSpinBox.NoButtons)

        self.compute_bands_btn = QPushButton("Compute bands")
        self.compute_bands_btn.setEnabled(
            False
        )  # Disabled until path has at least two points

        self.selection_grid.addWidget(self.remove_last_btn, 1, 6)
        self.remove_last_btn.setEnabled(False)  # Disabled until path has points

        self.selection_grid.addWidget(self.clear_path_btn, 1, 7)
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        self.selection_grid.addWidget(QLabel("K Points:"), 2, 6)
        self.selection_grid.addWidget(self.n_points_spinbox, 2, 7)

        self.selection_grid.addWidget(self.compute_bands_btn, 3, 6, 1, 2)

        self.selection_grid.setVerticalSpacing(2)
        self.selection_grid.setHorizontalSpacing(2)

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

        # self.control_panel.addWidget(self.compute_bands_btn)
        # self.control_panel.setSpacing(3)
        # layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space

        # layout.addWidget(PlaceholderWidget("BANDS"))


class DOSView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space

        layout.addWidget(PlaceholderWidget("DOS"))


class TopologyView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space

        layout.addWidget(PlaceholderWidget("TOPOLOGY"))


class ComputationView(QWidget):
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

        # Create a layout for the TabView itself
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space
        self.bands_panel = BandsView()
        self.dos_panel = DOSView()
        self.topology_panel = TopologyView()
        # Create main tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.bands_panel, "Bands")
        self.tabs.addTab(self.dos_panel, "DOS")
        self.tabs.addTab(self.topology_panel, "Topology")
        self.tabs.setTabPosition(QTabWidget.East)
        self.tabs.setDocumentMode(True)
        # Set size policy to make the tab widget expand
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the tab widget to the layout
        layout.addWidget(self.tabs)

        # Set the layout for this widget
        self.setLayout(layout)

        # Ensure the TabView itself expands properly
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setMinimumSize(QSize(300, 200))

        # # Colors
        # self.axis_colors = [
        #     CF_vermillion,
        #     CF_green,
        #     CF_sky,
        # ]  # R, G, B for x, y, z
        # self.point_color = CF_blue
        # self.selected_point_color = CF_yellow

        # # Setup layout
        # layout = QHBoxLayout(self)
        # layout.setContentsMargins(0, 0, 0, 0)

        # # Create 3D plot widget
        # self.view = gl.GLViewWidget()
        # # Set almost-orthographic projection
        # self.view.opts["distance"] = 2000
        # self.view.opts["fov"] = 1  # In degrees
        # self.view.setBackgroundColor("k")  # Black background

        # # Axes
        # axis_limit = 10
        # axes = [
        #     np.array([[-axis_limit, 0, 0], [axis_limit, 0, 0]]),
        #     np.array([[0, -axis_limit, 0], [0, axis_limit, 0]]),
        #     np.array([[0, 0, -axis_limit], [0, 0, axis_limit]]),
        # ]
        # for ii, color in enumerate(self.axis_colors):
        #     self.view.addItem(
        #         gl.GLLinePlotItem(pos=axes[ii], color=color, width=5, antialias=True)
        #     )

        # # Selection panel
        # self.control_panel = QVBoxLayout()
        # self.selection_grid = QGridLayout()
        # self.control_panel.addLayout(self.selection_grid)

        # selection_form_layout = QFormLayout()
        # selection_form_layout.setVerticalSpacing(2)

        # # Gamma point controls (Γ - origin of reciprocal space)
        # self.add_gamma_btn = QPushButton("Γ")
        # gamma_label = QLabel("Brillouin Zone Path")
        # gamma_label.setAlignment(Qt.AlignCenter)
        # self.selection_grid.addWidget(gamma_label, 0, 0, 1, 3)
        # self.selection_grid.addWidget(self.add_gamma_btn, 1, 1)

        # # Vertex selection controls
        # self.prev_vertex_btn = QPushButton("←")
        # self.next_vertex_btn = QPushButton("→")
        # self.add_vertex_btn = QPushButton("V")
        # self.selection_grid.addWidget(self.prev_vertex_btn, 2, 0)
        # self.selection_grid.addWidget(self.add_vertex_btn, 2, 1)
        # self.selection_grid.addWidget(self.next_vertex_btn, 2, 2)

        # # Edge midpoint selection controls
        # self.prev_edge_btn = QPushButton("←")
        # self.next_edge_btn = QPushButton("→")
        # self.add_edge_btn = QPushButton("E")
        # self.selection_grid.addWidget(self.prev_edge_btn, 3, 0)
        # self.selection_grid.addWidget(self.add_edge_btn, 3, 1)
        # self.selection_grid.addWidget(self.next_edge_btn, 3, 2)

        # # Face center selection controls
        # self.prev_face_btn = QPushButton("←")
        # self.next_face_btn = QPushButton("→")
        # self.add_face_btn = QPushButton("F")
        # self.selection_grid.addWidget(self.prev_face_btn, 4, 0)
        # self.selection_grid.addWidget(self.add_face_btn, 4, 1)
        # self.selection_grid.addWidget(self.next_face_btn, 4, 2)

        # self.selection_grid.setVerticalSpacing(2)
        # self.selection_grid.setHorizontalSpacing(2)

        # # Path controls
        # remove_clear_layout = QHBoxLayout()
        # self.control_panel.addLayout(remove_clear_layout)

        # computation_control_layout = QHBoxLayout()
        # self.control_panel.addLayout(computation_control_layout)

        # self.remove_last_btn = QPushButton("Undo")
        # self.remove_last_btn.setEnabled(False)  # Disabled until path has points

        # self.clear_path_btn = QPushButton("Clear")
        # self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        # remove_clear_layout.addWidget(self.remove_last_btn)
        # remove_clear_layout.addWidget(self.clear_path_btn)
        # # Calculation controls
        # self.n_points_spinbox = QSpinBox()
        # self.n_points_spinbox.setRange(1, 10000)
        # self.n_points_spinbox.setValue(100)
        # self.n_points_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        # self.compute_bands_btn = QPushButton("Compute")
        # self.compute_bands_btn.setEnabled(
        #     False
        # )  # Disabled until path has at least two points

        # computation_control_layout.addWidget(QLabel("K Points:"))
        # computation_control_layout.addWidget(self.n_points_spinbox)
        # # computation_control_layout.addWidget(self.compute_bands_btn)

        # # Initially disable all selection buttons
        # btns = [
        #     self.add_gamma_btn,
        #     self.prev_vertex_btn,
        #     self.next_vertex_btn,
        #     self.add_vertex_btn,
        #     self.prev_edge_btn,
        #     self.next_edge_btn,
        #     self.add_edge_btn,
        #     self.prev_face_btn,
        #     self.next_face_btn,
        #     self.add_face_btn,
        # ]
        # for btn in btns:
        #     btn.setEnabled(False)

        # # Group buttons by type for easier controller access
        # self.vertex_btns = [
        #     self.prev_vertex_btn,
        #     self.next_vertex_btn,
        #     self.add_vertex_btn,
        # ]
        # self.edge_btns = [self.prev_edge_btn, self.next_edge_btn, self.add_edge_btn]
        # self.face_btns = [self.prev_face_btn, self.next_face_btn, self.add_face_btn]
        # self.control_panel.addWidget(self.compute_bands_btn)
        # self.control_panel.setSpacing(3)

        # # Assemble the full layout
        # layout.addWidget(self.view, stretch=2)
        # layout.addLayout(self.control_panel, stretch=1)
