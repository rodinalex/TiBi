from PySide6.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QFrame, QGridLayout
from PySide6.QtCore import Qt


class HoppingMatrix(QWidget):
    def __init__(self):
        super().__init__()

        matrix_layout = QVBoxLayout(self)

        # Scrollable Area for Matrix
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Content widget for grid
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(3)

        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        matrix_layout.addWidget(self.scroll_area)
