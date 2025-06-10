from pathlib import Path
from PySide6.QtWidgets import QFrame
import sys


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


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "TiBi" / relative_path
    else:
        tibi_package_dir = Path(
            __file__
        ).parent.parent  # Go up from ui/ to TiBi/
        return tibi_package_dir / relative_path
