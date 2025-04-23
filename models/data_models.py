from collections import UserDict
from PySide6.QtCore import QObject, Signal


class DataModelSignals(QObject):
    """
    Signals container for DataModel class.

    Holds the signals that DataModel instances can emit to notify
    observers of changes to the model's data.
    """

    # Signal emitted when the model data changes in any way
    updated = Signal()


class DataModel(UserDict):
    """
    Reactive dictionary model with change notifications.

    Extends Python's UserDict to add signal emission when data changes.
    This allows UI components to reactively update when the model changes.
    Used primarily for storing mappings like state-to-state hoppings.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the model with optional initial data.

        Args:
            *args, **kwargs: Same parameters as dict constructor
        """
        # Initialize signals before the parent constructor to ensure
        # they exist before any data is added
        self.signals = DataModelSignals()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        """
        Set a key-value pair in the dictionary and emit updated signal if changed.

        This method overrides the dictionary's __setitem__ to add signal emission
        when the value for a key changes. It only emits the signal if the new
        value is different from the previous value.

        Args:
            key: The dictionary key
            val: The value to store
        """
        previous = self.get(key)  # Get the existing value if any
        if val != previous:  # Only proceed if there's an actual change
            super().__setitem__(key, val)  # Set the value in the dictionary
            self.signals.updated.emit()  # Notify observers of the change

    def update(self, d):
        """
        Update multiple dictionary values and emit only a single signal if any changed.

        This optimized version of update avoids emitting multiple signals when
        updating multiple values at once. It tracks whether any values actually
        changed and only emits the signal once at the end if needed.

        Args:
            d: Dictionary containing the new key-value pairs to update
        """
        changed = False  # Track if any values were actually changed

        for key, val in d.items():
            previous = self.get(key)  # Get existing value if any
            if val != previous:  # Only update if there's an actual change
                super().__setitem__(key, val)  # Update the value
                changed = True  # Note that at least one value changed

        # Only emit the signal once, and only if something actually changed
        if changed:
            self.signals.updated.emit()


class AlwaysNotifyDataModel(UserDict):
    """
    A variant of DataModel that always emits signals on updates.

    This is particularly useful for array data or complex objects where
    equality comparison is expensive or unreliable.
    """

    def __init__(self, *args, **kwargs):
        self.signals = DataModelSignals()
        self._updating = False  # Flag to track update operation
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        if not self._updating:  # Only emit if not in the middle of an update
            self.signals.updated.emit()

    def update(self, d):
        self._updating = True  # Start update operation
        super().update(d)
        self._updating = False  # End update operation
        self.signals.updated.emit()  # Emit once after all updates
