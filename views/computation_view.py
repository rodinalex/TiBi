from PySide6.QtWidgets import (
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from .panels import BandsPanel, HoppingPanel


class ComputationView(QWidget):
    """ """

    def __init__(self):
        """ """
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
        # Set size policy to make the tab widget expand
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the tab widget to the layout
        layout.addWidget(self.tabs)

        # Set the layout for this widget
        self.setLayout(layout)

        # Ensure the TabView itself expands properly
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setMinimumSize(QSize(300, 200))
