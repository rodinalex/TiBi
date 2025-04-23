from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QSize

import matplotlib.figure as mpl_fig
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# from src.band_structure import calculate_bands_along_path, get_special_points


class BandStructurePlotView(QWidget):
    """
    Widget for displaying band structure plots.

    This widget creates a matplotlib figure embedded in a Qt widget to display
    band structure calculations along a path in k-space. It includes controls for
    running calculations and visualization options.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(400, 300))

        # Data
        self.unit_cell = None
        self.bz_path = []
        self.special_point_labels = []
        self.num_points = 100

        # Setup layout
        layout = QVBoxLayout(self)

        # Matplotlib Figure
        self.figure = mpl_fig.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Add widgets to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("k-vector")
        self.ax.set_ylabel("Energy")
        self.ax.grid(True)

        # Initial draw
        self.canvas.draw()
