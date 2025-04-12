from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
)


class ButtonPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.new_uc_btn = QPushButton("New UC")
        self.new_site_btn = QPushButton("New Site")
        self.new_state_btn = QPushButton("New State")

        self.delete_btn = QPushButton("Delete")

        self.reduce_btn = QPushButton("Reduce UC")

        self.new_site_btn.setEnabled(False)
        self.new_state_btn.setEnabled(False)
        self.reduce_btn.setEnabled(False)

        layout.addWidget(self.new_uc_btn)
        layout.addWidget(self.new_site_btn)
        layout.addWidget(self.new_state_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.reduce_btn)
