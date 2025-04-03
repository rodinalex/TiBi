from collections import UserDict, UserList
from PySide6.QtCore import QObject, Signal
from typing import Tuple
from src.tibitypes import State
import numpy as np


# Signals that Data Models emit
class DataModelSignals(QObject):
    updated = Signal()


# General Data Model used for storing dataclasses as dictionaries.
# Emits a signal when updated to trigger synchronization
class DataModel(UserDict):
    # Initialize as a regular dictionary + data signals
    def __init__(self, *args, **kwargs):
        self.signals = DataModelSignals()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        previous = self.get(key)  # Get the existing value.
        if val != previous:  # There is a change.
            super().__setitem__(key, val)  # Set the value.
            self.signals.updated.emit()  # Emit the signal.

    def update(self, d):
        """Update multiple values and emit the signal only once"""
        changed = False
        for key, val in d.items():
            previous = self.get(key)
            if val != previous:
                super().__setitem__(key, val)
                changed = True  # Track if anything changed
        if changed:
            self.signals.updated.emit()


class ListModelSignals(QObject):
    updated = Signal()


# General List Mode used for storing data
# Emits a signal when updated to trigger synchronization
class ListModel(UserList):
    def __init__(self, *args):
        self.signals = ListModelSignals()
        super().__init__(*args)

    def append(self, item):
        super().append(item)
        print("Signal emitted!")  # Debugging
        self.signals.updated.emit()

    def extend(self, iterable):
        super().extend(iterable)
        self.signals.updated.emit()

    def insert(self, index, item):
        super().insert(index, item)
        self.signals.updated.emit()

    def remove(self, item):
        super().remove(item)
        self.signals.updated.emit()

    def pop(self, index=-1):
        item = super().pop(index)
        self.signals.updated.emit()
        return item  # Ensure pop still returns the removed element

    def clear(self):
        super().clear()
        self.signals.updated.emit()

    def __setitem__(self, index, item):
        if self[index] != item:
            super().__setitem__(index, item)
            self.signals.updated.emit()

    def __delitem__(self, index):
        super().__delitem__(index)
        self.signals.updated.emit()

    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        self.signals.updated.emit()

    def reverse(self):
        super().reverse()
        self.signals.updated.emit()
