from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QProgressBar
from PySide6.QtCore import Signal


class ProgressDialog(QDialog):
    """
    A modal that displays a progress bar and a cancel button.

    Attributes
    ----------
    cancel_requested : Signal
        Signal emitted when the cancel button is clicked.

    Methods
    -------
    update_progress(value: int)
        Updates the progress bar with the given value.
    """

    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Working...")
        self.setModal(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def update_progress(self, value: int):
        """
        Update the progress bar with the given value.
        """
        self.progress_bar.setValue(value)
