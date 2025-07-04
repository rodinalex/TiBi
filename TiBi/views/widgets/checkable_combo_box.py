from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox


class CheckableComboBox(QComboBox):
    """
    Drop-down box that supports multiple selections.

    Selected items are denoted by ticks.

    Attributes
    ----------
    selection_changed : Signal(object)
        Emitted when the selection changes. Even if multiple items
        are selected/deselected, the signal is emitted once. The signal
        carries a list of indices of the selected items.

    Methods
    -------
    checked_items
        Get the indices of the selected items.
    clear_selection
        Deselect all items.
    refresh_combo(list[str])
        Reset the menu with a new list of items.
    select_all
        Select all items.
    """

    selection_changed = Signal(object)

    def __init__(self):
        super().__init__()
        # Create model
        self.combo_model = QStandardItemModel()
        # Set model to view
        self.setModel(self.combo_model)
        self.combo_model.itemChanged.connect(
            lambda _: self.selection_changed.emit(self.checked_items())
        )

    def refresh_combo(self, items: list[str]):
        """
        Reset the combo box with a new list of items.

        Parameters
        ----------
        items : list[str]
            New list of items to be added to the menu.
        """
        self.combo_model.clear()
        for idx in range(len(items)):
            # for text in items:
            text = items[idx]
            item = QStandardItem(text)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Checked, Qt.CheckStateRole)
            item.setData(idx, Qt.UserRole)
            self.combo_model.appendRow(item)
        self.selection_changed.emit(self.checked_items())

    def checked_items(self):
        """
        Get the indices of the selected items.

        Returns
        -------
        result : list[int]
            List of indices of selected items
        """
        result = []
        for ii in range(self.combo_model.rowCount()):
            item = self.combo_model.item(ii)
            if item.checkState() == Qt.Checked:
                result.append(item.data(Qt.UserRole))
        return result

    def clear_selection(self):
        """
        Deselect all items.
        """
        self.combo_model.blockSignals(True)
        for ii in range(self.combo_model.rowCount()):
            item = self.combo_model.item(ii)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.combo_model.blockSignals(False)
        self.selection_changed.emit(self.checked_items())

    def select_all(self):
        """
        Select all items.
        """
        self.combo_model.blockSignals(True)
        for ii in range(self.combo_model.rowCount()):
            item = self.combo_model.item(ii)
            item.setData(Qt.Checked, Qt.CheckStateRole)
        self.combo_model.blockSignals(False)
        self.selection_changed.emit(self.checked_items())
