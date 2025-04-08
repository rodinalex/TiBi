import uuid
from PySide6.QtCore import QObject, Signal, QModelIndex
from src.tibitypes import UnitCell, Site, State, BasisVector
from ui.UC.tree_view_panel import TreeViewPanel
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel


class UCController(QObject):
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
        unit_cells: dict[uuid.UUID, UnitCell],  # Dictionary of all unit cells
        unit_cell_panel: UnitCellPanel,  # Form panel for editing unit cells
        site_panel: SitePanel,  # Form panel for editing sites
        state_panel: StatePanel,  # Form panel for editing states
        tree_view: TreeViewPanel,  # Tree view showing the hierarchy
        selection,  # Tracks currently selected items
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
        self.unit_cell_panel = unit_cell_panel
        self.site_panel = site_panel
        self.state_panel = state_panel
        self.tree_view = tree_view
        self.selection = selection

        # Connect UI signals to appropriate handler methods

        # Tree view button
        self.tree_view.add_unit_cell_btn.clicked.connect(self.add_unit_cell)

        # Unit cell panel buttons
        self.unit_cell_panel.delete_btn.clicked.connect(self.delete_unit_cell)
        self.unit_cell_panel.add_btn.clicked.connect(self.add_site)

        # Site panel buttons
        self.site_panel.delete_btn.clicked.connect(self.delete_site)
        self.site_panel.add_btn.clicked.connect(self.add_state)

        # State panel buttons
        self.state_panel.delete_btn.clicked.connect(self.delete_state)

        # Tree view signals
        self.tree_view.unit_cell_delete.connect(self.delete_unit_cell)
        self.tree_view.site_delete.connect(self.delete_site)
        self.tree_view.state_delete.connect(self.delete_state)

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
        self.tree_view.update_tree_item(new_cell.id)
        self.tree_view.select_item(new_cell.id, "unit_cell")

    def save_unit_cell(self):
        """
        Save changes from the unit cell panel to the selected unit cell model.

        Takes all field values from the unit cell form panel and updates the
        corresponding properties in the UnitCell model object. This includes the
        name and all properties of the three basis vectors (x, y, z components
        and periodicity flags).
        """
        # Get the currently selected unit cell
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]

        # Update name and basic properties
        current_uc.name = self.unit_cell_panel.model["name"]

        # Update first basis vector (v1)
        current_uc.v1.x = float(self.unit_cell_panel.model["v1x"])
        current_uc.v1.y = float(self.unit_cell_panel.model["v1y"])
        current_uc.v1.z = float(self.unit_cell_panel.model["v1z"])
        current_uc.v1.is_periodic = self.unit_cell_panel.model["v1periodic"]

        # Update second basis vector (v2)
        current_uc.v2.x = float(self.unit_cell_panel.model["v2x"])
        current_uc.v2.y = float(self.unit_cell_panel.model["v2y"])
        current_uc.v2.z = float(self.unit_cell_panel.model["v2z"])
        current_uc.v2.is_periodic = self.unit_cell_panel.model["v2periodic"]

        # Update third basis vector (v3)
        current_uc.v3.x = float(self.unit_cell_panel.model["v3x"])
        current_uc.v3.y = float(self.unit_cell_panel.model["v3y"])
        current_uc.v3.z = float(self.unit_cell_panel.model["v3z"])
        current_uc.v3.is_periodic = self.unit_cell_panel.model["v3periodic"]

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(selected_uc_id)
        self.tree_view.select_item(selected_uc_id, "unit_cell")

    def delete_unit_cell(self):
        """
        Delete the currently selected unit cell from the model.

        Removes the unit cell from the unit_cells dictionary and refreshes the tree view.
        This also deletes all child sites and states associated with this unit cell.
        """
        # Get the ID of the selected unit cell
        selected_uc_id = self.selection["unit_cell"]

        # Remove the unit cell from the model
        del self.unit_cells[selected_uc_id]

        # Update UI (selective removal instead of full refresh)
        self.tree_view.remove_tree_item(selected_uc_id)

        # Clear selection explicitly
        self.tree_view.tree_view.selectionModel().clearSelection()
        self.tree_view.tree_view.setCurrentIndex(
            QModelIndex()
        )  # Clear the cursor/visual highlight
        self.tree_view.none_selected.emit()

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
        self.tree_view.update_tree_item(selected_uc_id, new_site.id)
        self.tree_view.select_item(new_site.id, "site", selected_uc_id)

    def save_site(self):
        """
        Save changes from the site panel to the selected site model.

        Takes all field values from the site form panel and updates the
        corresponding properties in the Site model object. This includes the
        name and fractional coordinates (c1, c2, c3).
        """
        # Get the currently selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]

        # Update site properties
        current_site.name = self.site_panel.model["name"]
        current_site.c1 = float(self.site_panel.model["c1"])
        current_site.c2 = float(self.site_panel.model["c2"])
        current_site.c3 = float(self.site_panel.model["c3"])

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(selected_uc_id, selected_site_id)
        self.tree_view.select_item(selected_site_id, "site", selected_uc_id)

    def delete_site(self):
        """
        Delete the currently selected site from its unit cell.

        Removes the site from the sites dictionary of the unit cell and refreshes
        the tree view. This also deletes all child states associated with this site.
        After deletion, selects the parent unit cell in the tree view.
        """
        # Get the currently selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]

        # Remove the site from the unit cell
        del self.unit_cells[selected_uc_id].sites[selected_site_id]

        # Update UI and select the parent unit cell (selective removal instead of full refresh)
        self.tree_view.remove_tree_item(selected_uc_id, selected_site_id)
        self.tree_view.select_item(selected_uc_id, "unit_cell")

    def add_state(self):
        """
        Create a new quantum state in the currently selected site.

        Creates a state with default name and zero energy, adds it to the
        states dictionary of the selected site, and selects it in the tree view.
        """
        # Create a new state with default properties
        name = "New State"
        energy = 0  # Default energy level (eV)
        new_state = State(name, energy)

        # Add the state to the selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_site.states[new_state.id] = new_state

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(selected_uc_id, selected_site_id, new_state.id)
        self.tree_view.select_item(
            new_state.id, "state", selected_site_id, selected_uc_id
        )

    def save_state(self):
        """
        Save changes from the state panel to the selected state model.

        Takes all field values from the state form panel and updates the
        corresponding properties in the State model object. This includes the
        name and energy level.
        """
        # Get the currently selected state
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_state = current_site.states[selected_state_id]

        # Update state properties
        current_state.name = self.state_panel.model["name"]
        current_state.energy = self.state_panel.model["energy"]

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(
            selected_uc_id, selected_site_id, selected_state_id
        )
        self.tree_view.select_item(
            selected_state_id, "state", selected_site_id, selected_uc_id
        )

    def delete_state(self):
        """
        Delete the currently selected quantum state from its site.

        Removes the state from the states dictionary of the site and refreshes
        the tree view. After deletion, selects the parent site in the tree view.
        """
        # Get the currently selected state
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]

        # Remove the state from the site
        del (
            self.unit_cells[selected_uc_id]
            .sites[selected_site_id]
            .states[selected_state_id]
        )

        # Update UI and select the parent site (selective removal instead of full refresh)
        self.tree_view.remove_tree_item(
            selected_uc_id, selected_site_id, selected_state_id
        )
        self.tree_view.select_item(selected_site_id, "site", selected_uc_id)
