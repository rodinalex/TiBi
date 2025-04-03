from PySide6.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, Signal, QItemSelectionModel
from src.tibitypes import UnitCell
import uuid


class TreeViewPanel(QWidget):
    # Define signals
    none_selected = Signal()
    unit_cell_selected = Signal(uuid.UUID)
    site_selected = Signal(uuid.UUID, uuid.UUID)  # unit_cell_id, site_id
    state_selected = Signal(
        uuid.UUID, uuid.UUID, uuid.UUID
    )  # unit_cell_id, site_id, state_id

    def __init__(self, unit_cells: dict[uuid.UUID, UnitCell]):
        super().__init__()

        self.unit_cells = unit_cells

        # Create and configure tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)

        # Create model
        self.tree_model = QStandardItemModel()
        self.root_node = self.tree_model.invisibleRootItem()

        # Set model to view
        self.tree_view.setModel(self.tree_model)

        # Add unit cell button
        self.add_unit_cell_btn = QPushButton("Add Unit Cell")

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Project Structure"))
        layout.addWidget(self.tree_view)
        layout.addWidget(self.add_unit_cell_btn)

        # Connect signals
        self.tree_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # Initial render
        self.refresh_tree()

    def refresh_tree(self):
        """Rebuild the tree from the current data model"""
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

    def create_tree_item(self, item, item_type, item_id):
        """Create a QStandardItem for tree with metadata"""
        tree_item = QStandardItem(item.name)
        tree_item.setData(item, Qt.UserRole)  # Store the actual data object
        tree_item.setData(item_type, Qt.UserRole + 1)  # Store the type
        tree_item.setData(item_id, Qt.UserRole + 2)  # Store the ID

        # Set other visual properties
        tree_item.setEditable(False)

        return tree_item

    # Determine which node is being selected and fire the appropriate Signal
    def on_selection_changed(self, selected, deselected):
        """Handle tree item selection"""
        indexes = selected.indexes()
        if not indexes:
            self.none_selected.emit()
            return

        # Get the selected item
        index = indexes[0]
        item = self.tree_model.itemFromIndex(index)

        item_type = item.data(Qt.UserRole + 1)
        item_id = item.data(Qt.UserRole + 2)

        # Get parent IDs if needed
        if item_type == "site" or item_type == "state":
            parent_item = item.parent()
            parent_id = parent_item.data(Qt.UserRole + 2)

            if item_type == "state":
                grandparent_item = parent_item.parent()
                grandparent_id = grandparent_item.data(Qt.UserRole + 2)
                self.state_selected.emit(grandparent_id, parent_id, item_id)
            else:  # site
                self.site_selected.emit(parent_id, item_id)
        else:  # unit_cell
            self.unit_cell_selected.emit(item_id)

    # Programmatically select a unit cell--useful when deleting or addint items
    def select_unit_cell(self, unit_cell_id):
        """Selects a unit cell by its ID after tree refresh"""
        for row in range(self.root_node.rowCount()):
            item = self.root_node.child(row)
            if item.data(Qt.UserRole + 2) == unit_cell_id:
                index = item.index()
                self.tree_view.setCurrentIndex(index)
                return

    # Programmatically select a site cell--useful when deleting or addint items
    def select_site(self, unit_cell_id, site_id):
        """Select a site in the tree view."""
        for row in range(self.root_node.rowCount()):
            unit_cell_item = self.root_node.child(row)
            if unit_cell_item.data(Qt.UserRole + 2) == unit_cell_id:
                # Found the unit cell, now search for the site
                for site_row in range(unit_cell_item.rowCount()):
                    site_item = unit_cell_item.child(site_row)
                    if site_item.data(Qt.UserRole + 2) == site_id:
                        # Select this site
                        index = self.tree_model.indexFromItem(site_item)
                        self.tree_view.selectionModel().setCurrentIndex(
                            index, QItemSelectionModel.ClearAndSelect
                        )
                        return  # Stop after selecting

    # Programmatically select a state --useful when deleting or addint items
    def select_state(self, unit_cell_id, site_id, state_id):
        """Select a state in the tree view."""
        for row in range(self.root_node.rowCount()):
            unit_cell_item = self.root_node.child(row)
            if unit_cell_item.data(Qt.UserRole + 2) == unit_cell_id:
                # Found the unit cell, now search for the site
                for site_row in range(unit_cell_item.rowCount()):
                    site_item = unit_cell_item.child(site_row)
                    if site_item.data(Qt.UserRole + 2) == site_id:
                        # Found the site, now search for the state
                        for state_row in range(site_item.rowCount()):
                            state_item = site_item.child(state_row)
                            if state_item.data(Qt.UserRole + 2) == state_id:
                                # Select this state
                                index = self.tree_model.indexFromItem(state_item)
                                self.tree_view.selectionModel().setCurrentIndex(
                                    index, QItemSelectionModel.ClearAndSelect
                                )
                                return  # Stop after selecting
