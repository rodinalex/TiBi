from collections import UserDict
from PySide6.QtCore import QObject, Signal
from typing import Tuple
from src.tibitypes import State
import numpy as np


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

    def update(self, d):
        """Update multiple values and emit the signal only once"""
        for key, val in d.items():
            previous = self.get(key)
            super().__setitem__(key, val)

        # Emit the signal once after all updates
        self.signals.updated.emit()


# # Model for state coupling
# class StateCoupling(UserDict):
#     # Initialize as a regular dictionary + data signals
#     def __init__(self, *args, **kwargs):
#         self.signals = DataModelSignals()
#         super().__init__(*args, **kwargs)

#     def __setitem__(self, key: Tuple[State, State], amps: list[np.complex128]):
#         s1, s2 = key
#         previous = self.get(key, [])  # Get the existing value.
#         super().__setitem__((s1, s2), amps)
#         super().__setitem__((s2, s1), [np.conj(x) for x in amps])
#         if amps != previous:
#             self.signals.updated.emit()
