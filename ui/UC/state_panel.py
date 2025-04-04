from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
    QPushButton,
    QDoubleSpinBox,
)
from models.uc_models import DataModel


class StatePanel(QWidget):
    """
    Form panel for editing quantum state properties.

    This panel provides a form interface for editing a quantum state's properties:
    - Name
    - Energy (in eV)

    It includes validation for the energy field to ensure it's a valid
    floating-point number and uses reactive data binding to keep the UI
    and model in sync.
    """

    def __init__(self, model: DataModel):
        super().__init__()

        self.model = model

        # Form layout
        form_layout = QFormLayout()

        # Name field
        self.name = QLineEdit()
        self.name.editingFinished.connect(
            lambda: self.update_model("name", self.name.text())
        )
        form_layout.addRow("Name:", self.name)

        # Energy field
        self.energy = QDoubleSpinBox()
        self.energy.editingFinished.connect(
            lambda: self.update_model("energy", self.energy.value())
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
        self.energy.setValue(self.model["energy"])
