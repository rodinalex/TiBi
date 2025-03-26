from collections import UserDict
from PySide6.QtCore import QObject, Signal


# Signals that Data Models emit
class DataModelSignals(QObject):
    updated = Signal()


# Models for form fields
class UCFormModel(UserDict):
    # Initialize as a regular dictionary + data signals
    def __init__(self, *args, **kwargs):
        self.signals = DataModelSignals()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        previous = self.get(key)  # Get the existing value.
        super().__setitem__(key, val)  # Set the value.
        if val != previous:  # There is a change.
            self.signals.updated.emit()  # Emit the signal.
            # print(f"Setting {key} to {val}")
