from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QWidget,
    QLineEdit,
    QFormLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
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
            c = QCheckBox()

            x.setValidator(QDoubleValidator())
            y.setValidator(QDoubleValidator())
            z.setValidator(QDoubleValidator())

            x.textChanged.connect(
                lambda t: self.update_model(v + "x", self.safe_float(t, v + "x"))
            )
            y.textChanged.connect(
                lambda t: self.update_model(v + "y", self.safe_float(t, v + "y"))
            )
            z.textChanged.connect(
                lambda t: self.update_model(v + "z", self.safe_float(t, v + "z"))
            )
            c.checkStateChanged.connect(
                lambda t: self.update_model(v + "periodic", t == Qt.Checked)
            )
            # IMPLEMENT editingFinished() signal from the text boxes
            # z.editingFinished().connect()

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

        # Buttons for actions
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Site")
        self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Delete")
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        # Sync the UI with the model
        self.update_ui()

    # Update model when the fields are being changed
    def update_model(self, key, value):
        self.model[key] = value

    # Use the model to fill the form fields
    def update_ui(self):
        self.name.setText(self.model["name"])

        self.v1[0].setText(str(self.model["v1x"]))
        self.v1[1].setText(str(self.model["v1y"]))
        self.v1[2].setText(str(self.model["v1z"]))
        self.v1[3].setChecked(bool(self.model["v1periodic"]))

        self.v2[0].setText(str(self.model["v2x"]))
        self.v2[1].setText(str(self.model["v2y"]))
        self.v2[2].setText(str(self.model["v2z"]))
        self.v2[3].setChecked(bool(self.model["v2periodic"]))

        self.v3[0].setText(str(self.model["v3x"]))
        self.v3[1].setText(str(self.model["v3y"]))
        self.v3[2].setText(str(self.model["v3z"]))
        self.v3[3].setChecked(bool(self.model["v3periodic"]))

    def safe_float(self, text, key):
        """Safely convert text to float, handling invalid inputs"""
        try:
            if text:
                return float(text)
            return 0.0
        except ValueError:
            # Return the previous value or 0.0 if conversion fails
            return self.model.get(key, 0.0)
