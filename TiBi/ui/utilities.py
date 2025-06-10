from pathlib import Path
from PySide6.QtGui import QFontMetrics
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

def set_spinbox_digit_width(spinbox, num_digits):
    """Set spinbox width to accommodate a specific number of digits"""
    # Get font metrics for the spinbox's current font
    font_metrics = QFontMetrics(spinbox.font())
    
    # Calculate width needed for the specified number of digits
    # Using '0' as it's typically one of the wider digits
    digit_width = font_metrics.horizontalAdvance('0' * num_digits)
    
    # Add some padding for margins, borders, and spin buttons
    padding = 10  # Adjust as needed
    total_width = digit_width + padding
    
    spinbox.setFixedWidth(total_width)