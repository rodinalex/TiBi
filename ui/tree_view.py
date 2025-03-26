from PySide6.QtWidgets import QWidget, QTreeView, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from src.tibitypes import UnitCell
import uuid


def convert_to_node(d):
    new_item = QStandardItem(d.name)
    new_item.setData(d, Qt.UserRole)


class TreeViewPanel(QWidget):
    def __init__(self, l: dict[uuid.UUID, UnitCell]):
        super().__init__()

        tree_view = QTreeView()
        tree_view.setHeaderHidden(True)

        tree_model = QStandardItemModel()
        root_node = tree_model.invisibleRootItem()

        layout = QVBoxLayout(self)
        layout.addWidget(tree_view)
