from PySide6.QtWidgets import (
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from .panels import BandsPanel, HoppingPanel


class ComputationView(QWidget):
    """
    A multi-tab view for setting up and managing computations.

    This view contains the following panels:

    - HoppintPanel: For managing hopping parameters
    - BandsPanel: For managing band structure and Brillouin grid calculations

    Attributes
    ----------
    hopping_panel : HoppingPanel
        Panel for editing hopping parameters between states.
    bands_panel : BandsPanel
        Panel for managing band and Brillouin grid calculations.
    """

    def __init__(self):
        super().__init__()

        # Create a layout for the TabView itself
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins to maximize space
        self.hopping_panel = HoppingPanel()
        self.bands_panel = BandsPanel()

        # Wrap each panel in scroll area
        hopping_scroll = QScrollArea()
        hopping_scroll.setWidgetResizable(True)
        hopping_scroll.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        hopping_scroll.setWidget(self.hopping_panel)

        bands_scroll = QScrollArea()
        bands_scroll.setWidgetResizable(True)
        bands_scroll.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        bands_scroll.setWidget(self.bands_panel)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.addTab(hopping_scroll, "Hopping")
        self.tabs.addTab(bands_scroll, "Bands")
        self.tabs.setTabPosition(QTabWidget.East)
        self.tabs.setDocumentMode(True)

        layout.addWidget(self.tabs)

        # Set the layout for this widget
        self.setLayout(layout)
