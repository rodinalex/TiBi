import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from ui.uc_plot import UnitCellPlot
from ui.bz_plot import BrillouinZonePlot
from ui.uc import UnitCellUI
from ui.hopping import HoppingPanel
from ui.band_plot import BandStructurePlot
from ui.placeholder import PlaceholderWidget
from controllers.app_controller import AppController


class MainWindow(QMainWindow):
    """
    Main application window that sets up the overall UI layout and coordinates interactions
    between different components.

    The layout consists of three columns:
    - Left column: Unit cell hierarchy tree view and property panels
    - Middle column: 3D visualization and hopping matrix
    - Right column: Computation options and band structure visualization
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1500, 900))

        # Hamiltonian
        self.hamiltonian = None

        # Initialize UI panels
        self.uc = UnitCellUI()

        # Initialize the plots
        self.unit_cell_plot = UnitCellPlot()
        self.bz_plot = BrillouinZonePlot()
        self.band_plot = BandStructurePlot()

        # Initialize the hopping panel
        self.hopping = HoppingPanel(self.uc.unit_cells)

        # Initialize the app controller
        self.controller = AppController(
            self.uc, self.hopping, self.unit_cell_plot, self.bz_plot, self.band_plot
        )

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left column for hierarchical view and form panels
        left_layout.addWidget(self.uc, stretch=1)
        left_layout.addWidget(self.hopping, stretch=2)

        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=1)
        mid_layout.addWidget(self.bz_plot, stretch=1)
        mid_layout.addWidget(PlaceholderWidget("SPOT"), stretch=1)

        # Right column for computation options and band structure
        right_layout.addWidget(self.band_plot, stretch=1)
        right_layout.addWidget(PlaceholderWidget("BAND"), stretch=1)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(mid_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=2)

        self.setCentralWidget(main_view)


app = QApplication(sys.argv)
window = MainWindow()

window.show()
app.exec()
