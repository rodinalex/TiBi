import uuid
from PySide6.QtCore import QObject, Qt, QModelIndex, QItemSelectionModel
from PySide6.QtGui import QStandardItem
from src.tibitypes import UnitCell, Site, State, BasisVector
from models.data_models import DataModel
from views.uc import UnitCellView


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
            unit_cell_panel: Panel for editing unit cell properties
            site_panel: Panel for editing site properties
            state_panel: Panel for editing state properties
            tree_view: Tree view displaying the hierarchy of unit cells, sites, and states
            selection: DataModel tracking the currently selected items
        """
        super().__init__()
        # Store references to UI components and data models
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_data = unit_cell_data
        self.site_data = site_data
        self.state_data = state_data
        self.unit_cell_view = unit_cell_view
        # Add a reference to the tree view's root node for easy access
        self.root_node = (
            self.unit_cell_view.tree_view_panel.tree_model.invisibleRootItem()
        )
        # Rebuild the tree view from scratch in the beginning
        self.refresh_tree()
        # Connect signals
        # Tree view signals

        # Unit Cell panel signalas

        # Site panel signales
        # self.tree_view.selectionModel().selectionChanged.connect(
        # self.on_selection_changed
        # )
        # self.tree_model.itemChanged.connect(self.on_item_changed)

        # Conenct signals to handlers

        # Connect UI signals to appropriate handler methods
        # Tree view signals
        # self.tree_view.delete.connect(self.delete_item)

        # Button panel signals
        self.unit_cell_view.button_panel.new_uc_btn.clicked.connect(self.add_unit_cell)
        self.unit_cell_view.button_panel.new_site_btn.clicked.connect(self.add_site)
        self.unit_cell_view.button_panel.new_state_btn.clicked.connect(self.add_state)
        # self.unit_cell_view.button_panel.delete_btn.clicked.connect(self.delete_item)
        # self.unit_cell_view.button_panel.reduce_btn.clicked.connect(
        #     self.reduce_uc_basis
        # )

    # Tree Navigation Functions
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
        self.unit_cell_view.tree_view_panel.tree_model.clear()
        self.root_node = (
            self.unit_cell_view.tree_view_panel.tree_model.invisibleRootItem()
        )

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
            parent = self.unit_cell_view.tree_view_panel.tree_model.invisibleRootItem()
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
        if state_id is not None:  # Adding/updating a state
            # Get the parent site
            parent = self.find_item_by_id(site_id, "site", uc_id)
            # Assign the meta data for the state
            item_type, item_id = "state", state_id
            # Find the item in the tree
            item = self.find_item_by_id(state_id, item_type, site_id, uc_id)
            # Get the state object from the unit cell list
            data = self.unit_cells[uc_id].sites[site_id].states[state_id]
        elif site_id is not None:  # Adding/updating a site
            # Get the parent unit cell
            parent = self.find_item_by_id(uc_id, "unit_cell")
            # Assign the meta data for the site
            item_type, item_id = "site", site_id
            # Find the item in the tree
            item = self.find_item_by_id(site_id, item_type, uc_id)
            # Get the site object from the unit cell list
            data = self.unit_cells[uc_id].sites[site_id]
        else:  # Adding/updating a unit cell
            # The parent is the root node
            parent = self.root_node
            # Assign the meta data for the unit cell
            item_type, item_id = "unit_cell", uc_id
            # Find the item in the tree
            item = self.find_item_by_id(uc_id, item_type)
            # Get the unit cell object from the unit cell list
            data = self.unit_cells[uc_id]

        if item:  # If the item exists, update it
            item.setText(data.name)
            item.setData(data, Qt.UserRole)
        else:  # Otherwise, create a new item and insert it into the tree
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
        if state_id is not None:  # Removing a state
            parent = self.find_item_by_id(site_id, "site", uc_id)
            item = self.find_item_by_id(state_id, "state", site_id, uc_id)
        elif site_id is not None:  # Removing a site
            parent = self.find_item_by_id(uc_id, "unit_cell")
            item = self.find_item_by_id(site_id, "site", uc_id)
        else:  # Removing a unit cell
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
            self.selection.update({"unit_cell": item_id, "site": None, "state": None})
        elif item_type == "site":
            parent = self.find_item_by_id(parent_id, "unit_cell")
            self.selection.update(
                {"unit_cell": parent_id, "site": item_id, "state": None}
            )
        else:
            parent = self.find_item_by_id(parent_id, "site", grandparent_id)
            self.selection.update(
                {"unit_cell": grandparent_id, "site": parent_id, "state": item_id}
            )
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

    def on_item_changed(self, item: QStandardItem):
        """
        Change the name of the selected item by double-clicking on it in the tree view.
        """
        item_type = item.data(Qt.UserRole + 1)
        new_name = item.text()
        if item_type == "unit_cell":
            self.unit_cell_data["name"] = new_name
        elif item_type == "site":
            self.site_data["name"] = new_name
        else:
            self.state_data["name"] = new_name

    # Unit Cell/Site/State Modification Functions

    def add_unit_cell(self):
        """
        Create a new unit cell with default properties and add it to the model.

        Creates a unit cell with orthogonal basis vectors along the x, y, and z axes,
        adds it to the unit_cells dictionary, and selects it in the tree view.
        """
        name = "New Unit Cell"
        v1 = BasisVector(1, 0, 0)  # Unit vector along x-axis
        v2 = BasisVector(0, 1, 0)  # Unit vector along y-axis
        v3 = BasisVector(0, 0, 1)  # Unit vector along z-axis

        # Create and store the new unit cell
        new_cell = UnitCell(name, v1, v2, v3)
        self.unit_cells[new_cell.id] = new_cell
        # Update UI (selective update instead of full refresh)
        # self.refresh_tree()
        self.update_tree_item(new_cell.id)
        self.select_item(new_cell.id, "unit_cell")

    def add_site(self):
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

        # Update UI (selective update instead of full refresh)
        self.update_tree_item(selected_uc_id, new_site.id)
        self.select_item(new_site.id, "site", selected_uc_id)

    def add_state(self):
        """
        Create a new quantum state in the currently selected site.

        Creates a state with default name and zero energy, adds it to the
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
        self.update_tree_item(selected_uc_id, selected_site_id, new_state.id)
        self.select_item(new_state.id, "state", selected_site_id, selected_uc_id)

    # # Save data whenever the models register an update
    # self.tree_view.unit_cell_model.signals.updated.connect(self.save_unit_cell)
    # self.tree_view.site_model.signals.updated.connect(self.save_site)
    # self.tree_view.state_model.signals.updated.connect(self.save_state)

    # def save_unit_cell(self):
    #     """
    #     Save changes from the unit cell panel to the selected unit cell model.

    #     Takes all field values from the unit cell form panel and updates the
    #     corresponding properties in the UnitCell model object. This includes the
    #     name and all properties of the three basis vectors (x, y, z components
    #     and periodicity flags).
    #     """
    #     # Get the currently selected unit cell
    #     selected_uc_id = self.selection["unit_cell"]
    #     current_uc = self.unit_cells[selected_uc_id]

    #     # Update name and basic properties
    #     current_uc.name = self.tree_view.unit_cell_model["name"]

    #     # Update first basis vector (v1)
    #     current_uc.v1.x = float(self.tree_view.unit_cell_model["v1x"])
    #     current_uc.v1.y = float(self.tree_view.unit_cell_model["v1y"])
    #     current_uc.v1.z = float(self.tree_view.unit_cell_model["v1z"])
    #     current_uc.v1.is_periodic = self.tree_view.unit_cell_model["v1periodic"]

    #     # Update second basis vector (v2)
    #     current_uc.v2.x = float(self.tree_view.unit_cell_model["v2x"])
    #     current_uc.v2.y = float(self.tree_view.unit_cell_model["v2y"])
    #     current_uc.v2.z = float(self.tree_view.unit_cell_model["v2z"])
    #     current_uc.v2.is_periodic = self.tree_view.unit_cell_model["v2periodic"]

    #     # Update third basis vector (v3)
    #     current_uc.v3.x = float(self.tree_view.unit_cell_model["v3x"])
    #     current_uc.v3.y = float(self.tree_view.unit_cell_model["v3y"])
    #     current_uc.v3.z = float(self.tree_view.unit_cell_model["v3z"])
    #     current_uc.v3.is_periodic = self.tree_view.unit_cell_model["v3periodic"]

    #     # Update UI (selective update instead of full refresh)
    #     self.tree_view.update_tree_item(selected_uc_id)
    #     self.tree_view.select_item(selected_uc_id, "unit_cell")

    # def save_site(self):
    #     """
    #     Save changes from the site panel to the selected site model.

    #     Takes all field values from the site form panel and updates the
    #     corresponding properties in the Site model object. This includes the
    #     name and fractional coordinates (c1, c2, c3).
    #     """
    #     # Get the currently selected site
    #     selected_uc_id = self.selection["unit_cell"]
    #     selected_site_id = self.selection["site"]
    #     current_uc = self.unit_cells[selected_uc_id]
    #     current_site = current_uc.sites[selected_site_id]

    #     # Update site properties
    #     current_site.name = self.tree_view.site_model["name"]
    #     current_site.c1 = float(self.tree_view.site_model["c1"])
    #     current_site.c2 = float(self.tree_view.site_model["c2"])
    #     current_site.c3 = float(self.tree_view.site_model["c3"])

    #     # Update UI (selective update instead of full refresh)
    #     self.tree_view.update_tree_item(selected_uc_id, selected_site_id)
    #     self.tree_view.select_item(selected_site_id, "site", selected_uc_id)

    # def save_state(self):
    #     """
    #     Save changes from the state panel to the selected state model.

    #     Takes all field values from the state form panel and updates the
    #     corresponding properties in the State model object. This includes the
    #     name and energy level.
    #     """
    #     print(self.selection)
    #     # Get the currently selected state
    #     selected_uc_id = self.selection["unit_cell"]
    #     selected_site_id = self.selection["site"]
    #     selected_state_id = self.selection["state"]
    #     current_uc = self.unit_cells[selected_uc_id]
    #     current_site = current_uc.sites[selected_site_id]
    #     current_state = current_site.states[selected_state_id]

    #     # Update state properties
    #     current_state.name = self.tree_view.state_model["name"]

    #     # Update UI (selective update instead of full refresh)
    #     self.tree_view.update_tree_item(
    #         selected_uc_id, selected_site_id, selected_state_id
    #     )
    #     self.tree_view.select_item(
    #         selected_state_id, "state", selected_site_id, selected_uc_id
    #     )

    # def delete_item(self):
    #     selected_uc_id = self.selection.get("unit_cell", None)
    #     selected_site_id = self.selection.get("site", None)
    #     selected_state_id = self.selection.get("state", None)

    #     # Check if there is a selected unit cell
    #     if selected_uc_id:
    #         # Check if there a selected site
    #         if selected_site_id:
    #             # Check if there is a selected state
    #             if selected_state_id:
    #                 # Delete the selected state from the site
    #                 del (
    #                     self.unit_cells[selected_uc_id]
    #                     .sites[selected_site_id]
    #                     .states[selected_state_id]
    #                 )
    #                 # Update UI and select the parent site (selective removal instead of full refresh)
    #                 self.tree_view.remove_tree_item(
    #                     selected_uc_id, selected_site_id, selected_state_id
    #                 )
    #                 self.tree_view.select_item(selected_site_id, "site", selected_uc_id)
    #             else:
    #                 # No state selected, therefore remove the site from the unit cell
    #                 del self.unit_cells[selected_uc_id].sites[selected_site_id]

    #                 # Update UI and select the parent unit cell (selective removal instead of full refresh)
    #                 self.tree_view.remove_tree_item(selected_uc_id, selected_site_id)
    #                 self.tree_view.select_item(selected_uc_id, "unit_cell")

    #         else:
    #             # No site selected, therefore remove the unit cell from the model
    #             del self.unit_cells[selected_uc_id]

    #             # Update UI (selective removal instead of full refresh)
    #             self.tree_view.remove_tree_item(selected_uc_id)

    #             # Clear selection explicitly
    #             self.tree_view.tree_view.selectionModel().clearSelection()
    #             self.tree_view.tree_view.setCurrentIndex(
    #                 QModelIndex()
    #             )  # Clear the cursor/visual highlight
    #             self.selection.update({"unit_cell": None, "site": None, "state": None})

    # def reduce_uc_basis(self):
    #     selected_uc_id = self.selection.get("unit_cell", None)
    #     if selected_uc_id:
    #         uc = self.unit_cells[selected_uc_id]
    #         reduced_basis = uc.reduced_basis()

    #         # Run a model update
    #         v1 = reduced_basis[0]
    #         v2 = reduced_basis[1]
    #         v3 = reduced_basis[2]
    #         self.tree_view.unit_cell_model.update(
    #             {
    #                 "v1x": v1.x,
    #                 "v1y": v1.y,
    #                 "v1z": v1.z,
    #                 "v2x": v2.x,
    #                 "v2y": v2.y,
    #                 "v2z": v2.z,
    #                 "v3x": v3.x,
    #                 "v3y": v3.y,
    #                 "v3z": v3.z,
    #             }
    #         )


#         # Sync the UI with the model
#         self.update_ui()

#     # Update model when the fields are being changed
#     def update_model(self, key, value):
#         self.model[key] = value

#     # Use the model to fill the form fields
#     def update_ui(self):
#         self.c1.setValue(self.model["c1"])
#         self.c2.setValue(self.model["c2"])
#         self.c3.setValue(self.model["c3"])


#         # Initial render
#         self.refresh_tree()


#     # Update model when the fields are being changed
#     def update_model(self, key, value):
#         self.model[key] = value

#     # Use the model to fill the form fields
#     def update_ui(self):

#         self.v1[0].setValue(self.model["v1x"])
#         self.v1[1].setValue(self.model["v1y"])
#         self.v1[2].setValue(self.model["v1z"])

#         self.v2[0].setValue(self.model["v2x"])
#         self.v2[1].setValue(self.model["v2y"])
#         self.v2[2].setValue(self.model["v2z"])

#         self.v3[0].setValue(self.model["v3x"])
#         self.v3[1].setValue(self.model["v3y"])
#         self.v3[2].setValue(self.model["v3z"])
