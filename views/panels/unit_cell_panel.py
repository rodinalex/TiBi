from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ui.constants import CF_vermillion, CF_green, CF_sky
from ..widgets import EnterKeySpinBox
from models import BasisVector


class UnitCellPanel(QWidget):
    """
    Form panel for editing unit cell properties.

    This panel provides a form interface for editing a unit cell's properties:
    - System dimensionality
    - Three basis vectors (v1, v2, v3) with x, y, z components

    The panel uses a reactive data binding approach, where UI components are
    automatically updated when the model changes, and model updates trigger
    appropriate UI refreshes.
    """

    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout(self)

        # Layout for basis vectors
        grid_layout = QGridLayout()

        panel_header = QLabel("Unit Cell Parameters")
        panel_header.setAlignment(Qt.AlignCenter)

        dimensionality_header = QLabel("Dimensionality")
        dimensionality_header.setAlignment(Qt.AlignCenter)

        basis_header = QLabel("Basis Vectors")
        basis_header.setAlignment(Qt.AlignCenter)

        # Dimensionality radio buttons
        self.radio0D = QRadioButton("0")
        self.radio1D = QRadioButton("1")
        self.radio2D = QRadioButton("2")
        self.radio3D = QRadioButton("3")

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio0D, id=0)
        self.radio_group.addButton(self.radio1D, id=1)
        self.radio_group.addButton(self.radio2D, id=2)
        self.radio_group.addButton(self.radio3D, id=3)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio0D)
        radio_layout.addWidget(self.radio1D)
        radio_layout.addWidget(self.radio2D)
        radio_layout.addWidget(self.radio3D)

        # Add Site and Reduce UC (LLL algorithm) buttons
        button_layout = QHBoxLayout()
        self.new_site_btn = QPushButton("+ Site")
        self.reduce_btn = QPushButton("Reduce")
        button_layout.addWidget(self.new_site_btn)
        button_layout.addWidget(self.reduce_btn)

        # Assemble the panel

        layout.addWidget(panel_header)
        layout.addWidget(dimensionality_header)
        layout.addLayout(radio_layout)
        layout.addLayout(grid_layout)
        layout.addLayout(button_layout)

        # Populate the basis vector grid
        grid_layout.addWidget(basis_header, 0, 1, 1, 3)

        # Function to create a row with (x, y, z) input fields
        def create_vector_column(n):
            x = EnterKeySpinBox()
            y = EnterKeySpinBox()
            z = EnterKeySpinBox()

            for coord in [x, y, z]:
                coord.setButtonSymbols(EnterKeySpinBox.NoButtons)
                coord.setRange(-1e308, 1e308)
                coord.setFixedWidth(40)
                coord.setDecimals(3)

            # Vector components are stacked vertically
            grid_layout.addWidget(x, 2, n)
            grid_layout.addWidget(y, 3, n)
            grid_layout.addWidget(z, 4, n)
            return (x, y, z)

        # Create vector input columns
        self.v1 = create_vector_column(1)
        self.v2 = create_vector_column(2)
        self.v3 = create_vector_column(3)

        # Vector labels go above the coordinate columns
        v1_label = QLabel("v<sub>1</sub>")
        v1_label.setAlignment(Qt.AlignCenter)
        v2_label = QLabel("v<sub>2</sub>")
        v2_label.setAlignment(Qt.AlignCenter)
        v3_label = QLabel("v<sub>3</sub>")
        v3_label.setAlignment(Qt.AlignCenter)

        grid_layout.addWidget(v1_label, 1, 1)
        grid_layout.addWidget(v2_label, 1, 2)
        grid_layout.addWidget(v3_label, 1, 3)

        # Create a coordinate label column to the left of coordinate columns
        for ii, (text, color) in enumerate(
            zip(["x", "y", "z"], [CF_vermillion, CF_green, CF_sky]), start=1
        ):
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            c = (
                int(color[0] * 255),
                int(color[1] * 255),
                int(color[2] * 255),
                int(color[3]),
            )  # Color in 0-255 component range
            label.setStyleSheet(f"color: rgba({c[0]},{c[1]},{c[2]},{c[3]});")
            grid_layout.addWidget(label, 1 + ii, 0)

        grid_layout.setVerticalSpacing(2)

    def set_basis_vectors(
        self, v1: BasisVector, v2: BasisVector, v3: BasisVector
    ) -> None:
        """
        Set the basis vectors in the UI.

        Args:
            v1 (BasisVector): Basis vector 1.
            v2 (BasisVector): Basis vector 2.
            v3 (BasisVector): Basis vector 3.
        """
        for ii, coord in enumerate("xyz"):
            self.v1[ii].setValue(getattr(v1, coord))
            self.v2[ii].setValue(getattr(v2, coord))
            self.v3[ii].setValue(getattr(v3, coord))
