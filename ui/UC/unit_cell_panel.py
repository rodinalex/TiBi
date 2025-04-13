from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QWidget,
    QFormLayout,
    QLabel,
    QDoubleSpinBox,
    QRadioButton,
    QButtonGroup,
)
from PySide6.QtCore import Qt
from models.uc_models import DataModel


class UnitCellPanel(QWidget):
    """
    Form panel for editing unit cell properties.

    This panel provides a form interface for editing a unit cell's properties:
    - Name
    - Three basis vectors (v1, v2, v3) with x, y, z components
    - Periodicity flags for each basis vector

    The panel uses a reactive data binding approach, where UI components are
    automatically updated when the model changes, and model updates trigger
    appropriate UI refreshes.
    """

    def __init__(self, model: DataModel):
        super().__init__()

        self.model = model

        dimensionality_header = QLabel("Dimensionality")
        dimensionality_header.setAlignment(Qt.AlignCenter)

        basis_header = QLabel("Unit Cell basis")
        basis_header.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(2)

        # Radio buttons
        self.radio0D = QRadioButton("0D")
        self.radio1D = QRadioButton("1D")
        self.radio2D = QRadioButton("2D")
        self.radio3D = QRadioButton("3D")

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

        # Function to create a row with (x, y, z) input fields
        def create_vector_row(v):
            layout = QHBoxLayout()  # Pack x, y, and z fields horizontally
            x = QDoubleSpinBox()
            y = QDoubleSpinBox()
            z = QDoubleSpinBox()
            c = QCheckBox()

            for coord in [x, y, z]:
                coord.setButtonSymbols(QDoubleSpinBox.NoButtons)
                coord.setRange(-1e308, 1e308)
                coord.setFixedWidth(40)
                coord.setDecimals(3)

            # Connect signals to update model

            x.editingFinished.connect(lambda: self.update_model(v + "x", x.value()))
            y.editingFinished.connect(lambda: self.update_model(v + "y", y.value()))
            z.editingFinished.connect(lambda: self.update_model(v + "z", z.value()))
            c.checkStateChanged.connect(
                lambda t: self.update_model(v + "periodic", t == Qt.Checked)
            )

            layout.addWidget(x)
            layout.addWidget(y)
            layout.addWidget(z)
            layout.addWidget(c)
            layout.addWidget(QLabel("Periodic"))
            return layout, (x, y, z, c)

        # Create vector input rows
        self.v1_layout, self.v1 = create_vector_row("v1")
        self.v2_layout, self.v2 = create_vector_row("v2")
        self.v3_layout, self.v3 = create_vector_row("v3")

        form_layout.addRow("v<sub>1</sub>:", self.v1_layout)
        form_layout.addRow("v<sub>2</sub>:", self.v2_layout)
        form_layout.addRow("v<sub>3</sub>:", self.v3_layout)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(dimensionality_header)
        layout.addLayout(radio_layout)
        layout.addWidget(basis_header)
        layout.addLayout(form_layout)

        # layout.setSpacing(5)

        # Sync the UI with the model
        self.update_ui()

    # Update model when the fields are being changed
    def update_model(self, key, value):
        self.model[key] = value

    # Use the model to fill the form fields
    def update_ui(self):

        self.v1[0].setValue(self.model["v1x"])
        self.v1[1].setValue(self.model["v1y"])
        self.v1[2].setValue(self.model["v1z"])
        self.v1[3].setChecked(bool(self.model["v1periodic"]))

        self.v2[0].setValue(self.model["v2x"])
        self.v2[1].setValue(self.model["v2y"])
        self.v2[2].setValue(self.model["v2z"])
        self.v2[3].setChecked(bool(self.model["v2periodic"]))

        self.v3[0].setValue(self.model["v3x"])
        self.v3[1].setValue(self.model["v3y"])
        self.v3[2].setValue(self.model["v3z"])
        self.v3[3].setChecked(bool(self.model["v3periodic"]))
