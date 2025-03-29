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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1200, 900))  # Slightly wider to accommodate 3D plot

        # Initialize UI panels
        self.uc = UnitCellUI()

        # Initialize the plot
        self.unit_cell_plot = UnitCellPlot()

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left column for hierarchical view and form panels
        left_layout.addWidget(self.uc)

        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=1)

        # Connect signals to update the plot when unit cell or site is selected
        self.uc.tree_view_panel.unit_cell_selected.connect(self.update_plot)
        self.uc.tree_view_panel.site_selected.connect(self.highlight_site)

        # Placeholder for hopping parameters (to be implemented later)
        mid_layout.addWidget(PlaceholderWidget("Hopping Parameters"), stretch=1)

        right_layout.addWidget(PlaceholderWidget("Computation Options"))
        right_layout.addWidget(PlaceholderWidget("Computation Input"))

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(mid_layout, stretch=5)
        main_layout.addLayout(right_layout, stretch=3)

        self.setCentralWidget(main_view)

    def update_plot(self, unit_cell_id):
        """Update the 3D plot with the selected unit cell"""
        if unit_cell_id in self.uc.controller.model:
            unit_cell = self.uc.controller.model[unit_cell_id]
            self.unit_cell_plot.set_unit_cell(unit_cell)

    def highlight_site(self, unit_cell_id, site_id):
        """Highlight the selected site in the 3D plot"""
        # First update the plot with the current unit cell
        self.update_plot(unit_cell_id)
        # Then highlight the specific site
        self.unit_cell_plot.select_site(site_id)


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
