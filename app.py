import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
    QLabel,
)
from PySide6.QtGui import QPalette, QColor
from models.uc_models import UCFormModel
from src.tibitypes import UnitCell
from ui.unit_cell_panel import UnitCellPanel
from ui.tree_view import TreeViewPanel

# Data Models
unit_cell_model = UCFormModel(
    name="New Unit Cell",
    v1x=1.0,
    v1y=0.0,
    v1z=0.0,
    v2x=0.0,
    v2y=1.0,
    v2z=0.0,
    v3x=0.0,
    v3y=0.0,
    v3z=1.0,
)

site_model = UCFormModel(name="New Site", c1=0.0, c2=0.0, c3=0.0)
state_model = UCFormModel(name="New State", energy=0.0)

# Unit Cell collection
unit_cells = {}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1000, 800))

        self.unit_cell_panel = UnitCellPanel(unit_cell_model)
        self.tree_view_panel = TreeViewPanel(unit_cells)

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        left_layout.addWidget(Color("red"), stretch=2)
        left_layout.addWidget(self.unit_cell_panel, stretch=1)
        left_layout.addWidget(Color("red"), stretch=1)

        mid_layout.addWidget(Color("red"))
        mid_layout.addWidget(Color("green"))

        right_layout.addWidget(Color("red"))
        right_layout.addWidget(Color("green"))

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(mid_layout, stretch=5)
        main_layout.addLayout(right_layout, stretch=3)

        self.setCentralWidget(main_view)


class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
