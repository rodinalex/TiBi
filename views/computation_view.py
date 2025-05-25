from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QSizePolicy,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QSpinBox,
    QGridLayout,
    QButtonGroup,
    QRadioButton,
)
from resources.ui_elements import CheckableComboBox, divider_line
from views.placeholder import PlaceholderWidget

from .panels import HoppingPanel


class BandsView(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.bands_selection_grid = QGridLayout()
        self.proj_layout = QVBoxLayout()
        layout.addLayout(self.bands_selection_grid, stretch=1)
        layout.addWidget(divider_line())
        layout.addLayout(self.proj_layout)
        layout.addWidget(divider_line())
        layout.addWidget(PlaceholderWidget("DOS"), stretch=1)

        # Bands Panel
        self.bands_selection_grid.setContentsMargins(10, 5, 15, 5)
        path_label = QLabel("Brillouin Zone Path")
        path_label.setAlignment(
            Qt.AlignCenter
        )  # This centers the text within the label
        self.bands_selection_grid.addWidget(path_label, 0, 0, 1, 5)
        # Gamma point controls (Γ - origin of reciprocal space)
        self.add_gamma_btn = QPushButton("Γ")
        self.bands_selection_grid.addWidget(self.add_gamma_btn, 1, 1)

        # Vertex selection controls
        self.prev_vertex_btn = QPushButton("←")
        self.next_vertex_btn = QPushButton("→")
        self.add_vertex_btn = QPushButton("V")
        self.bands_selection_grid.addWidget(self.next_vertex_btn, 2, 2)
        self.bands_selection_grid.addWidget(self.add_vertex_btn, 2, 1)
        self.bands_selection_grid.addWidget(self.prev_vertex_btn, 2, 0)

        # Edge midpoint selection controls
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("E")
        self.bands_selection_grid.addWidget(self.next_edge_btn, 3, 2)
        self.bands_selection_grid.addWidget(self.add_edge_btn, 3, 1)
        self.bands_selection_grid.addWidget(self.prev_edge_btn, 3, 0)

        # Face center selection controls
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("F")
        self.bands_selection_grid.addWidget(self.next_face_btn, 4, 2)
        self.bands_selection_grid.addWidget(self.add_face_btn, 4, 1)
        self.bands_selection_grid.addWidget(self.prev_face_btn, 4, 0)

        # Path controls
        self.remove_last_btn = QPushButton("Remove Last")
        self.clear_path_btn = QPushButton("Clear Path")

        kpoints_layout = QHBoxLayout()
        self.n_points_spinbox = QSpinBox()
        self.n_points_spinbox.setRange(1, 10000)
        self.n_points_spinbox.setValue(100)
        self.n_points_spinbox.setButtonSymbols(QSpinBox.NoButtons)

        self.compute_bands_btn = QPushButton("Compute")
        self.compute_bands_btn.setEnabled(
            False
        )  # Disabled until path has at least two points

        self.bands_selection_grid.addWidget(self.remove_last_btn, 1, 4)
        self.remove_last_btn.setEnabled(
            False
        )  # Disabled until path has points

        self.bands_selection_grid.addWidget(self.clear_path_btn, 2, 4)
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        kpoints_layout.addWidget(QLabel("k points:"))
        kpoints_layout.addWidget(self.n_points_spinbox)
        self.bands_selection_grid.addLayout(kpoints_layout, 3, 4)

        self.bands_selection_grid.addWidget(self.compute_bands_btn, 4, 4)

        self.bands_selection_grid.setVerticalSpacing(2)
        self.bands_selection_grid.setHorizontalSpacing(2)

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
        self.edge_btns = [
            self.prev_edge_btn,
            self.next_edge_btn,
            self.add_edge_btn,
        ]
        self.face_btns = [
            self.prev_face_btn,
            self.next_face_btn,
            self.add_face_btn,
        ]

        # Projection panel
        projection_label = QLabel("State Projection")
        projection_label.setAlignment(Qt.AlignCenter)
        projection_tools = QHBoxLayout()

        self.proj_layout.setContentsMargins(10, 5, 15, 5)

        self.proj_layout.addWidget(projection_label)
        self.proj_layout.addLayout(projection_tools)

        self.proj_combo = CheckableComboBox()
        self.project_btn = QPushButton("Project")
        self.select_all_btn = QPushButton("All")
        self.clear_all_btn = QPushButton("None")

        proj_left = QVBoxLayout()
        proj_right = QVBoxLayout()
        proj_buttons = QHBoxLayout()

        projection_tools.addLayout(proj_left, stretch=3)
        projection_tools.addLayout(proj_right, stretch=1)

        proj_left.addWidget(self.proj_combo)
        proj_left.addLayout(proj_buttons)

        proj_buttons.addWidget(self.select_all_btn)
        proj_buttons.addWidget(self.clear_all_btn)

        self.bands_radio = QRadioButton("Bands")
        self.dos_radio = QRadioButton("DOS")

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.bands_radio, id=0)
        self.radio_group.addButton(self.dos_radio, id=1)

        proj_right.addWidget(self.bands_radio)
        proj_right.addWidget(self.dos_radio)

        # DOS Panel


class DOSView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins to maximize space

        layout.addWidget(PlaceholderWidget("DOS"))


class TopologyView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins to maximize space

        layout.addWidget(PlaceholderWidget("TOPOLOGY"))


class ComputationView(QWidget):
    """ """

    def __init__(self):
        """ """
        super().__init__()

        # Create a layout for the TabView itself
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins to maximize space
        self.hopping_panel = HoppingPanel()
        self.bands_panel = BandsView()
        self.dos_panel = DOSView()
        self.topology_panel = TopologyView()
        # Create main tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.hopping_panel, "Hopping")
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
