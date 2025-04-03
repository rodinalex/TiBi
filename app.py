import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from ui.uc_plot import UnitCellPlot
from ui.uc import UnitCellUI
from ui.hopping import HoppingPanel

# from controllers.hopping_controller import HoppingController


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
        self.setFixedSize(QSize(1200, 900))  # Slightly wider to accommodate 3D plot

        # Initialize UI panels
        self.uc = UnitCellUI()

        # Initialize the plot
        self.unit_cell_plot = UnitCellPlot()

        # Initialize the hopping panel
        self.hopping = HoppingPanel(self.uc.unit_cells)

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left column for hierarchical view and form panels
        left_layout.addWidget(self.uc, stretch=2)
        left_layout.addWidget(PlaceholderWidget("Computation Options"), stretch=1)

        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=6)
        mid_layout.addWidget(self.hopping, stretch=4)
        mid_layout.addWidget(PlaceholderWidget("Computation Options"), stretch=2)

        # Connect signals to update the plot when unit cell or site is selected
        self.uc.tree_view_panel.unit_cell_selected.connect(self.update_plot)
        self.uc.tree_view_panel.site_selected.connect(self.highlight_site)
        # Notify the hopping block when the selection changes
        self.uc.selection.signals.updated.connect(
            lambda: self.hopping.set_uc_id(self.uc.selection["unit_cell"])
        )

        right_layout.addWidget(PlaceholderWidget("Computation Options"))
        right_layout.addWidget(PlaceholderWidget("Computation Input"))

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(mid_layout, stretch=5)
        main_layout.addLayout(right_layout, stretch=3)

        self.setCentralWidget(main_view)

    def update_plot(self, unit_cell_id):
        """
        Update the 3D plot with the selected unit cell.
        
        This method is called when a unit cell is selected in the tree view.
        It retrieves the selected unit cell from the model and passes it to the
        3D visualization panel for display.
        
        Args:
            unit_cell_id: UUID of the selected unit cell
        """
        if unit_cell_id in self.uc.unit_cells:
            unit_cell = self.uc.unit_cells[unit_cell_id]
            self.unit_cell_plot.set_unit_cell(unit_cell)
        else:
            # Clear the plot if unit cell doesn't exist
            self.unit_cell_plot.set_unit_cell(None)

    def highlight_site(self, unit_cell_id, site_id):
        """
        Highlight the selected site in the 3D plot.
        
        This method is called when a site is selected in the tree view.
        It first updates the plot to show the correct unit cell, then tells
        the plot to highlight the specific site with a different color.
        
        Args:
            unit_cell_id: UUID of the unit cell containing the site
            site_id: UUID of the site to highlight
        """
        # First update the plot with the current unit cell
        self.update_plot(unit_cell_id)

        # Then highlight the specific site if it exists
        try:
            if unit_cell_id in self.uc.unit_cells:
                unit_cell = self.uc.unit_cells[unit_cell_id]
                if site_id in unit_cell.sites:
                    self.unit_cell_plot.select_site(site_id)
        except Exception as e:
            print(f"Error highlighting site: {e}")


class PlaceholderWidget(QWidget):
    """Placeholder widget with a label to show where future components will go"""

    def __init__(self, name):
        super().__init__()
        self.setAutoFillBackground(True)

        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        # Add a label
        layout = QVBoxLayout(self)
        label = QLabel(f"[{name}]")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


app = QApplication(sys.argv)
window = MainWindow()

window.show()
app.exec()
