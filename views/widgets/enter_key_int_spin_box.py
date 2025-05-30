import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSpinBox


class EnterKeyIntSpinBox(QSpinBox):
    """
    Custom `QSpinBox` that emits a signal when the Enter key is pressed.

    On defocus, the value is reset to the original value and no signal
    is emitted.
    """

    editingConfirmed = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_value = self.value()

    def focusInEvent(self, event):
        self._original_value = self.value()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        # Revert to original value on focus out
        self.blockSignals(True)
        self.setValue(self._original_value)
        self.blockSignals(False)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            # Emit signal only if the value has changed
            if not np.isclose(self.value(), self._original_value):
                self._original_value = self.value()
                self.editingConfirmed.emit()
        elif event.key() == Qt.Key_Escape:
            self.blockSignals(True)
            self.setValue(self._original_value)
            self.blockSignals(False)
        else:
            super().keyPressEvent(event)
