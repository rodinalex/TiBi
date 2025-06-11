from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from TiBi.ui.utilities import divider_line, set_spinbox_digit_width
from ..widgets import CheckableComboBox, EnterKeySpinBox, EnterKeyIntSpinBox


class BandsPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.bands_grid = QGridLayout()
        self.proj_layout = QVBoxLayout()
        self.dos_layout = QVBoxLayout()
        layout.addLayout(self.bands_grid, stretch=1)
        layout.addWidget(divider_line())
        layout.addLayout(self.proj_layout)
        layout.addWidget(divider_line())
        layout.addLayout(self.dos_layout, stretch=1)

        # Bands Section
        self.bands_grid.setContentsMargins(10, 5, 15, 5)
        path_label = QLabel("Brillouin Zone Path")
        path_label.setProperty("style", "bold")
        path_label.setAlignment(
            Qt.AlignCenter
        )  # This centers the text within the label
        self.bands_grid.addWidget(path_label, 0, 0, 1, 5)
        # Gamma point controls (Γ - origin of reciprocal space)
        self.add_gamma_btn = QPushButton("Γ")
        self.bands_grid.addWidget(self.add_gamma_btn, 1, 1)
        # Vertex selection controls
        self.prev_vertex_btn = QPushButton("←")
        self.next_vertex_btn = QPushButton("→")
        self.add_vertex_btn = QPushButton("V")
        self.bands_grid.addWidget(self.next_vertex_btn, 2, 2)
        self.bands_grid.addWidget(self.add_vertex_btn, 2, 1)
        self.bands_grid.addWidget(self.prev_vertex_btn, 2, 0)

        # Edge midpoint selection controls
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("E")
        self.bands_grid.addWidget(self.next_edge_btn, 3, 2)
        self.bands_grid.addWidget(self.add_edge_btn, 3, 1)
        self.bands_grid.addWidget(self.prev_edge_btn, 3, 0)

        # Face center selection controls
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("F")
        self.bands_grid.addWidget(self.next_face_btn, 4, 2)
        self.bands_grid.addWidget(self.add_face_btn, 4, 1)
        self.bands_grid.addWidget(self.prev_face_btn, 4, 0)

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

        self.bands_grid.addWidget(self.remove_last_btn, 1, 4)
        self.remove_last_btn.setEnabled(
            False
        )  # Disabled until path has points

        self.bands_grid.addWidget(self.clear_path_btn, 2, 4)
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        kpoints_layout.addWidget(QLabel("k points:"))
        kpoints_layout.addWidget(self.n_points_spinbox)
        self.bands_grid.addLayout(kpoints_layout, 3, 4)

        self.bands_grid.addWidget(self.compute_bands_btn, 4, 4)

        self.bands_grid.setVerticalSpacing(2)
        self.bands_grid.setHorizontalSpacing(2)

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

        for row in range(5):  # Rows 0 to 4 in bands_grid
            self.bands_grid.setRowMinimumHeight(row, 25)
            # self.bands_grid.setRowStretch(row, 1)  # Ensure equal stretching

        # Approximate output size label
        self.approximate_band_size = QLabel("Approximate output size: 0 kB")
        self.bands_grid.addWidget(self.approximate_band_size, 5, 0, 1, 5)

        # Projection panel
        projection_label = QLabel("State Projection")
        projection_label.setProperty("style", "bold")
        projection_label.setAlignment(Qt.AlignCenter)
        projection_tools = QHBoxLayout()

        self.proj_layout.setContentsMargins(10, 5, 15, 5)

        self.proj_layout.addWidget(projection_label)
        self.proj_layout.addLayout(projection_tools)

        self.proj_combo = CheckableComboBox()
        self.project_btn = QPushButton("Project")
        self.select_all_btn = QPushButton("All")
        self.clear_all_btn = QPushButton("None")
        self.select_all_btn.setEnabled(False)
        self.clear_all_btn.setEnabled(False)

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
        self.bands_radio.setChecked(True)

        proj_right.addWidget(self.bands_radio)
        proj_right.addWidget(self.dos_radio)

        # DOS Section
        self.bz_grid = QGridLayout()
        self.dos_visualization_grid = QGridLayout()
        self.dos_layout.addLayout(self.bz_grid)
        self.dos_layout.addWidget(divider_line())
        self.dos_layout.addLayout(self.dos_visualization_grid)
        self.dos_layout.setContentsMargins(10, 5, 15, 5)

        bz_grid_label = QLabel("Brillouin Zone Grid")
        bz_grid_label.setProperty("style", "bold")
        bz_grid_label.setAlignment(Qt.AlignCenter)
        self.bz_grid.addWidget(bz_grid_label, 0, 0, 1, 3)

        dos_presentation_label = QLabel("DOS Visualization")
        dos_presentation_label.setProperty("style", "bold")
        dos_presentation_label.setAlignment(Qt.AlignCenter)
        self.dos_visualization_grid.addWidget(
            dos_presentation_label, 0, 0, 1, 3
        )

        # Grid points controls
        self.v1_points_spinbox = QSpinBox()
        self.v2_points_spinbox = QSpinBox()
        self.v3_points_spinbox = QSpinBox()
        self.num_bins_spinbox = EnterKeyIntSpinBox()
        self.broadening_spinbox = EnterKeySpinBox()

        for b in [
            self.v1_points_spinbox,
            self.v2_points_spinbox,
            self.v3_points_spinbox,
        ]:
            b.setRange(2, 200)
            b.setValue(30)
            set_spinbox_digit_width(b, 3)
            b.setButtonSymbols(QSpinBox.NoButtons)
            b.setEnabled(False)

        self.num_bins_spinbox.setRange(2, 1000)
        self.num_bins_spinbox.setValue(20)
        self.num_bins_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        set_spinbox_digit_width(self.num_bins_spinbox, 5)

        self.broadening_spinbox.setDecimals(3)
        self.broadening_spinbox.setRange(0.001, 10.0)
        self.broadening_spinbox.setValue(0.001)
        self.broadening_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        set_spinbox_digit_width(self.broadening_spinbox, 5)

        self.bz_grid.addWidget(QLabel("v<sub>1</sub> points:"), 1, 0)
        self.bz_grid.addWidget(QLabel("v<sub>2</sub> points:"), 2, 0)
        self.bz_grid.addWidget(QLabel("v<sub>3</sub> points:"), 3, 0)

        self.bz_grid.addWidget(self.v1_points_spinbox, 1, 1)
        self.bz_grid.addWidget(self.v2_points_spinbox, 2, 1)
        self.bz_grid.addWidget(self.v3_points_spinbox, 3, 1)

        # Approximate output size label
        self.approximate_BZ_grid_size = QLabel("Approximate output size: 0 kB")
        self.bz_grid.addWidget(self.approximate_BZ_grid_size, 4, 0, 1, 3)

        self.dos_visualization_grid.addWidget(QLabel("Bin number:"), 1, 0)
        self.dos_visualization_grid.addWidget(QLabel("Broadening:"), 2, 0)

        self.dos_visualization_grid.addWidget(self.num_bins_spinbox, 1, 1)
        self.dos_visualization_grid.addWidget(self.broadening_spinbox, 2, 1)

        self.compute_grid_btn = QPushButton("Compute")
        self.compute_grid_btn.setEnabled(False)

        # Grid type choice
        self.MP_radio = QRadioButton("Monkhorst-Pack")
        self.Gamma_radio = QRadioButton("Γ-centered")
        self.grid_choice_group = QButtonGroup(self)
        self.grid_choice_group.addButton(self.MP_radio, id=0)
        self.grid_choice_group.addButton(self.Gamma_radio, id=1)
        self.MP_radio.setChecked(True)

        # DOS presentation choice
        self.histogram_radio = QRadioButton("Histogram")
        self.lorentzian_radio = QRadioButton("Lorentzian")
        self.presentation_choice_group = QButtonGroup(self)
        self.presentation_choice_group.addButton(self.histogram_radio, id=0)
        self.presentation_choice_group.addButton(self.lorentzian_radio, id=1)
        self.histogram_radio.setChecked(True)

        self.bz_grid.addWidget(self.MP_radio, 1, 2)
        self.bz_grid.addWidget(self.Gamma_radio, 2, 2)
        self.bz_grid.addWidget(self.compute_grid_btn, 3, 2)

        self.dos_visualization_grid.addWidget(self.histogram_radio, 1, 2)
        self.dos_visualization_grid.addWidget(self.lorentzian_radio, 2, 2)
