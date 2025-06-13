from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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
from TiBi.ui import get_resource_path
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
        path_label = QLabel("Band Calculations")
        path_label.setProperty("style", "bold")
        path_label.setAlignment(
            Qt.AlignCenter
        )  # This centers the text within the label
        self.bands_grid.addWidget(path_label, 0, 0, 1, 8)

        # Icons
        left_arrow_icon = QIcon()
        left_arrow_icon.addFile(
            str(get_resource_path("assets/icons/down_arrow.svg")),
            mode=QIcon.Mode.Normal,
        )
        left_arrow_icon.addFile(
            str(get_resource_path("assets/icons/down_arrow_disabled.svg")),
            mode=QIcon.Mode.Disabled,
        )

        right_arrow_icon = QIcon()
        right_arrow_icon.addFile(
            str(get_resource_path("assets/icons/up_arrow.svg")),
            mode=QIcon.Mode.Normal,
        )
        right_arrow_icon.addFile(
            str(get_resource_path("assets/icons/up_arrow_disabled.svg")),
            mode=QIcon.Mode.Disabled,
        )

        # Gamma point controls (Γ - origin of reciprocal space)
        self.add_gamma_btn = QPushButton("Γ")
        self.add_gamma_btn.setToolTip("Gamma Point")
        self.add_gamma_btn.setStatusTip("Add the Gamma Point to the path.")
        self.add_gamma_btn.setFixedSize(30, 30)
        self.bands_grid.addWidget(self.add_gamma_btn, 2, 0)
        # Vertex selection controls
        self.prev_vertex_btn = QPushButton()
        self.prev_vertex_btn.setToolTip("Previous")
        self.prev_vertex_btn.setStatusTip("Select the previous Vertex.")
        self.prev_vertex_btn.setIcon(left_arrow_icon)
        self.prev_vertex_btn.setIconSize(self.prev_vertex_btn.sizeHint())

        self.next_vertex_btn = QPushButton()
        self.next_vertex_btn.setToolTip("Next")
        self.next_vertex_btn.setStatusTip("Select the next Vertex.")
        self.next_vertex_btn.setIcon(right_arrow_icon)
        self.next_vertex_btn.setIconSize(self.next_vertex_btn.sizeHint())

        self.add_vertex_btn = QPushButton("V")
        self.add_vertex_btn.setToolTip("Vertex")
        self.add_vertex_btn.setStatusTip(
            "Add the selected Vertex to the path."
        )
        self.prev_vertex_btn.setFixedSize(30, 30)
        self.next_vertex_btn.setFixedSize(30, 30)
        self.add_vertex_btn.setFixedSize(30, 30)

        self.bands_grid.addWidget(self.next_vertex_btn, 1, 1)
        self.bands_grid.addWidget(self.add_vertex_btn, 2, 1)
        self.bands_grid.addWidget(self.prev_vertex_btn, 3, 1)

        # Edge midpoint selection controls
        self.prev_edge_btn = QPushButton()
        self.prev_edge_btn.setToolTip("Previous")
        self.prev_edge_btn.setStatusTip("Select the previous Edge.")
        self.prev_edge_btn.setIcon(left_arrow_icon)
        self.prev_edge_btn.setIconSize(self.prev_edge_btn.sizeHint())

        self.next_edge_btn = QPushButton()
        self.next_edge_btn.setToolTip("Next")
        self.next_edge_btn.setStatusTip("Select the next Edge.")
        self.next_edge_btn.setIcon(right_arrow_icon)
        self.next_edge_btn.setIconSize(self.next_edge_btn.sizeHint())

        self.add_edge_btn = QPushButton("E")
        self.add_edge_btn.setToolTip("Edge")
        self.add_edge_btn.setStatusTip("Add the selected Edge to the path.")
        self.prev_edge_btn.setFixedSize(30, 30)
        self.next_edge_btn.setFixedSize(30, 30)
        self.add_edge_btn.setFixedSize(30, 30)

        self.bands_grid.addWidget(self.next_edge_btn, 1, 2)
        self.bands_grid.addWidget(self.add_edge_btn, 2, 2)
        self.bands_grid.addWidget(self.prev_edge_btn, 3, 2)

        # Face center selection controls
        self.prev_face_btn = QPushButton()
        self.prev_face_btn.setToolTip("Previous")
        self.prev_face_btn.setStatusTip("Select the previous Face.")
        self.prev_face_btn.setIcon(left_arrow_icon)
        self.prev_face_btn.setIconSize(self.prev_face_btn.sizeHint())

        self.next_face_btn = QPushButton()
        self.next_face_btn.setToolTip("Next")
        self.next_face_btn.setStatusTip("Select the next Face.")
        self.next_face_btn.setIcon(right_arrow_icon)
        self.next_face_btn.setIconSize(self.next_face_btn.sizeHint())

        self.add_face_btn = QPushButton("F")
        self.add_face_btn.setToolTip("Face")
        self.add_face_btn.setStatusTip("Add the selected Face to the path.")
        self.prev_face_btn.setFixedSize(30, 30)
        self.next_face_btn.setFixedSize(30, 30)
        self.add_face_btn.setFixedSize(30, 30)

        self.bands_grid.addWidget(self.next_face_btn, 1, 3)
        self.bands_grid.addWidget(self.add_face_btn, 2, 3)
        self.bands_grid.addWidget(self.prev_face_btn, 3, 3)

        # Path controls
        self.remove_last_btn = QPushButton()
        remove_last = QIcon()
        remove_last.addFile(
            str(get_resource_path("assets/icons/remove_last.svg")),
            mode=QIcon.Mode.Normal,
        )
        remove_last.addFile(
            str(get_resource_path("assets/icons/remove_last_disabled.svg")),
            mode=QIcon.Mode.Disabled,
        )
        self.remove_last_btn.setIcon(remove_last)
        self.remove_last_btn.setFixedSize(30, 30)
        self.remove_last_btn.setIconSize(self.remove_last_btn.sizeHint())
        self.remove_last_btn.setToolTip("Remove Last")
        self.remove_last_btn.setStatusTip(
            "Remove the last added point from the Brillouin Zone path."
        )

        self.clear_path_btn = QPushButton()
        clear_path_icon = QIcon()
        clear_path_icon.addFile(
            str(get_resource_path("assets/icons/trash_hopping.svg")),
            mode=QIcon.Mode.Normal,
        )
        clear_path_icon.addFile(
            str(get_resource_path("assets/icons/trash_hopping_disabled.svg")),
            mode=QIcon.Mode.Disabled,
        )
        self.clear_path_btn.setIcon(clear_path_icon)
        self.clear_path_btn.setFixedSize(30, 30)
        self.clear_path_btn.setIconSize(self.clear_path_btn.sizeHint())
        self.clear_path_btn.setToolTip("Clear")
        self.clear_path_btn.setStatusTip("Clear the Brillouin Zone path.")

        kpoints_layout = QHBoxLayout()
        self.n_points_spinbox = QSpinBox()
        self.n_points_spinbox.setRange(1, 10000)
        self.n_points_spinbox.setValue(100)
        self.n_points_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        set_spinbox_digit_width(self.n_points_spinbox, 5)

        self.compute_bands_btn = QPushButton()
        compute_icon = QIcon()
        compute_icon.addFile(
            str(get_resource_path("assets/icons/computer.svg")),
            mode=QIcon.Mode.Normal,
        )
        compute_icon.addFile(
            str(get_resource_path("assets/icons/computer_disabled.svg")),
            mode=QIcon.Mode.Disabled,
        )
        self.compute_bands_btn.setIcon(compute_icon)
        self.compute_bands_btn.setFixedSize(30, 30)
        self.compute_bands_btn.setIconSize(self.compute_bands_btn.sizeHint())
        self.compute_bands_btn.setToolTip("Compute")
        self.compute_bands_btn.setStatusTip("Compute the Bands.")

        self.bands_grid.addWidget(self.remove_last_btn, 1, 5)
        self.remove_last_btn.setEnabled(
            False
        )  # Disabled until path has points

        self.bands_grid.addWidget(self.clear_path_btn, 1, 6)
        self.clear_path_btn.setEnabled(False)  # Disabled until path has points

        self.bands_grid.addWidget(self.compute_bands_btn, 1, 7)
        self.compute_bands_btn.setEnabled(
            False
        )  # Disabled until path has at least two points

        kpoints_layout.addWidget(QLabel("Points:"))
        kpoints_layout.addWidget(self.n_points_spinbox)
        self.bands_grid.addLayout(kpoints_layout, 2, 5, 1, 3)

        self.bands_grid.setVerticalSpacing(5)
        self.bands_grid.setHorizontalSpacing(5)

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

        for row in range(4):  # Rows 0 to 4 in bands_grid
            self.bands_grid.setRowMinimumHeight(row, 25)

        # Approximate output size label
        self.approximate_band_size = QLabel("Approximate output size: 0 kB")
        self.bands_grid.addWidget(self.approximate_band_size, 4, 0, 1, 8)

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
        self.select_all_btn.setToolTip("Select All")
        self.select_all_btn.statusTip("Select all States for Projection.")
        self.clear_all_btn = QPushButton("None")
        self.clear_all_btn.setToolTip("Clear Selection")
        self.clear_all_btn.statusTip(
            "Deselect all States and show only the Bands."
        )
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
        self.bz_grid.addWidget(bz_grid_label, 0, 0, 1, 4)

        dos_presentation_label = QLabel("DOS Visualization")
        dos_presentation_label.setProperty("style", "bold")
        dos_presentation_label.setAlignment(Qt.AlignCenter)
        self.dos_visualization_grid.addWidget(
            dos_presentation_label, 0, 0, 1, 4
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
        self.bz_grid.addWidget(self.approximate_BZ_grid_size, 4, 0, 1, 4)

        self.dos_visualization_grid.addWidget(QLabel("Bin number:"), 1, 0)
        self.dos_visualization_grid.addWidget(QLabel("Broadening:"), 2, 0)

        self.dos_visualization_grid.addWidget(self.num_bins_spinbox, 1, 1)
        self.dos_visualization_grid.addWidget(self.broadening_spinbox, 2, 1)

        self.compute_grid_btn = QPushButton()
        self.compute_grid_btn.setIcon(compute_icon)
        self.compute_grid_btn.setFixedSize(30, 30)
        self.compute_grid_btn.setIconSize(self.compute_grid_btn.sizeHint())
        self.compute_grid_btn.setToolTip("Compute")
        self.compute_grid_btn.setStatusTip("Compute the Brillouin Zone grid.")
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

        self.bz_grid.addWidget(self.MP_radio, 1, 3)
        self.bz_grid.addWidget(self.Gamma_radio, 2, 3)
        self.bz_grid.addWidget(self.compute_grid_btn, 3, 3)

        self.dos_visualization_grid.addWidget(self.histogram_radio, 1, 3)
        self.dos_visualization_grid.addWidget(self.lorentzian_radio, 2, 3)
