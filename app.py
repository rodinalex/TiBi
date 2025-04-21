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


def main():
    # Create models
    unit_cells = {}
    # ... other models

    # Create UI components
    uc_ui = UnitCellUI()
    hopping_panel = HoppingPanel()
    unit_cell_plot = UnitCellPlot()
    bz_plot = BrillouinZonePlot()
    band_plot = BandStructurePlot()

    # Create the main window and arrange components
    main_window = MainWindow(
        uc_ui=uc_ui,
        hopping_panel=hopping_panel,
        unit_cell_plot=unit_cell_plot,
        bz_plot=bz_plot,
        band_plot=band_plot,
    )

    # Create controllers
    app_controller = AppController(
        uc=uc_ui,
        hopping=hopping_panel,
        unit_cell_plot=unit_cell_plot,
        bz_plot=bz_plot,
        band_plot=band_plot,
    )
    # ... other controllers

    # Start the application
    main_window.show()
    app.exec()


class MainWindow(QMainWindow):
    def __init__(self, uc_ui, hopping_panel, unit_cell_plot, bz_plot, band_plot):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1500, 900))

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        # Create layout with passed-in components
        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Add components to layouts
        left_layout.addWidget(uc_ui, stretch=1)
        left_layout.addWidget(hopping_panel, stretch=2)
        # ... and so on

        # Set as central widget
        self.setCentralWidget(main_view)


if __name__ == "__main__":
    # This is the entry point when running "python3 app.py"
    app = QApplication(sys.argv)
    main()
    sys.exit(app.exec())


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
