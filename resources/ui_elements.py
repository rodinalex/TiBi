from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFrame, QTreeView
import uuid

from src.tibitypes import UnitCell


def divider_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setFixedHeight(2)
    line.setStyleSheet("color: #888888;")
    return line


class SystemTree(QTreeView):

    tree_selection_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setEditTriggers(QTreeView.DoubleClicked)

        # Create model
        self.tree_model = QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()

        # Set model to view
        self.setModel(self.tree_model)

        # Internal signals
        self.selectionModel().selectionChanged.connect(
            self._on_tree_selection_changed
        )

    def refresh_tree(self, unit_cells: dict[uuid.UUID, UnitCell]):
        """
        Rebuild the entire tree from the current data model.

        This method clears the existing tree and reconstructs it based on the
        current state of the unit_cells dictionary. It creates a hierarchical
        structure with three levels: unit cells, sites, and states.

        Each node in the tree stores the corresponding object, type, and UUID
        as user data, allowing for easy retrieval during selection events.

        Note: For better performance, prefer the more specific update methods:
        - _add_tree_item() - For adding or updating a single node
        - _remove_tree_item() - For removing a single node

        This full refresh is typically only needed during initialization or
        when multiple components of the tree need to be updated simultaneously.
        """
        self.tree_model.clear()
        self.root_node = self.tree_model.invisibleRootItem()

        # Add unit cells
        for uc_id, unit_cell in unit_cells.items():
            unit_cell_item = self._create_tree_item(
                unit_cell.name, item_type="unit_cell", item_id=uc_id
            )
            self.root_node.appendRow(unit_cell_item)

            # Add sites for this unit cell
            for site_id, site in unit_cell.sites.items():
                site_item = self._create_tree_item(
                    site.name, item_type="site", item_id=site_id
                )
                unit_cell_item.appendRow(site_item)

                # Add states for this site
                for state_id, state in site.states.items():
                    state_item = self._create_tree_item(
                        state.name, item_type="state", item_id=state_id
                    )
                    site_item.appendRow(state_item)

    def _create_tree_item(
        self, item_name: str, item_type: str, item_id: uuid.UUID
    ) -> QStandardItem:
        """
        Create a QStandardItem for tree with metadata

        Args:
            item_name: name of the item
            item_type: item type ("unit_cell", "site", or "state")
            item_id: UUID of the item
        """
        tree_item = QStandardItem(item_name)
        tree_item.setData(item_type, Qt.UserRole + 1)  # Store the type
        tree_item.setData(item_id, Qt.UserRole + 2)  # Store the ID

        # Set other visual properties
        tree_item.setEditable(True)

        return tree_item

    def _find_item_by_id(
        self, uc_id, site_id=None, state_id=None
    ) -> QStandardItem | None:
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
        if state_id is not None:
            parent = self._find_item_by_id(uc_id, site_id)
            item_id = state_id
        elif site_id is not None:
            parent = self._find_item_by_id(uc_id)
            item_id = site_id
        else:
            parent = self.root_node
            item_id = uc_id

        for row in range(parent.rowCount()):
            item = parent.child(row)
            if item.data(Qt.UserRole + 2) == item_id:
                return item

    def _add_tree_item(self, name, uc_id, site_id=None, state_id=None):
        """
        Add a tree item without rebuilding the entire tree.
        Select the item after the addition.

        Args:
            uc_id: UUID of the unit cell
            site_id: UUID of the site
            state_id: UUID of the state
        """
        if state_id is not None:  # Adding a state
            parent = self._find_item_by_id(uc_id, site_id)
            item_type, item_id = "state", state_id
        elif site_id is not None:  # Adding a site
            parent = self._find_item_by_id(uc_id)
            item_type, item_id = "site", site_id
        else:  # Adding a unit cell
            parent = self.root_node
            item_type, item_id = "unit_cell", uc_id

        item = self._create_tree_item(
            name, item_type=item_type, item_id=item_id
        )
        parent.appendRow(item)
        index = self.tree_model.indexFromItem(item)
        self.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.ClearAndSelect
        )

    def _remove_tree_item(self, uc_id, site_id=None, state_id=None):
        """
        Remove an item from the tree. If the item has a parent
        (i.e., is not a UnitCell), select the parent. Otherwise,
        clear the selection

        Args:
            uc_id: UUID of the grandparent unit cell
            site_id: UUID of the parent site
            state_id: UUID of the state to remove
        """
        item = self._find_item_by_id(uc_id, site_id, state_id)
        if item:
            # If the item is a unit cell, the parent is None, so we
            # default to the invisibleRootItem
            parent = item.parent() or self.root_node
            # If the item has a parent, select it
            if item.parent():
                index = self.tree_model.indexFromItem(parent)
                self.selectionModel().setCurrentIndex(
                    index, QItemSelectionModel.ClearAndSelect
                )
            # Otherwise, deselect everything (the item is a unit cell)
            else:
                self.selectionModel().clearSelection()
                self.setCurrentIndex(QModelIndex())
            # Delete the item
            parent.removeRow(item.row())

    def _on_tree_selection_changed(self, selected, deselected):
        """
        Handle the change of selection in the tree.

        This method is called when the user selects a node in the tree view or
        the selection occurs programmatically.
        It determines what type of node was selected
        (unit cell, site, or state) and emits a dictionary with
        the item's id and, if applicable, its parent's/grandparent's id's.
        The dictionary is then used to update the app's selection model.

        Args:
            selected: The newly selected items
            deselected: The previously selected items that are now deselected
        """
        indexes = selected.indexes()

        if not indexes:
            new_selection = {"unit_cell": None, "site": None, "state": None}
        else:
            # Get the selected item
            index = indexes[0]
            item = self.tree_model.itemFromIndex(index)

            item_type = item.data(Qt.UserRole + 1)
            item_id = item.data(Qt.UserRole + 2)

            if item_type == "unit_cell":  # unit cell selected
                new_selection = {
                    "unit_cell": item_id,
                    "site": None,
                    "state": None,
                }
            else:  # site or state selected
                parent_item = item.parent()
                parent_id = parent_item.data(Qt.UserRole + 2)

                if item_type == "site":  # site selected
                    new_selection = {
                        "unit_cell": parent_id,
                        "site": item_id,
                        "state": None,
                    }

                else:  # state selected
                    grandparent_item = parent_item.parent()
                    grandparent_id = grandparent_item.data(Qt.UserRole + 2)
                    new_selection = {
                        "unit_cell": grandparent_id,
                        "site": parent_id,
                        "state": item_id,
                    }
        self.tree_selection_changed.emit(new_selection)
