from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtGui import QDoubleValidator
from models.uc_models import UCFormModel


class SitePanel(QWidget):
    def __init__(self, model: UCFormModel):
        super().__init__()

        self.model = model

        # Name field
        form_layout = QFormLayout()

        self.name = QLineEdit()
        self.name.textChanged.connect(lambda t: self.update_model("name", t))
        form_layout.addRow("Name:", self.name)

        # Coordinate fields
        self.c1 = QLineEdit()
        self.c2 = QLineEdit()
        self.c3 = QLineEdit()

        # Set validators to ensure numeric input
        self.c1.setValidator(QDoubleValidator())
        self.c2.setValidator(QDoubleValidator())
        self.c3.setValidator(QDoubleValidator())

        # Connect signals to update model
        self.c1.textChanged.connect(
            lambda t: self.update_model("c1", self.safe_float(t, "c1"))
        )
        self.c2.textChanged.connect(
            lambda t: self.update_model("c2", self.safe_float(t, "c2"))
        )
        self.c3.textChanged.connect(
            lambda t: self.update_model("c3", self.safe_float(t, "c3"))
        )

        # Add form fields
        form_layout.addRow("c<sub>1</sub>:", self.c1)
        form_layout.addRow("c<sub>2</sub>:", self.c2)
        form_layout.addRow("c<sub>3</sub>:", self.c3)

        # Buttons for actions
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Site")
        self.apply_btn = QPushButton("Apply Changes")
        self.delete_btn = QPushButton("Delete")
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.apply_btn)
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
        self.c1.setText(str(self.model["c1"]))
        self.c2.setText(str(self.model["c2"]))
        self.c3.setText(str(self.model["c3"]))

    def safe_float(self, text, key):
        """Safely convert text to float, handling invalid inputs"""
        try:
            if text:
                return float(text)
            return 0.0
        except ValueError:
            # Return the previous value or 0.0 if conversion fails
            return self.model.get(key, 0.0)
