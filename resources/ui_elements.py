from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QFrame, QTreeView


def divider_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setFixedHeight(2)
    line.setStyleSheet("color: #888888;")
    return line


class SystemTree(QTreeView):

    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setEditTriggers(QTreeView.DoubleClicked)

        # Create model
        self.tree_model = QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()

        # # Set model to view
        # self.tree_view.setModel(self.tree_model)

        # # Set the delegate to save the data only on Enter-press
        # delegate = EnterOnlyDelegate(self.tree_view)
        # self.tree_view.setItemDelegate(delegate)

        # button_layout = QHBoxLayout()
        # self.new_uc_btn = QPushButton("+ UC")
        # self.delete_btn = QPushButton("Delete")

        # button_layout.addWidget(self.new_uc_btn)
        # button_layout.addWidget(self.delete_btn)

        # # Layout
        # layout = QVBoxLayout(self)
        # layout.addWidget(self.tree_view)
        # layout.addLayout(button_layout)

        # # Set up Delete shortcut
        # self.delete_shortcut = QShortcut(QKeySequence("Del"), self.tree_view)
        # self.delete_shortcut.activated.connect(
        #     lambda: self.delete_requested.emit()
        # )

        # # Add Backspace as an alternative shortcut
        # self.backspace_shortcut = QShortcut(
        #     QKeySequence("Backspace"), self.tree_view
        # )
        # self.backspace_shortcut.activated.connect(
        #     lambda: self.delete_requested.emit()
        # )
