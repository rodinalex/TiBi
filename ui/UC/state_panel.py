from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
    QPushButton,
)
from PySide6.QtGui import QDoubleValidator
from models.uc_models import DataModel


class StatePanel(QWidget):
    def __init__(self, model: DataModel):
        super().__init__()

        self.model = model

        # Form layout
        form_layout = QFormLayout()

        # Name field
        self.name = QLineEdit()
        self.name.textChanged.connect(lambda t: self.update_model("name", t))
        form_layout.addRow("Name:", self.name)

        # Energy field
        self.energy = QLineEdit()
        self.energy.setValidator(QDoubleValidator())
        # Safely convert text to float, handling invalid inputs
        self.energy.textChanged.connect(
            lambda t: self.update_model("energy", self.safe_float(t, "energy"))
        )
        form_layout.addRow("Energy:", self.energy)

        # Buttons for actions
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Delete")
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
        self.energy.setText(str(self.model["energy"]))

    def safe_float(self, text, key):
        """Safely convert text to float, handling invalid inputs"""
        try:
            if text:
                return float(text)
            return 0.0
        except ValueError:
            # Return the previous value or 0.0 if conversion fails
            return self.model.get(key, 0.0)
