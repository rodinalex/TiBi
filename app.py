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
from ui.placeholder import PlaceholderWidget


class MainWindow(QMainWindow):
    """
    Main application window that sets up the overall UI layout and coordinates interactions
    between different components.

    The layout consists of three columns:
    - Left column: Unit cell hierarchy tree view and property panels
    - Middle column: 3D visualization and hopping matrix
    - Right column: Computation options (placeholder for future functionality)
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1200, 900))

        # Initialize UI panels
        self.uc = UnitCellUI()

        # Initialize the plots
        self.unit_cell_plot = UnitCellPlot()
        self.bz_plot = BrillouinZonePlot()

        # Initialize the hopping panel
        self.hopping = HoppingPanel(self.uc.unit_cells)

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left column for hierarchical view and form panels
        left_layout.addWidget(self.uc, stretch=1)
        left_layout.addWidget(self.hopping, stretch=1)

        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=2)
        mid_layout.addWidget(PlaceholderWidget("Computation Options"), stretch=1)
        mid_layout.addWidget(PlaceholderWidget("Computation Options"), stretch=1)

        # Connect signals to update the plot after tree selection
        self.uc.selection.signals.updated.connect(self.update_plot)
        # Connect signals to update the plot after the model for the unit cell or site changes
        self.uc.unit_cell_model.signals.updated.connect(self.update_plot)
        self.uc.site_model.signals.updated.connect(self.update_plot)
        # Notify the hopping block when the selection changes
        self.uc.selection.signals.updated.connect(
            lambda: self.hopping.set_uc_id(self.uc.selection["unit_cell"])
        )

        right_layout.addWidget(self.bz_plot, stretch=1)
        right_layout.addWidget(PlaceholderWidget("BZ Tools"), stretch=1)
        right_layout.addWidget(PlaceholderWidget("Computation Options"), stretch=2)

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(mid_layout, stretch=5)
        main_layout.addLayout(right_layout, stretch=3)

        self.setCentralWidget(main_view)

    def update_plot(self):
        """
        Update the 3D plot with the selected unit cell.
        Highlight the selected site in the 3D plot.

        This method is called after a selection in the tree view.
        It first updates the plot to show the correct unit cell, then tells
        the plot to highlight the specific site with a different color.

        Args:
            unit_cell_id: UUID of the unit cell containing the site
            site_id: UUID of the site to highlight
            state: UUID of the state from the state selection signal
        """
        unit_cell_id = self.uc.selection.get("unit_cell", None)
        site_id = self.uc.selection.get("unit_cell", None)
        if unit_cell_id in self.uc.unit_cells:
            unit_cell = self.uc.unit_cells[unit_cell_id]
            self.unit_cell_plot.set_unit_cell(unit_cell)
        else:
            # Clear the plot if unit cell doesn't exist
            self.unit_cell_plot.set_unit_cell(None)

        try:
            if unit_cell_id in self.uc.unit_cells:
                unit_cell = self.uc.unit_cells[unit_cell_id]
                if site_id in unit_cell.sites:
                    self.unit_cell_plot.select_site(site_id)
        except Exception as e:
            print(f"Error highlighting site: {e}")


app = QApplication(sys.argv)
window = MainWindow()

window.show()
app.exec()
