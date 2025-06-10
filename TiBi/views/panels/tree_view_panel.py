from PySide6.QtCore import QEvent, QRect, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QKeySequence,
    QShortcut,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QVBoxLayout, QWidget

from TiBi.ui import get_resource_path
from TiBi.ui.styles import hex_to_rgb, THEME_SETTINGS
from ..widgets import SystemTree


class TreeDelegate(QStyledItemDelegate):
    """
    A delegate that requires the user to commit changes to tree item names by
    pressing "Enter". Clicking away/defocusing resets the tree item name to
    its pre-edit form. The purpose is to handle the Qt default behavior,
    where defocusing keeps the new display name in the tree but does not send
    an updated signal so that the data can be updated internally.
    Additionally, the delegate draws rectangular "Delete" and "Add" buttons
    next to the item names.
    """

    name_edit_finished = Signal(object)  # Emits QModelIndex
    new_unit_cell_requested = Signal()
    new_site_requested = Signal()
    new_state_requested = Signal()
    delete_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editing_index = None
        self.delete_renderer = QSvgRenderer(
            str(get_resource_path("assets/icons/trash.svg"))
        )
        self.add_renderer = QSvgRenderer(
            str(get_resource_path("assets/icons/plus.svg"))
        )
    def _button_rects(self, option, index):
        """Regions defining the item buttons."""
        size = 16
        margin = 4
        right = option.rect.right() - margin

        buttons = {}
        buttons["delete"] = QRect(
            right - size, option.rect.center().y() - size // 2, size, size
        )
        if self._get_item_level(index) < 2:
            buttons["add"] = QRect(
                right - 2 * size - margin,
                option.rect.center().y() - size // 2,
                size,
                size,
            )
        return buttons

    def _get_item_level(self, index):
        """
        Determine the tree level of the item (0=UnitCell, 1=Site, 2=State)
        """
        level = 0
        current = index
        while current.parent().isValid():
            level += 1
            current = current.parent()
        return level

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        editor.setProperty(
            "originalText", index.data()
        )  # Save the original name
        self._editing_index = index
        return editor

    def paint(self, painter, option, index):
        if index.data(Qt.UserRole) == "ADD_UNIT_CELL":
            # Custom paint for "Add Unit Cell" item
            painter.save()
            # Get the full width of the viewport (the whole row)
            tree = self.parent()
            full_rect = QRect(
                0,
                option.rect.y(),
                tree.viewport().width(),
                option.rect.height(),
            )

            # Draw background across the full width
            painter.fillRect(
                full_rect,
                QColor(*hex_to_rgb(THEME_SETTINGS["PRIMARY_HEX"])),
            )

            # Text formatting
            painter.setPen(QColor(*hex_to_rgb(THEME_SETTINGS["ON_PRIMARY"])))
            font = painter.font()
            painter.setFont(font)

            # Adjust text inside the original rect (with padding)
            text_rect = option.rect.adjusted(8, 0, -8, 0)
            painter.drawText(text_rect, Qt.AlignVCenter, "+ Add Unit Cell")

            painter.restore()

        else:
            super().paint(painter, option, index)
            # Only show the delete icon for selected items
            if option.state & QStyle.State_Selected:
                rects = self._button_rects(option, index)
                self.delete_renderer.render(painter, rects["delete"])
                if "add" in rects:
                    # painter.drawPixmap(rects["add"], self.add_icon)
                    self.add_renderer.render(painter, rects["add"])

    def editorEvent(self, event, model, option, index):
        # Handle special "Add Unit Cell" item
        if index.data(Qt.UserRole) == "ADD_UNIT_CELL":
            if event.type() == QEvent.MouseButtonRelease:
                if option.rect.contains(event.pos()):
                    self.new_unit_cell_requested.emit()
                    return True
            return False

        rects = self._button_rects(option, index)

        if event.type() == QEvent.MouseButtonPress:
            # Store whether the item was selected before this click
            self._was_selected_before_click = (
                self.parent().selectionModel().isSelected(index)
            )
            return super().editorEvent(event, model, option, index)

        elif event.type() == QEvent.MouseButtonRelease:
            if rects["delete"].contains(event.pos()):
                # Only trigger delete if the item was already selected
                if self._was_selected_before_click:
                    self.delete_requested.emit()
                    return True
                # If it wasn't selected before, the click selects the item
                return False
            elif ("add" in rects) and rects["add"].contains(event.pos()):
                # Only trigger delete if the item was already selected
                if self._was_selected_before_click:
                    if self._get_item_level(index) == 0:
                        self.new_site_requested.emit()
                    elif self._get_item_level(index) == 1:
                        self.new_state_requested.emit()
                    return True
                return False
        return super().editorEvent(event, model, option, index)

    def eventFilter(self, editor, event):
        if event.type() == QEvent.FocusOut:
            # Restore original text on focus loss (cancel edit)
            editor.blockSignals(True)
            editor.setText(editor.property("originalText"))
            editor.blockSignals(False)
            self.closeEditor.emit(editor, QStyledItemDelegate.RevertModelCache)
            return True

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            # User manually pressed Enter — accept the edit
            self.commitData.emit(editor)
            self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)
            if self._editing_index is not None:
                self.name_edit_finished.emit(self._editing_index)
                self._editing_index = None
            return True

        return super().eventFilter(editor, event)


class TreeViewPanel(QWidget):
    """
    Tree view panel for displaying and selecting the unit cell hierarchy.

    This panel displays a hierarchical tree showing unit cells, their sites,
    and the states at each site. It handles selection events and emits signals
    when different types of nodes are selected, allowing other components to
    respond appropriately.

    The tree has three levels:
    1. Unit cells
    2. Sites within a unit cell
    3. States within a site

    Features:
    - Hierarchical display of unit cells, sites, and states
    - Single selection mode for focused editing
    - Double-click to edit names directly in the tree
    - Keyboard shortcuts for deletion (Del and Backspace)
    - Signal emission on deletion requests

    This panel is designed to work with a controller that will handle the
    data modifications in response to UI actions.
    """

    # Define signals
    name_edit_finished = Signal(object)  # Emits QModelIndex
    new_unit_cell_requested = Signal()
    new_site_requested = Signal()
    new_state_requested = Signal()
    delete_requested = Signal()

    def __init__(self):
        super().__init__()

        # Create and configure tree view
        self.tree_view = SystemTree()
        self.setMaximumWidth(220)

        # Set the delegate to save the data only on Enter-press
        self.delegate = TreeDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)

        # Set up Delete shortcut
        self.delete_shortcut = QShortcut(QKeySequence("Del"), self.tree_view)
        self.delete_shortcut.activated.connect(
            lambda: self.delete_requested.emit()
        )

        # Add Backspace as an alternative shortcut
        self.backspace_shortcut = QShortcut(
            QKeySequence("Backspace"), self.tree_view
        )
        self.backspace_shortcut.activated.connect(
            lambda: self.delete_requested.emit()
        )

        # Relay delegate signals
        self.delegate.delete_requested.connect(
            lambda: QTimer.singleShot(0, lambda: self.delete_requested.emit())
        )
        self.delegate.new_unit_cell_requested.connect(
            lambda: QTimer.singleShot(
                0, lambda: self.new_unit_cell_requested.emit()
            )
        )
        self.delegate.new_site_requested.connect(
            lambda: QTimer.singleShot(
                0, lambda: self.new_site_requested.emit()
            )
        )
        self.delegate.new_state_requested.connect(
            lambda: QTimer.singleShot(
                0, lambda: self.new_state_requested.emit()
            )
        )
        self.delegate.name_edit_finished.connect(
            lambda x: QTimer.singleShot(
                0, lambda x=x: self.name_edit_finished.emit(x)
            )
        )
