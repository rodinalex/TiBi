from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import QSize

import matplotlib.figure as mpl_fig
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)


class PlotView(QWidget):
    """
    Widget for displaying 2D plots.

    This widget creates a matplotlib figure embedded in a Qt widget to display
    data as 2D plots. It includes navigation controls for zooming, panning,
    and saving the plot.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        # Matplotlib Figure
        self.figure = mpl_fig.Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setIconSize(QSize(20, 20))

        # Add widgets to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True)

        # Initial draw
        self.canvas.draw()
