from PySide6.QtGui import QGuiApplication
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


def mm_to_pixels(mm: float) -> int:
    """
    Convert millimeters to pixels.

    The conversion takes into account the screen resolution of the device.

    Parameters
    ----------
    mm : float
        Length in millimiters.

    Returns
    -------
    int
        Length in pixels.
    """
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    return int((mm / 25.4) * dpi)
