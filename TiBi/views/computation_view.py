from PySide6.QtWidgets import (
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
        # Create main tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.hopping_panel, "Hopping")
        self.tabs.addTab(self.bands_panel, "Bands")
        self.tabs.setTabPosition(QTabWidget.East)
        self.tabs.setDocumentMode(True)
        # Add the tab widget to the layout
        layout.addWidget(self.tabs)

        # Set the layout for this widget
        self.setLayout(layout)
