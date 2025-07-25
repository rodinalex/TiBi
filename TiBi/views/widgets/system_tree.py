from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView
import uuid

from TiBi.models import UnitCell


class SystemTree(QTreeView):
    """
    Custom `QTreeViewtree`for displaying `UnitCell`s, `Site`s, and `State`s.

    This tree view is designed to show a hierarchical structure of `UnitCell`s,
    `Site`s, and `State`s. It allows for easy navigation and selection of these
    elements. The tree is built using a `QStandardItemModel`, and each item
    in the tree is represented by a `QStandardItem`. The tree supports
    single selection mode and can be edited by double-clicking on an item.
    The tree view emits a signal when the selection changes, providing
    information about the selected `UnitCell`, `Site`, and `State`.

    Attributes
    ----------
    tree_model : QStandardItemModel
        The model used to populate the tree view.
    root_node : QStandardItem
        The root item of the tree model, representing the tree's top level.
    tree_selection_changed : Signal
        Emitted when the selection in the tree changes. The signal carries
        a dictionary with the selected `UnitCell`, `Site`, and `State` IDs.

    Methods
    -------
    add_tree_item(name, uc_id, site_id=None, state_id=None)
        Add and select a tree item without rebuilding the entire tree.
    find_item_by_id(self, uc_id, site_id=None, state_id=None)
        Find a tree item by its ID.
    refresh_tree(unit_cells: dict[uuid.UUID, UnitCell])
        Rebuilds the entire tree from the current data model.
    remove_tree_item(uc_id, site_id=None, state_id=None)
        Remove an item from the tree.
    """

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

        Note: For better performance, prefer the more specific update methods:
        - `add_tree_item()` - For adding or updating a single node
        - `remove_tree_item()` - For removing a single node

        This full refresh is typically only needed during initialization or
        when multiple components of the tree need to be updated simultaneously.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary of `UnitCells`s to be displayed in the tree.
            The keys are UUIDs and the values are `UnitCell` objects.
        """
        self.tree_model.clear()
        self.root_node = self.tree_model.invisibleRootItem()

        # Add special "add" item at the top
        add_item = QStandardItem("+ Add Unit Cell")
        add_item.setData("ADD_UNIT_CELL", Qt.UserRole)  # Special marker
        add_item.setFlags(Qt.ItemIsEnabled)  # Not selectable, but clickable
        self.root_node.appendRow(add_item)

        # Add unit cells
        for uc_id, unit_cell in unit_cells.items():
            unit_cell_item = self._create_tree_item(
                unit_cell.name, item_id=uc_id
            )
            self.root_node.appendRow(unit_cell_item)

            # Add sites for this unit cell
            for site_id, site in unit_cell.sites.items():
                site_item = self._create_tree_item(site.name, item_id=site_id)
                unit_cell_item.appendRow(site_item)

                # Add states for this site
                for state_id, state in site.states.items():
                    state_item = self._create_tree_item(
                        state.name, item_id=state_id
                    )
                    site_item.appendRow(state_item)

    def _create_tree_item(
        self, item_name: str, item_id: uuid.UUID
    ) -> QStandardItem:
        """
        Create a `QStandardItem` for tree.

        Parameters
        ----------
        item_name : str
            Name of the item.
        item_id : uuid.UUID
            id of the item.

        Returns
        -------
        QStandardItem
            The new tree item.
        """
        tree_item = QStandardItem(item_name)
        tree_item.setData(item_id, Qt.UserRole)  # Store the ID

        # Set other visual properties
        tree_item.setEditable(True)

        return tree_item

    def find_item_by_id(
        self, uc_id, site_id=None, state_id=None
    ) -> QStandardItem | None:
        """
        Find a tree item by its ID.

        Parameters
        ----------
        uc_id : uuid.UUID
            id of the `UnitCell`
        site_id : uuid.UUID, optional
            id of the `Site`
        state_id : uuid.UUID, optional
            id of the `State`

        Returns
        -------
        QStandardItem | None
            The required item if found, `None` otherwise.
        """
        if state_id is not None:
            parent = self.find_item_by_id(uc_id, site_id)
            item_id = state_id
        elif site_id is not None:
            parent = self.find_item_by_id(uc_id)
            item_id = site_id
        else:
            parent = self.root_node
            item_id = uc_id

        for row in range(parent.rowCount()):
            item = parent.child(row)
            if item.data(Qt.UserRole) == item_id:
                return item

    def _select_item_by_id(self, uc_id, site_id=None, state_id=None) -> None:
        """
        Select a tree item programmatically by its ID.

        Parameters
        ----------
        uc_id : uuid.UUID
            id of the `UnitCell`
        site_id : uuid.UUID, optional
            id of the `Site`
        state_id : uuid.UUID, optional
            id of the `State`
        """
        item = self.find_item_by_id(uc_id, site_id, state_id)
        if item:
            index = self.tree_model.indexFromItem(item)
            self.selectionModel().setCurrentIndex(
                index, QItemSelectionModel.ClearAndSelect
            )

    def add_tree_item(self, name, uc_id, site_id=None, state_id=None):
        """
        Add and select a tree item without rebuilding the entire tree.

        Parameters
        ----------
        uc_id : uuid.UUID
            id of the `UnitCell`
        site_id : uuid.UUID, optional
            id of the `Site`
        state_id : uuid.UUID, optional
            id of the `State`
        """
        if state_id is not None:  # Adding a state
            parent = self.find_item_by_id(uc_id, site_id)
            item_id = state_id
        elif site_id is not None:  # Adding a site
            parent = self.find_item_by_id(uc_id)
            item_id = site_id
        else:  # Adding a unit cell
            parent = self.root_node
            item_id = uc_id

        item = self._create_tree_item(name, item_id=item_id)
        parent.appendRow(item)
        index = self.tree_model.indexFromItem(item)
        self.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.ClearAndSelect
        )

    def remove_tree_item(self, uc_id, site_id=None, state_id=None):
        """
        Remove an item from the tree.

        If the item has a parent
        (i.e., is not a `UnitCell`), select the parent. Otherwise,
        clear the selection

        Parameters
        ----------
        uc_id : uuid.UUID
            id of the `UnitCell`
        site_id : uuid.UUID, optional
            id of the `Site`
        state_id : uuid.UUID, optional
            id of the `State`
        """
        item = self.find_item_by_id(uc_id, site_id, state_id)
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

    def _on_tree_selection_changed(self, selected: QStandardItem, deselected):
        """
        Handle the change of selection in the tree.

        This method is called when the user selects a node in the tree view or
        the selection occurs programmatically.
        It determines what type of node was selected
        (unit cell, site, or state) and emits a dictionary with
        the item's id and, if applicable, its parent's/grandparent's id's.
        The dictionary is then used to update the app's selection model.

        Parameters
        ----------
        selected : QStandardItem
            The newly selected item
        deselected : QStandardItem
            The previously selected items that are now deselected
        """
        indexes = selected.indexes()

        if not indexes:
            new_selection = {"unit_cell": None, "site": None, "state": None}
        else:
            # Get the selected item
            index = indexes[0]
            item = self.tree_model.itemFromIndex(index)

            item_id = item.data(Qt.UserRole)

            if item.parent() is None:  # unit cell selected
                new_selection = {
                    "unit_cell": item_id,
                    "site": None,
                    "state": None,
                }
            elif item.parent().parent() is None:  # site selected
                parent_item = item.parent()
                parent_id = parent_item.data(Qt.UserRole)

                new_selection = {
                    "unit_cell": parent_id,
                    "site": item_id,
                    "state": None,
                }
            else:  # state selected
                parent_item = item.parent()
                parent_id = parent_item.data(Qt.UserRole)
                grandparent_item = parent_item.parent()
                grandparent_id = grandparent_item.data(Qt.UserRole)

                new_selection = {
                    "unit_cell": grandparent_id,
                    "site": parent_id,
                    "state": item_id,
                }

        self.tree_selection_changed.emit(new_selection)
