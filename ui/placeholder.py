from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


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
