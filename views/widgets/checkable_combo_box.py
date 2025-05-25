from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox


class CheckableComboBox(QComboBox):

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
        result = []
        for ii in range(self.combo_model.rowCount()):
            item = self.combo_model.item(ii)
            if item.checkState() == Qt.Checked:
                result.append(item.data(Qt.UserRole))
        return result

    def clear_selection(self):
        self.combo_model.blockSignals(True)
        for ii in range(self.combo_model.rowCount()):
            item = self.combo_model.item(ii)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.combo_model.blockSignals(False)
        self.selection_changed.emit(self.checked_items())

    def select_all(self):
        self.combo_model.blockSignals(True)
        for ii in range(self.combo_model.rowCount()):
            item = self.combo_model.item(ii)
            item.setData(Qt.Checked, Qt.CheckStateRole)
        self.combo_model.blockSignals(False)
        self.selection_changed.emit(self.checked_items())
