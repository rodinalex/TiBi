# import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QSizePolicy,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    # QVBoxLayout,
    # QFormLayout,
    QPushButton,
    QSpinBox,
    QGridLayout,
)
from PySide6.QtCore import Qt
from resources.ui_elements import CheckableComboBox, divider_line
from views.placeholder import PlaceholderWidget


class BandsView(QWidget):
    def __init__(self):
        super().__init__()

        # Selection panel
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.selection_grid = QGridLayout()
        layout.addLayout(self.selection_grid, stretch=1)
        layout.addWidget(divider_line())
        layout.addWidget(PlaceholderWidget("BAND PROJECTION"), stretch=1)
        layout.addWidget(divider_line())
        self.projection_box = CheckableComboBox()
        layout.addWidget(self.projection_box)
        # layout.addWidget(PlaceholderWidget("SPOT"), stretch=1)

        # selection_form_layout = QFormLayout()
        # selection_form_layout.setVerticalSpacing(2)

        path_label = QLabel("Brillouin Zone Path")
        path_label.setAlignment(
            Qt.AlignCenter
        )  # This centers the text within the label
        self.selection_grid.addWidget(path_label, 0, 1, 1, 6)
        # Gamma point controls (Γ - origin of reciprocal space)
        self.add_gamma_btn = QPushButton("Γ")
        self.selection_grid.addWidget(self.add_gamma_btn, 1, 3)

        # Vertex selection controls
        self.prev_vertex_btn = QPushButton("←")
        self.next_vertex_btn = QPushButton("→")
        self.add_vertex_btn = QPushButton("V")
        self.selection_grid.addWidget(self.next_vertex_btn, 2, 4)
        self.selection_grid.addWidget(self.add_vertex_btn, 2, 3)
        self.selection_grid.addWidget(self.prev_vertex_btn, 2, 2)

        # Edge midpoint selection controls
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("E")
        self.selection_grid.addWidget(self.next_edge_btn, 3, 4)
        self.selection_grid.addWidget(self.add_edge_btn, 3, 3)
        self.selection_grid.addWidget(self.prev_edge_btn, 3, 2)

        # Face center selection controls
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("F")
        self.selection_grid.addWidget(self.next_face_btn, 4, 4)
        self.selection_grid.addWidget(self.add_face_btn, 4, 3)
        self.selection_grid.addWidget(self.prev_face_btn, 4, 2)

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

        self.selection_grid.addWidget(self.remove_last_btn, 1, 6)
        self.remove_last_btn.setEnabled(
            False
        )  # Disabled until path has points

        self.selection_grid.addWidget(self.clear_path_btn, 2, 6)
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        kpoints_layout.addWidget(QLabel("k points:"))
        kpoints_layout.addWidget(self.n_points_spinbox)
        self.selection_grid.addLayout(kpoints_layout, 3, 6)

        self.selection_grid.addWidget(self.compute_bands_btn, 4, 6, 1, 1)

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

        # self.control_panel.addWidget(self.compute_bands_btn)
        # self.control_panel.setSpacing(3)
        # layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space

        # layout.addWidget(PlaceholderWidget("BANDS"))


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
        self.bands_panel = BandsView()
        self.dos_panel = DOSView()
        self.topology_panel = TopologyView()
        # Create main tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.bands_panel, "Bands")
        self.tabs.addTab(self.dos_panel, "DOS")
        self.tabs.addTab(self.topology_panel, "Topology")
        self.tabs.setTabPosition(QTabWidget.North)
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
