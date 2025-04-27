import uuid
from PySide6.QtCore import QObject, Qt, QModelIndex, QItemSelectionModel, Signal
from PySide6.QtGui import QStandardItem
from src.tibitypes import UnitCell, Site, State, BasisVector
from models.data_models import DataModel
from views.uc_view import UnitCellView
from resources.constants import default_site_size

import random


class UnitCellController(QObject):
    """
    Controller that manages interactions between the UI and data models for unit cells.

    This controller connects UI signals from the form panels and tree view to appropriate
    actions that modify the underlying data models. It handles all CRUD (create, read,
    update, delete) operations for the hierarchy of unit cells, sites, and states.

    The controller follows the MVC (Model-View-Controller) pattern:
    - Models: The unit_cells dictionary and the form panel models
    - Views: The tree view and form panels
    - Controller: This class, which updates models in response to UI events

    After data model changes, the controller updates the tree view and reselects
    the appropriate node to maintain UI state consistency.
    """

    plotUpdateRequested = Signal()

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        unit_cell_data: DataModel,
        site_data: DataModel,
        state_data: DataModel,
        unit_cell_view: UnitCellView,
    ):
        """
        Initialize the controller and connect UI signals to handler methods.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: DataModel tracking the currently selected unit cell, site, and state
            unit_cell_data: DataModel containing the properties of the selected unit cell
            site_data: DataModel containing the properties of the selected site
            state_data: DataModel containing the properties of the selected state
            unit_cell_view: The main view component containing tree view and form panels
        """
        super().__init__()
        # Store references to UI components and data models
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_data = unit_cell_data
        self.site_data = site_data
        self.state_data = state_data
        self.unit_cell_view = unit_cell_view

        # Get the fields from unit_cell_view for convenience
        # For the basis vectors, each reference has three spinboxes
        self.v1 = self.unit_cell_view.unit_cell_panel.v1
        self.v2 = self.unit_cell_view.unit_cell_panel.v2
        self.v3 = self.unit_cell_view.unit_cell_panel.v3

        self.n1 = self.unit_cell_view.unit_cell_panel.n1
        self.n2 = self.unit_cell_view.unit_cell_panel.n2
        self.n3 = self.unit_cell_view.unit_cell_panel.n3

        self.R = self.unit_cell_view.site_panel.R
        self.c1 = self.unit_cell_view.site_panel.c1
        self.c2 = self.unit_cell_view.site_panel.c2
        self.c3 = self.unit_cell_view.site_panel.c3
        # Rebuild the tree view from scratch in the beginning
        self._refresh_tree()

        # Sync UI with data models
        self._update_unit_cell_ui()
        self._update_site_ui()

        # Connect signals

        # Tree view signals
        self.unit_cell_view.tree_view_panel.tree_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self.unit_cell_view.tree_view_panel.tree_model.itemChanged.connect(
            self._on_item_changed
        )
        self.unit_cell_view.tree_view_panel.delete.connect(self._delete_item)

        # Unit Cell panel signals
        def connect_vector_fields(vector_name, spinboxes):
            for ii, axis in enumerate("xyz"):
                spinboxes[ii].editingFinished.connect(
                    lambda ii=ii, axis=axis: self._update_unit_cell_data(
                        f"{vector_name}{axis}", spinboxes[ii].value()
                    )
                )

        connect_vector_fields("v1", self.v1)
        connect_vector_fields("v2", self.v2)
        connect_vector_fields("v3", self.v3)

        # Site panel signals

        self.R.editingFinished.connect(lambda: self._update_site_size())

        self.c1.editingFinished.connect(
            lambda: self._update_site_data("c1", self.c1.value())
        )
        self.c2.editingFinished.connect(
            lambda: self._update_site_data("c2", self.c2.value())
        )
        self.c3.editingFinished.connect(
            lambda: self._update_site_data("c3", self.c3.value())
        )

        # Dimensionality radio buttons
        self.unit_cell_view.unit_cell_panel.radio0D.toggled.connect(
            self._dimensionality_change
        )
        self.unit_cell_view.unit_cell_panel.radio1D.toggled.connect(
            self._dimensionality_change
        )
        self.unit_cell_view.unit_cell_panel.radio2D.toggled.connect(
            self._dimensionality_change
        )
        self.unit_cell_view.unit_cell_panel.radio3D.toggled.connect(
            self._dimensionality_change
        )

        # Button panel signals
        self.unit_cell_view.tree_view_panel.new_uc_btn.clicked.connect(
            self._add_unit_cell
        )
        self.unit_cell_view.unit_cell_panel.new_site_btn.clicked.connect(self._add_site)
        self.unit_cell_view.site_panel.new_state_btn.clicked.connect(self._add_state)
        self.unit_cell_view.tree_view_panel.delete_btn.clicked.connect(
            self._delete_item
        )
        self.unit_cell_view.unit_cell_panel.reduce_btn.clicked.connect(
            self._reduce_uc_basis
        )
        # Selection change
        self.selection.signals.updated.connect(self._show_panels)

        # # When model changes, update UI
        self.unit_cell_data.signals.updated.connect(self._update_unit_cell_ui)
        self.site_data.signals.updated.connect(self._update_site_ui)

    # Tree Navigation Functions
    def _refresh_tree(self):
        """
        Rebuild the entire tree from the current data model.

        This method clears the existing tree and reconstructs it based on the
        current state of the unit_cells dictionary. It creates a hierarchical
        structure with three levels: unit cells, sites, and states.

        Each node in the tree stores the corresponding object, type, and UUID
        as user data, allowing for easy retrieval during selection events.

        Note: For better performance, prefer the more specific update methods:
        - _update_tree_item() - For adding or updating a single node
        - _remove_tree_item() - For removing a single node

        This full refresh is typically only needed during initialization or when
        multiple components of the tree need to be updated simultaneously.
        """
        self.unit_cell_view.tree_view_panel.tree_model.clear()
        self.root_node = (
            self.unit_cell_view.tree_view_panel.tree_model.invisibleRootItem()
        )

        # Add unit cells
        for uc_id, unit_cell in self.unit_cells.items():
            unit_cell_item = self._create_tree_item(
                unit_cell, item_type="unit_cell", item_id=uc_id
            )
            self.root_node.appendRow(unit_cell_item)

            # Add sites for this unit cell
            for site_id, site in unit_cell.sites.items():
                site_item = self._create_tree_item(
                    site, item_type="site", item_id=site_id
                )
                unit_cell_item.appendRow(site_item)

                # Add states for this site
                for state_id, state in site.states.items():
                    state_item = self._create_tree_item(
                        state, item_type="state", item_id=state_id
                    )
                    site_item.appendRow(state_item)

    def _find_item_by_id(self, item_id, item_type, parent_id=None, grandparent_id=None):
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
            parent = self.unit_cell_view.tree_view_panel.tree_model.invisibleRootItem()
        elif item_type == "site":
            parent = self._find_item_by_id(parent_id, "unit_cell")
        else:
            parent = self._find_item_by_id(parent_id, "site", grandparent_id)

        for row in range(parent.rowCount()):
            item = parent.child(row)
            if item.data(Qt.UserRole + 2) == item_id:
                return item

    def _update_tree_item(self, uc_id, site_id=None, state_id=None):
        """
        Update or add a tree item without rebuilding the entire tree.
        The item to update is determined from the number of id arguments provided.

        Args:
            uc_id: UUID of the unit cell
            site_id: UUID of the site
            state_id: UUID of the state
        """
        if state_id is not None:  # Adding/updating a state
            # Get the parent site
            parent = self._find_item_by_id(site_id, "site", uc_id)
            # Assign the meta data for the state
            item_type, item_id = "state", state_id
            # Find the item in the tree
            item = self._find_item_by_id(state_id, item_type, site_id, uc_id)
            # Get the state object from the unit cell list
            data = self.unit_cells[uc_id].sites[site_id].states[state_id]
        elif site_id is not None:  # Adding/updating a site
            # Get the parent unit cell
            parent = self._find_item_by_id(uc_id, "unit_cell")
            # Assign the meta data for the site
            item_type, item_id = "site", site_id
            # Find the item in the tree
            item = self._find_item_by_id(site_id, item_type, uc_id)
            # Get the site object from the unit cell list
            data = self.unit_cells[uc_id].sites[site_id]
        else:  # Adding/updating a unit cell
            # The parent is the root node
            parent = self.root_node
            # Assign the meta data for the unit cell
            item_type, item_id = "unit_cell", uc_id
            # Find the item in the tree
            item = self._find_item_by_id(uc_id, item_type)
            # Get the unit cell object from the unit cell list
            data = self.unit_cells[uc_id]

        if item:  # If the item exists, update it
            item.setText(data.name)
            item.setData(data, Qt.UserRole)
        else:  # Otherwise, create a new item and insert it into the tree
            item = self._create_tree_item(data, item_type=item_type, item_id=item_id)
            parent.appendRow(item)

    def _remove_tree_item(self, uc_id, site_id=None, state_id=None):
        """
        Remove an item from the tree.

        Args:
            uc_id: UUID of the grandparent unit cell
            site_id: UUID of the parent site
            state_id: UUID of the state to remove
        """
        if state_id is not None:  # Removing a state
            parent = self._find_item_by_id(site_id, "site", uc_id)
            item = self._find_item_by_id(state_id, "state", site_id, uc_id)
        elif site_id is not None:  # Removing a site
            parent = self._find_item_by_id(uc_id, "unit_cell")
            item = self._find_item_by_id(site_id, "site", uc_id)
        else:  # Removing a unit cell
            parent = self.root_node
            item = self._find_item_by_id(uc_id, "unit_cell")

        parent.removeRow(item.row())

    def _create_tree_item(self, item, item_type, item_id):
        """Create a QStandardItem for tree with metadata"""
        tree_item = QStandardItem(item.name)
        tree_item.setData(item, Qt.UserRole)  # Store the actual data object
        tree_item.setData(item_type, Qt.UserRole + 1)  # Store the type
        tree_item.setData(item_id, Qt.UserRole + 2)  # Store the ID

        # Set other visual properties
        tree_item.setEditable(True)

        return tree_item

    def _on_selection_changed(self, selected, deselected):
        """
        Handle tree item selection events and emit appropriate signals.

        This method is called when the user selects a node in the tree view.
        It determines what type of node was selected (unit cell, site, or state)
        and updates the selection model with the item's id and, if applicable,
        its parent's/grandparent's id's. After the relevant id's are saved, a request
        to update unit cell and Brollouin zone plots is emitted.

        Args:
            selected: The newly selected items
            deselected: The previously selected items that are now deselected
        """
        indexes = selected.indexes()
        if not indexes:
            self.selection.update({"unit_cell": None, "site": None, "state": None})
            return

        # Get the selected item
        index = indexes[0]
        item = self.unit_cell_view.tree_view_panel.tree_model.itemFromIndex(index)

        item_type = item.data(Qt.UserRole + 1)
        item_id = item.data(Qt.UserRole + 2)

        if item_type == "unit_cell":  # unit cell selected
            self.selection.update({"unit_cell": item_id, "site": None, "state": None})
        else:  # site or state selected
            parent_item = item.parent()
            parent_id = parent_item.data(Qt.UserRole + 2)
            if item_type == "site":  # site selected
                self.selection.update(
                    {"unit_cell": parent_id, "site": item_id, "state": None}
                )
            else:  # state selected
                grandparent_item = parent_item.parent()
                grandparent_id = grandparent_item.data(Qt.UserRole + 2)
                self.selection.update(
                    {"unit_cell": grandparent_id, "site": parent_id, "state": item_id}
                )
            size_param = self.unit_cells[self.selection["unit_cell"]].site_sizes[
                self.selection["site"]
            ]
            self.R.setValue(size_param)

        # Now that selection is fully updated, request plot update
        self.plotUpdateRequested.emit()

    # Programmatically select a tree item
    def _select_item(self, item_id, item_type, parent_id=None, grandparent_id=None):
        """
        Select a tree item by its ID and type.

        This method programmatically selects an item in the tree view, which triggers
        the selection changed signal and updates the form panels to display the item's
        properties. It's used after operations like adding or modifying items to ensure
        the UI reflects the current state.

        The method handles the hierarchical nature of the tree view, using parent and
        grandparent IDs to locate items at different nesting levels. After the selection,
        a request to update unit cell and Brollouin zone plots is emitted.

        Args:
            item_id: UUID of the item to find
            item_type: Type of the item ("unit_cell", "site", or "state")
            parent_id: UUID of the parent item (for site or state)
            grandparent_id: UUID of the grandparent item (for state)
        """
        if item_type == "unit_cell":
            parent = self.root_node
        elif item_type == "site":
            parent = self._find_item_by_id(parent_id, "unit_cell")
        else:
            parent = self._find_item_by_id(parent_id, "site", grandparent_id)

        for row in range(parent.rowCount()):
            item = parent.child(row)
            if item.data(Qt.UserRole + 2) == item_id:
                index = self.unit_cell_view.tree_view_panel.tree_model.indexFromItem(
                    item
                )
                self.unit_cell_view.tree_view_panel.tree_view.selectionModel().setCurrentIndex(
                    index, QItemSelectionModel.ClearAndSelect
                )
                return

    def _on_item_changed(self, item: QStandardItem):
        """
        Change the name of the selected item by double-clicking on it in the tree view.
        Update the data and save it.
        """
        item_type = item.data(Qt.UserRole + 1)
        new_name = item.text()
        if item_type == "unit_cell":
            self.unit_cell_data["name"] = new_name
            self._save_unit_cell()
        elif item_type == "site":
            self.site_data["name"] = new_name
            self._save_site()
        else:
            self.state_data["name"] = new_name
            self._save_state()

    # Unit Cell/Site/State Modification Functions

    def _add_unit_cell(self):
        """
        Create a new unit cell with default properties and add it to the model.

        Creates a unit cell with orthogonal basis vectors along the x, y, and z axes,
        adds it to the unit_cells dictionary, and selects it in the tree view.

        The default unit cell has:
        - Name: "New Unit Cell"
        - Three orthogonal unit vectors along the x, y, and z axes
        - No periodicity (0D system)
        - No sites or states initially

        After creation, the tree view is updated and the new unit cell is automatically
        selected so the user can immediately edit its properties.
        """
        name = "New Unit Cell"
        v1 = BasisVector(1, 0, 0)  # Unit vector along x-axis
        v2 = BasisVector(0, 1, 0)  # Unit vector along y-axis
        v3 = BasisVector(0, 0, 1)  # Unit vector along z-axis

        # Create and store the new unit cell
        new_cell = UnitCell(name, v1, v2, v3)
        self.unit_cells[new_cell.id] = new_cell
        # Update UI (selective update instead of full refresh)
        self._update_tree_item(new_cell.id)
        self._select_item(new_cell.id, "unit_cell")

    def _add_site(self):
        """
        Create a new site in the currently selected unit cell.

        Creates a site with default name and coordinates (0,0,0), adds it to the
        sites dictionary of the selected unit cell, and selects it in the tree view.
        """
        # Create a new site with default properties
        name = "New Site"
        c1 = 0  # Fractional coordinate along first basis vector
        c2 = 0  # Fractional coordinate along second basis vector
        c3 = 0  # Fractional coordinate along third basis vector
        new_site = Site(name, c1, c2, c3)

        # Add the site to the selected unit cell
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]
        current_uc.sites[new_site.id] = new_site
        current_uc.site_colors[new_site.id] = (
            random.randrange(256),
            random.randrange(256),
            random.randrange(256),
            1.0,
        )
        current_uc.site_sizes[new_site.id] = default_site_size

        # Update UI (selective update instead of full refresh)
        self._update_tree_item(selected_uc_id, new_site.id)
        self._select_item(new_site.id, "site", selected_uc_id)

    def _add_state(self):
        """
        Create a new quantum state in the currently selected site.

        Creates a state with default name, adds it to the
        states dictionary of the selected site, and selects it in the tree view.
        """
        # Create a new state with default properties
        name = "New State"
        new_state = State(name)

        # Add the state to the selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_site.states[new_state.id] = new_state

        # Update UI (selective update instead of full refresh)
        self._update_tree_item(selected_uc_id, selected_site_id, new_state.id)
        self._select_item(new_state.id, "state", selected_site_id, selected_uc_id)

    def _save_unit_cell(self):
        """
        Save changes from the unit cell data model to the selected unit cell.

        This method is automatically triggered when the unit_cell_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        After saving, the tree view is updated to show any changes (like renamed items).
        """
        # Get the currently selected unit cell
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]

        # Update name and basic properties
        current_uc.name = self.unit_cell_data["name"]

        # Update first basis vector (v1)
        current_uc.v1.x = float(self.unit_cell_data["v1x"])
        current_uc.v1.y = float(self.unit_cell_data["v1y"])
        current_uc.v1.z = float(self.unit_cell_data["v1z"])
        current_uc.v1.is_periodic = self.unit_cell_data["v1periodic"]

        # Update second basis vector (v2)
        current_uc.v2.x = float(self.unit_cell_data["v2x"])
        current_uc.v2.y = float(self.unit_cell_data["v2y"])
        current_uc.v2.z = float(self.unit_cell_data["v2z"])
        current_uc.v2.is_periodic = self.unit_cell_data["v2periodic"]

        # Update third basis vector (v3)
        current_uc.v3.x = float(self.unit_cell_data["v3x"])
        current_uc.v3.y = float(self.unit_cell_data["v3y"])
        current_uc.v3.z = float(self.unit_cell_data["v3z"])
        current_uc.v3.is_periodic = self.unit_cell_data["v3periodic"]

        # Update UI (selective update instead of full refresh)
        self._update_tree_item(selected_uc_id)

        # After unit cell object is updated, notify plot controllers
        self.plotUpdateRequested.emit()

    def _save_site(self):
        """
        Save changes from the site data model to the selected site.

        This method is automatically triggered when the site_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        After saving, the tree view is updated to show any changes (like renamed items).
        """
        # Get the currently selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]

        # Update site properties
        current_site.name = self.site_data["name"]
        current_site.c1 = float(self.site_data["c1"])
        current_site.c2 = float(self.site_data["c2"])
        current_site.c3 = float(self.site_data["c3"])

        # Update UI (selective update instead of full refresh)
        self._update_tree_item(selected_uc_id, selected_site_id)

        # After site object is updated, notify plot controllers
        self.plotUpdateRequested.emit()

    def _save_state(self):
        """
        Save changes from the state data model to the selected state.

        This method is automatically triggered when the site_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        After saving, the tree view is updated to show any changes (like renamed items).
        """
        # Get the currently selected state
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_state = current_site.states[selected_state_id]

        # Update state properties
        current_state.name = self.state_data["name"]

        # Update UI (selective update instead of full refresh)
        self._update_tree_item(selected_uc_id, selected_site_id, selected_state_id)

    def _delete_item(self):
        """
        Delete the currently selected item from the model.

        This method handles deletion of unit cells, sites, and states based on the
        current selection. It updates both the data model and the tree view to reflect
        the deletion, and ensures that the selection is updated appropriately.

        The deletion follows the containment hierarchy:
        - Deleting a unit cell also removes all its sites and states
        - Deleting a site also removes all its states
        - Deleting a state only removes that specific state

        After deletion, the parent item is selected (or nothing if a unit cell was deleted).
        At the end, a request to update unit cell and Brillouin zone plots is emitted.
        """
        selected_uc_id = self.selection.get("unit_cell", None)
        selected_site_id = self.selection.get("site", None)
        selected_state_id = self.selection.get("state", None)

        # Check if there is a selected unit cell
        if selected_uc_id:
            # Check if there a selected site
            if selected_site_id:
                # Check if there is a selected state
                if selected_state_id:
                    # Delete the selected state from the site
                    del (
                        self.unit_cells[selected_uc_id]
                        .sites[selected_site_id]
                        .states[selected_state_id]
                    )
                    # Update UI and select the parent site (selective removal instead of full refresh)
                    self._remove_tree_item(
                        selected_uc_id, selected_site_id, selected_state_id
                    )
                    self._select_item(selected_site_id, "site", selected_uc_id)
                else:
                    # No state selected, therefore remove the site from the unit cell
                    del self.unit_cells[selected_uc_id].sites[selected_site_id]

                    # Update UI and select the parent unit cell (selective removal instead of full refresh)
                    self._remove_tree_item(selected_uc_id, selected_site_id)
                    self._select_item(selected_uc_id, "unit_cell")

            else:
                # No site selected, therefore remove the unit cell from the model
                del self.unit_cells[selected_uc_id]

                # Update UI (selective removal instead of full refresh)
                self._remove_tree_item(selected_uc_id)

                # Clear selection explicitly
                self.unit_cell_view.tree_view_panel.tree_view.selectionModel().clearSelection()
                self.unit_cell_view.tree_view_panel.tree_view.setCurrentIndex(
                    QModelIndex()
                )  # Clear the cursor/visual highlight
                self.selection.update({"unit_cell": None, "site": None, "state": None})
        self.plotUpdateRequested.emit()

    def _reduce_uc_basis(self):
        """
        Reduce the basis vectors of the selected unit cell using the LLL algorithm.

        This method applies the Lenstra-Lenstra-Lovász (LLL) lattice reduction algorithm
        to find a more orthogonal set of basis vectors that spans the same lattice.
        This is useful for finding a 'nicer' representation of the unit cell with
        basis vectors that are shorter and more orthogonal to each other.

        The method only affects the periodic directions of the unit cell. After
        reduction, the UI is updated to reflect the new basis vectors.
        """
        selected_uc_id = self.selection.get("unit_cell", None)
        if selected_uc_id:
            uc = self.unit_cells[selected_uc_id]
            reduced_basis = uc.reduced_basis()

            # Run a model update
            v1 = reduced_basis[0]
            v2 = reduced_basis[1]
            v3 = reduced_basis[2]
            self.unit_cell_data.update(
                {
                    "v1x": v1.x,
                    "v1y": v1.y,
                    "v1z": v1.z,
                    "v2x": v2.x,
                    "v2y": v2.y,
                    "v2z": v2.z,
                    "v3x": v3.x,
                    "v3y": v3.y,
                    "v3z": v3.z,
                }
            )
            self._save_unit_cell()

    def _show_panels(self):
        """
        Update the UI panels based on the current selection state.

        This method is called whenever the selection changes. It determines which
        panels should be visible and populates them with data from the selected items.
        The panels are shown or hidden using a stacked widget approach.

        The method handles all three levels of the hierarchy:
        - When a unit cell is selected, its properties are shown in the unit cell panel
        - When a site is selected, its properties are shown in the site panel
        - When a state is selected, no additional panel is shown as the state is only
        described by its name

        Appropriate buttons are also enabled/disabled based on the selection context.
        """
        unit_cell_id = self.selection.get("unit_cell", None)
        site_id = self.selection.get("site", None)
        state_id = self.selection.get("state", None)
        if unit_cell_id:
            # Get the selected unit cell
            uc = self.unit_cells[unit_cell_id]
            # Update the form model with all unit cell properties
            # The form will automatically update due to the reactive data binding
            self.unit_cell_data.update(
                {
                    "name": uc.name,
                    "v1x": uc.v1.x,
                    "v1y": uc.v1.y,
                    "v1z": uc.v1.z,
                    "v2x": uc.v2.x,
                    "v2y": uc.v2.y,
                    "v2z": uc.v2.z,
                    "v3x": uc.v3.x,
                    "v3y": uc.v3.y,
                    "v3z": uc.v3.z,
                    "v1periodic": uc.v1.is_periodic,
                    "v2periodic": uc.v2.is_periodic,
                    "v3periodic": uc.v3.is_periodic,
                }
            )
            dim = uc.v1.is_periodic + uc.v2.is_periodic + uc.v3.is_periodic
            self.unit_cell_view.unit_cell_panel.radio_group.button(dim).setChecked(True)
            self.unit_cell_view.uc_stack.setCurrentWidget(
                self.unit_cell_view.unit_cell_panel
            )

            if site_id:
                site = uc.sites[site_id]
                # Update the form model with all site properties
                # The corresponding update function to update the fields is fired automatically.
                self.site_data.update(
                    {
                        "name": site.name,
                        "c1": site.c1,
                        "c2": site.c2,
                        "c3": site.c3,
                    }
                )
                self.unit_cell_view.site_stack.setCurrentWidget(
                    self.unit_cell_view.site_panel
                )
                if state_id:
                    state = site.states[state_id]

                    # Update the form model with the state properties
                    # The corresponding update function to update the fields is fired automatically.
                    self.state_data.update(
                        {
                            "name": state.name,
                        }
                    )
            else:
                self.unit_cell_view.site_stack.setCurrentWidget(
                    self.unit_cell_view.site_info_label
                )
        else:
            self.unit_cell_view.uc_stack.setCurrentWidget(
                self.unit_cell_view.uc_info_label
            )

    def _dimensionality_change(self):
        """
        Handle changes in the dimensionality selection (0D, 1D, 2D, 3D).

        This method is called when the user selects a different dimensionality radio button.
        It updates the unit cell's periodicity flags and enables/disables appropriate
        basis vector components based on the selected dimensionality.

        For example:
        - 0D: All directions are non-periodic (isolated system)
        - 1D: First direction is periodic, others are not
        - 2D: First and second directions are periodic, third is not
        - 3D: All directions are periodic (fully periodic crystal)
        """
        btn = self.sender()
        if btn.isChecked():
            selected_dim = btn.text()
            if selected_dim == "0":
                self.v1[0].setEnabled(True)
                self.v1[1].setEnabled(False)
                self.v1[2].setEnabled(False)

                self.v2[0].setEnabled(False)
                self.v2[1].setEnabled(True)
                self.v2[2].setEnabled(False)

                self.v3[0].setEnabled(False)
                self.v3[1].setEnabled(False)
                self.v3[2].setEnabled(True)

                self.unit_cell_data.update(
                    {
                        "v1x": 1.0,
                        "v1y": 0.0,
                        "v1z": 0.0,
                        "v2x": 0.0,
                        "v2y": 1.0,
                        "v2z": 0.0,
                        "v3x": 0.0,
                        "v3y": 0.0,
                        "v3z": 1.0,
                        "v1periodic": False,
                        "v2periodic": False,
                        "v3periodic": False,
                    }
                )
                self.n1.setEnabled(False)
                self.n2.setEnabled(False)
                self.n3.setEnabled(False)

            elif selected_dim == "1":
                self.v1[0].setEnabled(True)
                self.v1[1].setEnabled(False)
                self.v1[2].setEnabled(False)

                self.v2[0].setEnabled(False)
                self.v2[1].setEnabled(True)
                self.v2[2].setEnabled(False)

                self.v3[0].setEnabled(False)
                self.v3[1].setEnabled(False)
                self.v3[2].setEnabled(True)

                self.unit_cell_data.update(
                    {
                        # "v1x": 1.0,
                        "v1y": 0.0,
                        "v1z": 0.0,
                        "v2x": 0.0,
                        # "v2y": 1.0,
                        "v2z": 0.0,
                        "v3x": 0.0,
                        "v3y": 0.0,
                        # "v3z": 1.0,
                        "v1periodic": True,
                        "v2periodic": False,
                        "v3periodic": False,
                    }
                )
                self.n1.setEnabled(True)
                self.n2.setEnabled(False)
                self.n3.setEnabled(False)

            elif selected_dim == "2":
                self.v1[0].setEnabled(True)
                self.v1[1].setEnabled(True)
                self.v1[2].setEnabled(False)

                self.v2[0].setEnabled(True)
                self.v2[1].setEnabled(True)
                self.v2[2].setEnabled(False)

                self.v3[0].setEnabled(False)
                self.v3[1].setEnabled(False)
                self.v3[2].setEnabled(True)

                self.unit_cell_data.update(
                    {
                        # "v1x": 1.0,
                        # "v1y": 0.0,
                        "v1z": 0.0,
                        # "v2x": 0.0,
                        # "v2y": 1.0,
                        "v2z": 0.0,
                        "v3x": 0.0,
                        "v3y": 0.0,
                        # "v3z": 1.0,
                        "v1periodic": True,
                        "v2periodic": True,
                        "v3periodic": False,
                    }
                )
                self.n1.setEnabled(True)
                self.n2.setEnabled(True)
                self.n3.setEnabled(False)

            elif selected_dim == "3":
                self.v1[0].setEnabled(True)
                self.v1[1].setEnabled(True)
                self.v1[2].setEnabled(True)

                self.v2[0].setEnabled(True)
                self.v2[1].setEnabled(True)
                self.v2[2].setEnabled(True)

                self.v3[0].setEnabled(True)
                self.v3[1].setEnabled(True)
                self.v3[2].setEnabled(True)

                self.unit_cell_data.update(
                    {
                        # "v1x": 1.0,
                        # "v1y": 0.0,
                        # "v1z": 0.0,
                        # "v2x": 0.0,
                        # "v2y": 1.0,
                        # "v2z": 0.0,
                        # "v3x": 0.0,
                        # "v3y": 0.0,
                        # "v3z": 1.0,
                        "v1periodic": True,
                        "v2periodic": True,
                        "v3periodic": True,
                    }
                )
                self.n1.setEnabled(True)
                self.n2.setEnabled(True)
                self.n3.setEnabled(True)
            self._save_unit_cell()

    def _update_unit_cell_data(self, key, value):
        """
        Update the unit cell data model with new values.

        This method is called when the user edits a property in the unit cell form panel.
        It updates the reactive data model, which will trigger a signal that causes the
        _save_unit_cell method to update the actual UnitCell object. This separation
        allows for validation and coalescing of multiple changes.

        Args:
            key: The property name to update (e.g., "v1x", "v2y", "name")
            value: The new value for the property
        """
        self.unit_cell_data[key] = value
        self._save_unit_cell()

    def _update_site_data(self, key, value):
        """
        Update the site data model with new values.

        This method is called when the user edits a property in the site form panel.
        It updates the reactive data model, which will trigger a signal that causes the
        _save_site method to update the actual Site object. This separation
        allows for validation and coalescing of multiple changes.

        Args:
            key: The property name to update (e.g., "c1", "name")
            value: The new value for the property
        """
        self.site_data[key] = value
        self._save_site()

    def _update_unit_cell_ui(self):
        """
        Update the UI with the current unit cell data.
        This method sets the values of the spinboxes in the unit cell panel
        based on the current values in the unit_cell_data dictionary.
        """

        self.v1[0].setValue(self.unit_cell_data["v1x"])
        self.v1[1].setValue(self.unit_cell_data["v1y"])
        self.v1[2].setValue(self.unit_cell_data["v1z"])

        self.v2[0].setValue(self.unit_cell_data["v2x"])
        self.v2[1].setValue(self.unit_cell_data["v2y"])
        self.v2[2].setValue(self.unit_cell_data["v2z"])

        self.v3[0].setValue(self.unit_cell_data["v3x"])
        self.v3[1].setValue(self.unit_cell_data["v3y"])
        self.v3[2].setValue(self.unit_cell_data["v3z"])

    def _update_site_ui(self):
        """
        Update the UI with the current site data.
        This method sets the values of the spinboxes in the site panel
        based on the current values in the site_data dictionary.
        """

        self.c1.setValue(self.site_data["c1"])
        self.c2.setValue(self.site_data["c2"])
        self.c3.setValue(self.site_data["c3"])

    def _update_site_size(self):
        """
        Update the size of the site marker. First, the data from the
        spinbox is saved to the dictionary of sizes. Next, an update
        is requested.
        """
        self.unit_cells[self.selection["unit_cell"]].site_sizes[
            self.selection["site"]
        ] = self.R.value()
        self.plotUpdateRequested.emit()
