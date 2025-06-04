from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..widgets import EnterKeySpinBox


class SitePanel(QWidget):
    """
    Form panel for editing site properties.

    This panel provides a form interface for editing a site's properties:
    - Radius for the site marker
    - Color for the site marker
    - Fractional coordinates (c1, c2, c3) within the unit cell

    It uses reactive data binding to keep the UI and model in sync.
    """

    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout(self)

        panel_header = QLabel("Site Parameters")
        panel_header.setProperty("style", "bold")
        panel_header.setAlignment(Qt.AlignCenter)

        header = QLabel("Site Coordinates")
        header.setAlignment(Qt.AlignCenter)

        # Coordinate and radius fields
        self.R = EnterKeySpinBox()
        self.c1 = EnterKeySpinBox()
        self.c2 = EnterKeySpinBox()
        self.c3 = EnterKeySpinBox()

        for c in [self.R, self.c1, self.c2, self.c3]:
            c.setRange(0.0, 1.0)
            c.setDecimals(3)
            c.setButtonSymbols(EnterKeySpinBox.NoButtons)

        # Color picker button
        self.color_picker_btn = QPushButton()
        self.color_picker_btn.setFixedWidth(25)

        appearance_layout = QHBoxLayout()
        appearance_layout.addWidget(QLabel("Radius:"))
        appearance_layout.addWidget(self.R)
        appearance_layout.addWidget(QLabel("Color:"))
        appearance_layout.addWidget(self.color_picker_btn)

        # Create a grid layout with labels on top and spin boxes below
        c1_label = QLabel("c<sub>1</sub>")
        c1_label.setAlignment(Qt.AlignCenter)
        c2_label = QLabel("c<sub>2</sub>")
        c2_label.setAlignment(Qt.AlignCenter)
        c3_label = QLabel("c<sub>3</sub>")
        c3_label.setAlignment(Qt.AlignCenter)

        grid_layout = QGridLayout()
        grid_layout.addWidget(c1_label, 1, 0)
        grid_layout.addWidget(c2_label, 1, 1)
        grid_layout.addWidget(c3_label, 1, 2)

        grid_layout.addWidget(self.c1, 2, 0)
        grid_layout.addWidget(self.c2, 2, 1)
        grid_layout.addWidget(self.c3, 2, 2)
        grid_layout.setVerticalSpacing(2)

        layout.addWidget(panel_header)
        layout.addLayout(appearance_layout)
        layout.addWidget(header)
        layout.addLayout(grid_layout)
