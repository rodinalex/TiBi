from PySide6.QtCore import (
    QItemSelectionModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QStandardItem
from PySide6.QtWidgets import QColorDialog, QDoubleSpinBox
import random
import uuid

from models.data_models import DataModel
from resources.constants import (
    default_site_size,
    mk_new_site,
    mk_new_state,
    mk_new_unit_cell,
    selection_init,
)
from src.tibitypes import BasisVector, Site, State, UnitCell
from views.uc_view import UnitCellView


class UnitCellController(QObject):
    """
    Controller managing interactions between the UI and unit cell data model.

    This controller connects UI signals from the form panels and tree view to
    appropriate actions that modify the underlying data models.
    It handles all CRUD (create, read, update, delete) operations for
    the hierarchy of unit cells, sites, and states.

    The controller follows the MVC (Model-View-Controller) pattern:
    - Models: The unit_cells dictionary and the form panel models
    - Views: The tree view and form panels
    - Controller: This class, which updates models in response to UI events

    After data model changes, the controller updates the tree view and
    reselects the appropriate node to maintain UI state consistency.
    """

    plot_update_requested = Signal()
    item_changed = (
        Signal()
    )  # A signal emitted when the user changes the item by interacting
    # with the tree. Used to notify the app_controller
    # that the hopping matrix needs to be redrawn to
    # reflect the correct site/state names

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        unit_cell_data: DataModel,
        unit_cell_view: UnitCellView,
    ):
        """
        Initialize the controller and connect UI signals to handler methods.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: DataModel tracking the currently selected
            unit cell, site, and state
            unit_cell_data: DataModel tracking the parameters of
            the selected unit cell and site
            unit_cell_view: The main view component containing
            tree view and form panels
        """
        super().__init__()
        # Store references to UI components and data models
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_data = unit_cell_data
        self.unit_cell_view = unit_cell_view

        # Get the fields from unit_cell_view for convenience
        # For the basis vectors, each reference has three spinboxes
        # corresponding to the Cartesian coordinates
        self.v1 = self.unit_cell_view.unit_cell_panel.v1
        self.v2 = self.unit_cell_view.unit_cell_panel.v2
        self.v3 = self.unit_cell_view.unit_cell_panel.v3

        self.R = self.unit_cell_view.site_panel.R
        self.c1 = self.unit_cell_view.site_panel.c1
        self.c2 = self.unit_cell_view.site_panel.c2
        self.c3 = self.unit_cell_view.site_panel.c3

        # Store the tree_view and tree_model as parameters for convenience
        self.tree_view = self.unit_cell_view.tree_view_panel.tree_view
        self.tree_model = self.unit_cell_view.tree_view_panel.tree_model

        # A flag to suppress the change of dimensionality listener.
        # Used when the dimensionality radio buttons are triggered
        # programmatically to avoid unnecessary update cycles.
        self._suppress_dim_listener = False
        # Rebuild the tree view from scratch in the beginning
        self.refresh_tree()

        # Sync UI with data models
        self._update_unit_cell_ui()

        # Connect signals
        # Tree view signals
        # Triggered when the tree selection changed,
        # either manually or programmatically
        self.tree_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        # Triggered when a tree item's name is changed by double clicking on it
        self.tree_model.itemChanged.connect(self._on_item_renamed)
        # Triggered when the user presses Del or Backspace while
        # a tree item is highlighted, or clicks the Delete button
        self.unit_cell_view.tree_view_panel.delete_requested.connect(
            self._delete_item
        )

        # Unit Cell basis vector signals.
        def connect_vector_fields(
            vector_name, spinboxes: list[QDoubleSpinBox]
        ):
            for ii, axis in enumerate("xyz"):
                spinboxes[ii].editingFinished.connect(
                    lambda ii=ii, axis=axis: self._update_unit_cell_data(
                        f"{vector_name}{axis}", spinboxes[ii].value()
                    )
                )

        connect_vector_fields("v1", self.v1)
        connect_vector_fields("v2", self.v2)
        connect_vector_fields("v3", self.v3)

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

        # Site panel signals.
        # Site Radius
        self.R.editingFinished.connect(lambda: self._update_site_size())

        # Site fractional coordinates
        self.c1.editingFinished.connect(
            lambda: self._update_site_data("c1", self.c1.value())
        )
        self.c2.editingFinished.connect(
            lambda: self._update_site_data("c2", self.c2.value())
        )
        self.c3.editingFinished.connect(
            lambda: self._update_site_data("c3", self.c3.value())
        )

        # Button signals
        # New UC button
        self.unit_cell_view.tree_view_panel.new_uc_btn.clicked.connect(
            self._add_unit_cell
        )
        # New Site button
        self.unit_cell_view.unit_cell_panel.new_site_btn.clicked.connect(
            self._add_site
        )
        # New State button
        self.unit_cell_view.site_panel.new_state_btn.clicked.connect(
            self._add_state
        )
        # Delete button--deletes the highlighted tree item
        self.unit_cell_view.tree_view_panel.delete_btn.clicked.connect(
            self._delete_item
        )
        # Reduce button--LLL argorithm to obtain the primitive cell
        self.unit_cell_view.unit_cell_panel.reduce_btn.clicked.connect(
            self._reduce_uc_basis
        )
        # Opens a color picker to change the color of the selected site
        self.unit_cell_view.site_panel.color_picker_btn.clicked.connect(
            self._pick_site_color
        )

        # Selection change. Triggered by the change of the selection model
        # to show the appropriate panels and plots
        self.selection.signals.updated.connect(self._show_panels)

        # When model changes, update UI. If the model changes
        # programmatically, the updates fill out the relevant fields
        self.unit_cell_data.signals.updated.connect(self._update_unit_cell_ui)

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
        - _add_tree_item() - For adding or updating a single node
        - _remove_tree_item() - For removing a single node

        This full refresh is typically only needed during initialization or
        when multiple components of the tree need to be updated simultaneously.
        """
        self.tree_model.clear()
        self.root_node = self.tree_model.invisibleRootItem()

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

    def _add_tree_item(self, uc_id, site_id=None, state_id=None):
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
            data = self.unit_cells[uc_id].sites[site_id].states[state_id]
        elif site_id is not None:  # Adding a site
            parent = self._find_item_by_id(uc_id)
            item_type, item_id = "site", site_id
            data = self.unit_cells[uc_id].sites[site_id]
        else:  # Adding a unit cell
            parent = self.root_node
            item_type, item_id = "unit_cell", uc_id
            data = self.unit_cells[uc_id]

        item = self._create_tree_item(
            data, item_type=item_type, item_id=item_id
        )
        parent.appendRow(item)
        index = self.tree_model.indexFromItem(item)
        self.tree_view.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.ClearAndSelect
        )

    # Programmatically select a tree item
    def _select_item(self, uc_id, site_id=None, state_id=None):
        """
        Select a tree item by its ID and type.

        This method programmatically selects an item in the tree view.
        This selection triggers _on_selection_changed function.

        Args:
            uc_id: UUID of the unit cell
            site_id: UUID of the site
            state_id: UUID of the state
        """
        item = self._find_item_by_id(uc_id, site_id, state_id)
        if item is not None:
            index = self.tree_model.indexFromItem(item)
            self.tree_view.selectionModel().setCurrentIndex(
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
        # If the item is a unit cell, the parent is None, so we
        # default to the invisibleRootItem
        parent = item.parent() or self.root_node
        # If the item has a parent, select it
        if item.parent():
            index = self.tree_model.indexFromItem(parent)
            self.tree_view.selectionModel().setCurrentIndex(
                index, QItemSelectionModel.ClearAndSelect
            )
        # Otherwise, deselect everything (the item is a unit cell)
        else:
            self.tree_view.selectionModel().clearSelection()
            self.tree_view.setCurrentIndex(QModelIndex())
        # Delete the item
        parent.removeRow(item.row())

    def _create_tree_item(
        self, item_data, item_type, item_id
    ) -> QStandardItem:
        """
        Create a QStandardItem for tree with metadata

        Args:
            item_data: UnitCell, Site, or State object. Used to get the name
            item_type: item type ("unit_cell", "site", or "state")
            item_id: UUID of the item
        """
        tree_item = QStandardItem(item_data.name)
        tree_item.setData(item_type, Qt.UserRole + 1)  # Store the type
        tree_item.setData(item_id, Qt.UserRole + 2)  # Store the ID

        # Set other visual properties
        tree_item.setEditable(True)

        return tree_item

    def _on_selection_changed(self, selected, deselected):
        """
        Handle the change of selection in the tree.

        This method is called when the user selects a node in the tree view or
        the selection occurs programmatically.
        It determines what type of node was selected
        (unit cell, site, or state) and updates the selection model with
        the item's id and, if applicable, its parent's/grandparent's id's.
        The change in the selection dictionary triggers
        the _show_panels function.

        Args:
            selected: The newly selected items
            deselected: The previously selected items that are now deselected
        """
        indexes = selected.indexes()

        if not indexes:
            self.selection.update(selection_init())
            return

        # Get the selected item
        index = indexes[0]
        item = self.tree_model.itemFromIndex(index)

        item_type = item.data(Qt.UserRole + 1)
        item_id = item.data(Qt.UserRole + 2)

        if item_type == "unit_cell":  # unit cell selected
            self.selection.update(
                {"unit_cell": item_id, "site": None, "state": None}
            )
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
                    {
                        "unit_cell": grandparent_id,
                        "site": parent_id,
                        "state": item_id,
                    }
                )
            # Since we are selecting a site or a state, we need to fill
            # in the site radius and color properties.
            # Note that the radius and color of the site are updated
            # upon selection, not upon model change. The reason is that size
            # and color are not the properties of a site per se, but rather
            # visualization properties, stored in separate dictionaries.
            # When a new site is selected, the site model (coordinates)
            # might be exactly the same as for the previously
            # selected site. Because the coordinate field update would not be
            # triggered, the radius and color fields would contain wrong data
            site_radius = self.unit_cells[
                self.selection["unit_cell"]
            ].site_sizes[self.selection["site"]]
            self.R.setValue(site_radius)

            site_color = self.unit_cells[
                self.selection["unit_cell"]
            ].site_colors[self.selection["site"]]

            c = (
                int(site_color[0] * 255),
                int(site_color[1] * 255),
                int(site_color[2] * 255),
                int(site_color[3]),
            )  # Color in 0-255 component range

            self.unit_cell_view.site_panel.color_picker_btn.setStyleSheet(
                f"background-color: rgba({c[0]}, {c[1]}, {c[2]}, {c[3]});"
            )

    def _on_item_renamed(self, item: QStandardItem):
        """
        Change the name of the selected item by double-clicking on it in
        the tree view. Update the data and save it.
        """
        item_type = item.data(Qt.UserRole + 1)
        new_name = item.text()
        if item_type == "unit_cell":
            self.unit_cell_data["unit_cell_name"] = new_name
            self._save_unit_cell()
        elif item_type == "site":
            self.unit_cell_data["site_name"] = new_name
            self._save_site()
        else:
            self.unit_cell_data["state_name"] = new_name
            self._save_state()
        self.item_changed.emit()

    # Unit Cell/Site/State Modification Functions

    def _add_unit_cell(self):
        """
        Create a new unit cell with default properties and add it to the model.

        Creates a unit cell with orthogonal basis vectors along
        the x, y, and z axes, adds it to the unit_cells dictionary,
        and selects it in the tree view.

        The default unit cell has:
        - Name: "New Unit Cell"
        - Three orthogonal unit vectors along the x, y, and z axes
        - No periodicity (0D system)
        - No sites or states initially

        After creation, the tree view is updated and the new unit cell is
        automatically selected so the user can immediately edit its properties.
        """
        new_cell = mk_new_unit_cell()
        self.unit_cells[new_cell.id] = new_cell

        self._add_tree_item(new_cell.id)

    def _add_site(self):
        """
        Create a new site in the currently selected unit cell.

        Creates a site with default name and coordinates (0,0,0), adds it to
        the sites dictionary of the selected unit cell, and selects it in
        the tree view.

        The default site has:
        - Name: "New Site"
        - Coordinates (0,0,0)
        - No states initially
        """
        new_site = mk_new_site()

        # Add the site to the selected unit cell
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]
        current_uc.sites[new_site.id] = new_site
        current_uc.site_colors[new_site.id] = (
            random.uniform(0, 1),
            random.uniform(0, 1),
            random.uniform(0, 1),
            1.0,
        )
        current_uc.site_sizes[new_site.id] = default_site_size

        self._add_tree_item(selected_uc_id, new_site.id)

    def _add_state(self):
        """
        Create a new state in the currently selected site.

        Creates a state with default name, adds it to the
        states dictionary of the selected site,
        and selects it in the tree view.

        The default state has:
        - Name: "New State"
        """
        # Create a new state with default properties
        new_state = mk_new_state()

        # Add the state to the selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_site.states[new_state.id] = new_state

        self._add_tree_item(selected_uc_id, selected_site_id, new_state.id)

    def _save_unit_cell(self):
        """
        Save changes from the unit cell data model to the selected unit cell.

        This method is automatically triggered when the unit_cell_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        Because the updates in the fields do not change the unit cell name,
        there is no update required for the tree.
        """
        # Get the currently selected unit cell
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]

        # Update name and basic properties
        current_uc.name = self.unit_cell_data["unit_cell_name"]

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

        # After unit cell object is updated, notify plot controllers
        self.plot_update_requested.emit()

    def _save_site(self):
        """
        Save changes from the site data model to the selected site.

        This method is automatically triggered when the site_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        Because the updates in the fields do not change the site name,
        there is no update required for the tree.
        """
        # Get the currently selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]

        # Update site properties
        current_site.name = self.unit_cell_data["site_name"]
        current_site.c1 = float(self.unit_cell_data["c1"])
        current_site.c2 = float(self.unit_cell_data["c2"])
        current_site.c3 = float(self.unit_cell_data["c3"])

        # After site object is updated, notify plot controllers
        self.plot_update_requested.emit()

    def _save_state(self):
        """
        Save changes from the state data model to the selected state.

        This method is automatically triggered when the site_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        Because the updates in the fields do not change the state name,
        there is no update required for the tree.
        """
        # Get the currently selected state
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_state = current_site.states[selected_state_id]

        # Update state properties
        current_state.name = self.unit_cell_data["state_name"]

    def _delete_item(self):
        """
        Delete the currently selected item from the model.

        This method handles deletion of unit cells, sites, and states based on
        the current selection. It updates both the data model and
        the tree view to reflect the deletion, and ensures that
        the selection is updated appropriately.

        The deletion follows the containment hierarchy:
        - Deleting a unit cell also removes all its sites and states
        - Deleting a site also removes all its states
        - Deleting a state only removes that specific state

        After deletion, the parent item is selected
        (or nothing if a unit cell was deleted).
        """
        selected_uc_id = self.selection.get("unit_cell", None)
        selected_site_id = self.selection.get("site", None)
        selected_state_id = self.selection.get("state", None)

        if selected_state_id:
            # Delete the selected state from the site
            del (
                self.unit_cells[selected_uc_id]
                .sites[selected_site_id]
                .states[selected_state_id]
            )
        elif selected_site_id:
            # No state selected, therefore remove the site from the unit cell
            del self.unit_cells[selected_uc_id].sites[selected_site_id]
        else:
            # No site selected, therefore remove the unit cell from the model
            del self.unit_cells[selected_uc_id]
        # Update UI and select the parent site
        # (selective removal instead of full refresh)
        self._remove_tree_item(
            selected_uc_id, selected_site_id, selected_state_id
        )

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

        unit_cell_updated_data = {}
        site_updated_data = {}
        state_updated_data = {}

        if unit_cell_id:
            # Get the selected unit cell
            uc = self.unit_cells[unit_cell_id]

            # Get the system dimensionality
            dim = uc.v1.is_periodic + uc.v2.is_periodic + uc.v3.is_periodic
            # Set the dimensionality radio button.
            # Suppress the dim_listener since we are updating the radio button programmatically
            self._suppress_dim_listener = True
            self.unit_cell_view.unit_cell_panel.radio_group.button(
                dim
            ).setChecked(True)
            self._suppress_dim_listener = False

            # Get the model fields that are going to be updated from the selected unit cell.
            # Update the empty unit_cell_updated_data dictionary
            unit_cell_updated_data.update(
                {
                    "unit_cell_name": uc.name,
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
            # Show the UnitCellPanel
            self.unit_cell_view.uc_stack.setCurrentWidget(
                self.unit_cell_view.unit_cell_panel
            )

            if site_id:
                site = uc.sites[site_id]
                # Get the model fields that are going to be updated from the selected site.
                # Update the empty site_updated_data dictionary
                site_updated_data.update(
                    {
                        "site_name": site.name,
                        "c1": site.c1,
                        "c2": site.c2,
                        "c3": site.c3,
                    }
                )
                # Show the SitePanel
                self.unit_cell_view.site_stack.setCurrentWidget(
                    self.unit_cell_view.site_panel
                )
                if state_id:
                    state = site.states[state_id]
                    # Get the model fields that are going to be updated from the selected state.
                    # Update the empty state_updated_data dictionary
                    state_updated_data.update(
                        {
                            "state_name": state.name,
                        }
                    )
            else:
                # If no site is selected, hide the SitePanel
                self.unit_cell_view.site_stack.setCurrentWidget(
                    self.unit_cell_view.site_info_label
                )
        else:
            # If no unit cell is selected, hide the SitePanel and UnitCellPanel
            self.unit_cell_view.uc_stack.setCurrentWidget(
                self.unit_cell_view.uc_info_label
            )
            self.unit_cell_view.site_stack.setCurrentWidget(
                self.unit_cell_view.site_info_label
            )
        # Compine the update dictionaries and use the combination to update the model
        self.unit_cell_data.update(
            unit_cell_updated_data | site_updated_data | state_updated_data
        )
        # Request a plot update
        self.plot_update_requested.emit()

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
            # If the listener is suppressed (when the dimensionality was set programmatically),
            # do not run the save cycle
            if self._suppress_dim_listener:
                return
            self._save_unit_cell()

    def _update_unit_cell_data(self, key, value):
        """
        Update the unit cell data model with new values pertaining to the unit cell.

        This method is called when the user edits a unit cell property in the unit cell form panel.
        It updates the reactive data model, which will trigger a signal that causes the
        _save_unit_cell method to update the actual UnitCell object. This separation
        allows for validation and coalescing of multiple changes.

        Args:
            key: The property name to update (e.g., "v1x", "v2y", "unit_cell_name")
            value: The new value for the property
        """
        self.unit_cell_data[key] = value
        self._save_unit_cell()

    def _update_site_data(self, key, value):
        """
        Update the unit cell data model with new values pertaining to the site

        This method is called when the user edits a site property in the unit cell form panel.
        It updates the reactive data model, which will trigger a signal that causes the
        _save_site method to update the actual UnitCell object. This separation
        allows for validation and coalescing of multiple changes.

        Args:
            key: The property name to update (e.g., "c1", "c2", "site_name")
            value: The new value for the property
        """
        self.unit_cell_data[key] = value
        self._save_site()

    def _update_unit_cell_ui(self):
        """
        Update the UI with the current unit cell data.
        This method sets the values of the spinboxes in the unit cell panel
        based on the current values in the unit_cell_data dictionary.
        These updates do not trigger any signals as the values change using
        setValue and not using direct input.
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

        self.c1.setValue(self.unit_cell_data["c1"])
        self.c2.setValue(self.unit_cell_data["c2"])
        self.c3.setValue(self.unit_cell_data["c3"])

    def _update_site_size(self):
        """
        Update the size of the site marker. First, the data from the
        spinbox is saved to the dictionary of sizes. Next, a UC plot
        update is requested.
        """
        self.unit_cells[self.selection["unit_cell"]].site_sizes[
            self.selection["site"]
        ] = self.R.value()
        self.plot_update_requested.emit()

    def _pick_site_color(self):
        """
        Use a color dialog to choose a color for the selected site to be used
        in the UC plot. The color is saved in the dictionary of colors. Next,
        a UC plot update is requested.
        """
        old_color = self.unit_cells[self.selection["unit_cell"]].site_colors[
            self.selection["site"]
        ]
        # Open the color dialog with the current color selected
        start_color = QColor(
            int(old_color[0] * 255),
            int(old_color[1] * 255),
            int(old_color[2] * 255),
            int(old_color[3] * 255),
        )
        new_color = QColorDialog.getColor(
            initial=start_color,
            options=QColorDialog.ShowAlphaChannel,
        )
        # Update the button color
        if new_color.isValid():
            self.unit_cell_view.site_panel.color_picker_btn.setStyleSheet(
                f"background-color: rgba({new_color.red()}, {new_color.green()}, {new_color.blue()}, {new_color.alpha()});"
            )
            # Update the color in the dictionary
            self.unit_cells[self.selection["unit_cell"]].site_colors[
                self.selection["site"]
            ] = (
                new_color.redF(),
                new_color.greenF(),
                new_color.blueF(),
                new_color.alphaF(),
            )
            self.plot_update_requested.emit()
