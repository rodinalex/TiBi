from PySide6.QtWidgets import QFrame


def divider_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setFixedHeight(2)  # Optional: make it thin
    line.setStyleSheet("color: #888888;")  # Optional: customize color
    return line
