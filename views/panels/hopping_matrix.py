from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class HoppingMatrix(QWidget):
    """
    A grid of buttons representing possible hopping connections between states.

    Each button in the grid represents a possible hopping between two states.
    The rows (columns) represent the destination (source) states.
    Buttons are colored differently based on whether a hopping exists or not,
    and whether the hopping is Hermitian.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable Area for Matrix
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Content widget for grid
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(3)

        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        title_label = QLabel("Coupling Matrix")
        title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(title_label)
        layout.addWidget(self.scroll_area)
