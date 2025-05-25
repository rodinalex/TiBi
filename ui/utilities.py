from PySide6.QtWidgets import QFrame


def divider_line():
    """
    Create a horizontal line to be used as a divider in the UI.

    Returns
    -------
        QFrame
            A horizontal line with a sunken shadow effect."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setFixedHeight(2)
    line.setStyleSheet("color: #888888;")
    return line
