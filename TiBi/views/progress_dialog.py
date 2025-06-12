from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QProgressBar
from PySide6.QtCore import Signal


class ProgressDialog(QDialog):
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Working...")
        self.setModal(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
