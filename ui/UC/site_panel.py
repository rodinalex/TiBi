from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QDoubleSpinBox,
    QLabel,
)

from PySide6.QtCore import Qt

from models.uc_models import DataModel


class SitePanel(QWidget):
    """
    Form panel for editing site properties.

    This panel provides a form interface for editing a site's properties:
    - Name
    - Fractional coordinates (c1, c2, c3) within the unit cell

    It uses reactive data binding to keep the UI and model in sync.
    """

    def __init__(self, model: DataModel):
        super().__init__()

        self.model = model

        header = QLabel("Site fractional coordinates")
        header.setAlignment(Qt.AlignCenter)

        spinner_layout = QHBoxLayout()

        # Coordinate fields
        self.c1 = QDoubleSpinBox()
        self.c2 = QDoubleSpinBox()
        self.c3 = QDoubleSpinBox()

        for c in [self.c1, self.c2, self.c3]:
            c.setRange(0.0, 1.0)
            c.setSingleStep(0.01)
            c.setDecimals(3)

        # Connect signals to update model
        self.c1.editingFinished.connect(
            lambda: self.update_model("c1", self.c1.value())
        )
        self.c2.editingFinished.connect(
            lambda: self.update_model("c2", self.c2.value())
        )
        self.c3.editingFinished.connect(
            lambda: self.update_model("c3", self.c3.value())
        )

        # Create row layouts with labels on the left and spin boxes on the right
        spinner1 = QHBoxLayout()
        spinner1.addWidget(QLabel("c<sub>1</sub>:"))
        spinner1.addWidget(self.c1)

        spinner2 = QHBoxLayout()
        spinner2.addWidget(QLabel("c<sub>2</sub>:"))
        spinner2.addWidget(self.c2)

        spinner3 = QHBoxLayout()
        spinner3.addWidget(QLabel("c<sub>3</sub>:"))
        spinner3.addWidget(self.c3)

        # Add spinners to the main form layout
        spinner_layout.addLayout(spinner1)
        spinner_layout.addLayout(spinner2)
        spinner_layout.addLayout(spinner3)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(header)
        layout.addLayout(spinner_layout)

        # Sync the UI with the model
        self.update_ui()

    # Update model when the fields are being changed
    def update_model(self, key, value):
        self.model[key] = value

    # Use the model to fill the form fields
    def update_ui(self):
        self.c1.setValue(self.model["c1"])
        self.c2.setValue(self.model["c2"])
        self.c3.setValue(self.model["c3"])
