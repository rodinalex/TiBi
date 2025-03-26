from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
    QLabel,
)
from PySide6.QtGui import QDoubleValidator
from models.uc_models import UCFormModel


class UnitCellPanel(QWidget):
    def __init__(self, model: UCFormModel):
        super().__init__()

        self.model = model

        # Name field
        form_layout = QFormLayout()

        self.name = QLineEdit()
        self.name.textChanged.connect(lambda t: self.update_model("name", t))
        form_layout.addRow("Name:", self.name)

        # Function to create a row with (x, y, z) input fields
        def create_vector_row(v):
            layout = QHBoxLayout()  # Pack x, y, and z fields horizontally
            x = QLineEdit()
            y = QLineEdit()
            z = QLineEdit()

            x.setValidator(QDoubleValidator())
            y.setValidator(QDoubleValidator())
            z.setValidator(QDoubleValidator())

            x.textChanged.connect(lambda t: self.update_model(v + "x", float(t)))
            y.textChanged.connect(lambda t: self.update_model(v + "y", float(t)))
            z.textChanged.connect(lambda t: self.update_model(v + "z", float(t)))

            layout.addWidget(x)
            layout.addWidget(y)
            layout.addWidget(z)
            return layout, (x, y, z)

        # Create vector input rows
        self.v1_layout, self.v1 = create_vector_row("v1")
        self.v2_layout, self.v2 = create_vector_row("v2")
        self.v3_layout, self.v3 = create_vector_row("v3")

        form_layout.addRow(QLabel("v<sub>1</sub>:"), self.v1_layout)
        form_layout.addRow(QLabel("v<sub>2</sub>:"), self.v2_layout)
        form_layout.addRow(QLabel("v<sub>3</sub>:"), self.v3_layout)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)

        # Sync the UI with the model
        self.update_ui()
        model.signals.updated.connect(self.update_ui)

    def update_model(self, key, value):
        self.model[key] = value

    def update_ui(self):
        self.name.setText(self.model["name"])

        self.v1[0].setText(str(self.model["v1x"]))
        self.v1[1].setText(str(self.model["v1y"]))
        self.v1[2].setText(str(self.model["v1z"]))

        self.v2[0].setText(str(self.model["v2x"]))
        self.v2[1].setText(str(self.model["v2y"]))
        self.v2[2].setText(str(self.model["v2z"]))

        self.v3[0].setText(str(self.model["v3x"]))
        self.v3[1].setText(str(self.model["v3y"]))
        self.v3[2].setText(str(self.model["v3z"]))
