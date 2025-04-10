from PySide6.QtWidgets import (
    QWidget,
    QTreeView,
    QVBoxLayout,
    QPushButton,
    QToolBar,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QShortcut
from PySide6.QtCore import Qt, Signal, QItemSelectionModel
from src.tibitypes import UnitCell
import uuid


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
    """

    # Define signals
    selection_changed_signal = Signal(object, object, object)

    unit_cell_delete = Signal()
    site_delete = Signal()
    state_delete = Signal()

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        unit_cell_model,
        site_model,
        state_model,
    ):
        super().__init__()

        self.unit_cells = unit_cells
        self.unit_cell_model = unit_cell_model
        self.site_model = site_model
        self.state_model = state_model

        # Create and configure tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setEditTriggers(QTreeView.DoubleClicked)

        # Create model
        self.tree_model = QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()
        self.tree_model.itemChanged.connect(self.on_item_changed)

        # Set model to view
        self.tree_view.setModel(self.tree_model)

        # Add unit cell button
        self.add_unit_cell_btn = QPushButton("Add Unit Cell")

        # Layout setup
        layout = QVBoxLayout(self)
        # layout.addWidget(QLabel("Project Structure"))
        layout.addWidget(self.tree_view)
        layout.addWidget(self.add_unit_cell_btn)

        # Connect signals
        self.tree_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )
        # Set up delete shortcut
        self.delete_shortcut = QShortcut(QKeySequence("Del"), self.tree_view)
        self.delete_shortcut.activated.connect(self.handle_delete_key)

        # Optional: Add Backspace as an alternative shortcut
        self.backspace_shortcut = QShortcut(QKeySequence("Backspace"), self.tree_view)
        self.backspace_shortcut.activated.connect(self.handle_delete_key)

        # Initial render
        self.refresh_tree()

    def refresh_tree(self):
        """
        Rebuild the entire tree from the current data model.

        This method clears the existing tree and reconstructs it based on the
        current state of the unit_cells dictionary. It creates a hierarchical
        structure with three levels: unit cells, sites, and states.

        Each node in the tree stores the corresponding object, type, and UUID
        as user data, allowing for easy retrieval during selection events.

        Note: For better performance, prefer the more specific update methods:
        - update_tree_item()
        - remove_tree_ite ()
        """
        self.tree_model.clear()
        self.root_node = self.tree_model.invisibleRootItem()

        # Add unit cells
        for uc_id, unit_cell in self.unit_cells.items():
            unit_cell_item = self.create_tree_item(
                unit_cell, item_type="unit_cell", item_id=uc_id
            )
            self.root_node.appendRow(unit_cell_item)

            # Add sites for this unit cell
            for site_id, site in unit_cell.sites.items():
                site_item = self.create_tree_item(
                    site, item_type="site", item_id=site_id
                )
                unit_cell_item.appendRow(site_item)

                # Add states for this site
                for state_id, state in site.states.items():
                    state_item = self.create_tree_item(
                        state, item_type="state", item_id=state_id
                    )
                    site_item.appendRow(state_item)

    def find_item_by_id(self, item_id, item_type, parent_id=None, grandparent_id=None):
        """
        Find a tree item by its ID and type.

        Args:
            item_id: UUID of the item to find
            item_type: Type of the item ("unit_cell", "site", or "state")
            parent_id: UUID of the parent item (for site or state)
            grandparent_id: UUID of the grandparent item (for state)

        Returns:
            The QStandardItem if found, None otherwise
        """
        if item_type == "unit_cell":
            parent = self.root_node
        elif item_type == "site":
            parent = self.find_item_by_id(parent_id, "unit_cell")
        else:
            parent = self.find_item_by_id(parent_id, "site", grandparent_id)

        for row in range(parent.rowCount()):
            item = parent.child(row)
            if item.data(Qt.UserRole + 2) == item_id:
                return item

    def update_tree_item(self, uc_id, site_id=None, state_id=None):
        """
        Update or add a tree item without rebuilding the entire tree.

        Args:
            uc_id: UUID of the grandparent unit cell
            site_id: UUID of the parent site
            state_id: UUID of the state to update
        """
        if state_id is not None:
            parent = self.find_item_by_id(site_id, "site", uc_id)
            item_type, item_id = "state", state_id
            item = self.find_item_by_id(state_id, item_type, site_id, uc_id)
            data = self.unit_cells[uc_id].sites[site_id].states[state_id]
        elif site_id is not None:
            parent = self.find_item_by_id(uc_id, "unit_cell")
            item_type, item_id = "site", site_id
            item = self.find_item_by_id(site_id, item_type, uc_id)
            data = self.unit_cells[uc_id].sites[site_id]
        else:
            parent = self.root_node
            item_type, item_id = "unit_cell", uc_id
            item = self.find_item_by_id(uc_id, item_type)
            data = self.unit_cells[uc_id]

        if item:
            item.setText(data.name)
            item.setData(data, Qt.UserRole)
        else:
            item = self.create_tree_item(data, item_type=item_type, item_id=item_id)
            parent.appendRow(item)

    def remove_tree_item(self, uc_id, site_id=None, state_id=None):
        """
        Remove an item from the tree.

        Args:
            uc_id: UUID of the grandparent unit cell
            site_id: UUID of the parent site
            state_id: UUID of the state to remove
        """
        if state_id is not None:
            parent = self.find_item_by_id(site_id, "site", uc_id)
            item = self.find_item_by_id(state_id, "state", site_id, uc_id)
        elif site_id is not None:
            parent = self.find_item_by_id(uc_id, "unit_cell")
            item = self.find_item_by_id(site_id, "site", uc_id)
        else:
            parent = self.root_node
            item = self.find_item_by_id(uc_id, "unit_cell")

        parent.removeRow(item.row())

    def create_tree_item(self, item, item_type, item_id):
        """Create a QStandardItem for tree with metadata"""
        tree_item = QStandardItem(item.name)
        tree_item.setData(item, Qt.UserRole)  # Store the actual data object
        tree_item.setData(item_type, Qt.UserRole + 1)  # Store the type
        tree_item.setData(item_id, Qt.UserRole + 2)  # Store the ID

        # Set other visual properties
        tree_item.setEditable(True)

        return tree_item

    # Determine which node is being selected and fire the appropriate Signal
    def on_selection_changed(self, selected, deselected):
        """
        Handle tree item selection events and emit appropriate signals.

        This method is called when the user selects a node in the tree view.
        It determines what type of node was selected (unit cell, site, or state)
        and emits the corresponding signal with the relevant IDs.

        For site and state selections, it retrieves the parent and grandparent
        IDs to provide the complete context of the selection.

        Args:
            selected: The newly selected items
            deselected: The previously selected items that are now deselected
        """
        indexes = selected.indexes()
        if not indexes:
            self.selection_changed_signal.emit(None, None, None)
            return

        # Get the selected item
        index = indexes[0]
        item = self.tree_model.itemFromIndex(index)

        item_type = item.data(Qt.UserRole + 1)
        item_id = item.data(Qt.UserRole + 2)

        if item_type == "unit_cell":
            self.selection_changed_signal.emit(item_id, None, None)
        else:
            parent_item = item.parent()
            parent_id = parent_item.data(Qt.UserRole + 2)
            if item_type == "site":
                self.selection_changed_signal.emit(parent_id, item_id, None)
            else:  # "state" selected
                grandparent_item = parent_item.parent()
                grandparent_id = grandparent_item.data(Qt.UserRole + 2)
                self.selection_changed_signal.emit(grandparent_id, parent_id, item_id)

    # Programmatically select a tree item
    def select_item(self, item_id, item_type, parent_id=None, grandparent_id=None):
        """
        Select a tree item by its ID and type.

        Args:
            item_id: UUID of the item to find
            item_type: Type of the item ("unit_cell", "site", or "state")
            parent_id: UUID of the parent item (for site or state)
            grandparent_id: UUID of the grandparent item (for state)

        Returns:
            Nothing
        """
        if item_type == "unit_cell":
            parent = self.root_node
            self.selection_changed_signal.emit(item_id, None, None)
        elif item_type == "site":
            parent = self.find_item_by_id(parent_id, "unit_cell")
            self.selection_changed_signal.emit(parent_id, item_id, None)
        else:
            parent = self.find_item_by_id(parent_id, "site", grandparent_id)
            self.selection_changed_signal.emit(grandparent_id, parent_id, item_id)
        for row in range(parent.rowCount()):
            item = parent.child(row)
            if item.data(Qt.UserRole + 2) == item_id:
                index = self.tree_model.indexFromItem(item)
                self.tree_view.selectionModel().setCurrentIndex(
                    index, QItemSelectionModel.ClearAndSelect
                )
                return

    def on_item_changed(self, item: QStandardItem):
        """
        Change the name of the selected item by double-clicking on it in the tree view.
        """
        item_type = item.data(Qt.UserRole + 1)
        new_name = item.text()
        if item_type == "unit_cell":
            self.unit_cell_model["name"] = new_name
        elif item_type == "site":
            self.site_model["name"] = new_name
        else:
            self.state_model["name"] = new_name

    def handle_delete_key(self):
        """
        Handle Delete/Backspace key press to remove selected item
        """
        # Get the current selection
        indexes = self.tree_view.selectionModel().selectedIndexes()
        if not indexes:
            return

        # Get the selected item
        index = indexes[0]
        item = self.tree_model.itemFromIndex(index)

        # Get item metadata
        item_type = item.data(Qt.UserRole + 1)

        # Handle deletion based on item type
        if item_type == "unit_cell":
            self.unit_cell_delete.emit()
        elif item_type == "site":
            self.site_delete.emit()
        elif item_type == "state":
            self.state_delete.emit()
