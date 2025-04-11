import uuid
from PySide6.QtCore import QObject, QModelIndex
from src.tibitypes import UnitCell, Site, State, BasisVector
from ui.UC.tree_view_panel import TreeViewPanel
from ui.UC.button_panel import ButtonPanel


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
        tree_view: TreeViewPanel,  # Tree view showing the hierarchy
        button_panel: ButtonPanel,  # Create/Delete buttons
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
        self.tree_view = tree_view
        self.button_panel = button_panel
        self.selection = selection

        # Connect UI signals to appropriate handler methods

        # Tree view signals
        self.tree_view.delete.connect(self.delete_item)
        self.tree_view.delete.connect(self.delete_item)
        self.tree_view.delete.connect(self.delete_item)

        # Button panel signals
        self.button_panel.new_uc_btn.clicked.connect(self.add_unit_cell)
        self.button_panel.new_site_btn.clicked.connect(self.add_site)
        self.button_panel.new_state_btn.clicked.connect(self.add_state)
        self.button_panel.delete_btn.clicked.connect(self.delete_item)

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
        current_uc.name = self.tree_view.unit_cell_model["name"]

        # Update first basis vector (v1)
        current_uc.v1.x = float(self.tree_view.unit_cell_model["v1x"])
        current_uc.v1.y = float(self.tree_view.unit_cell_model["v1y"])
        current_uc.v1.z = float(self.tree_view.unit_cell_model["v1z"])
        current_uc.v1.is_periodic = self.tree_view.unit_cell_model["v1periodic"]

        # Update second basis vector (v2)
        current_uc.v2.x = float(self.tree_view.unit_cell_model["v2x"])
        current_uc.v2.y = float(self.tree_view.unit_cell_model["v2y"])
        current_uc.v2.z = float(self.tree_view.unit_cell_model["v2z"])
        current_uc.v2.is_periodic = self.tree_view.unit_cell_model["v2periodic"]

        # Update third basis vector (v3)
        current_uc.v3.x = float(self.tree_view.unit_cell_model["v3x"])
        current_uc.v3.y = float(self.tree_view.unit_cell_model["v3y"])
        current_uc.v3.z = float(self.tree_view.unit_cell_model["v3z"])
        current_uc.v3.is_periodic = self.tree_view.unit_cell_model["v3periodic"]

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(selected_uc_id)
        self.tree_view.select_item(selected_uc_id, "unit_cell")

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
        current_site.name = self.tree_view.site_model["name"]
        current_site.c1 = float(self.tree_view.site_model["c1"])
        current_site.c2 = float(self.tree_view.site_model["c2"])
        current_site.c3 = float(self.tree_view.site_model["c3"])

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(selected_uc_id, selected_site_id)
        self.tree_view.select_item(selected_site_id, "site", selected_uc_id)

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
        current_state.name = self.tree_view.state_model["name"]

        # Update UI (selective update instead of full refresh)
        self.tree_view.update_tree_item(
            selected_uc_id, selected_site_id, selected_state_id
        )
        self.tree_view.select_item(
            selected_state_id, "state", selected_site_id, selected_uc_id
        )

    def delete_item(self):
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
                    self.tree_view.remove_tree_item(
                        selected_uc_id, selected_site_id, selected_state_id
                    )
                    self.tree_view.select_item(selected_site_id, "site", selected_uc_id)
                else:
                    # No state selected, therefore remove the site from the unit cell
                    del self.unit_cells[selected_uc_id].sites[selected_site_id]

                    # Update UI and select the parent unit cell (selective removal instead of full refresh)
                    self.tree_view.remove_tree_item(selected_uc_id, selected_site_id)
                    self.tree_view.select_item(selected_uc_id, "unit_cell")

            else:
                # No site selected, therefore remove the unit cell from the model
                del self.unit_cells[selected_uc_id]

                # Update UI (selective removal instead of full refresh)
                self.tree_view.remove_tree_item(selected_uc_id)

                # Clear selection explicitly
                self.tree_view.tree_view.selectionModel().clearSelection()
                self.tree_view.tree_view.setCurrentIndex(
                    QModelIndex()
                )  # Clear the cursor/visual highlight
                self.tree_view.selection_changed_signal.emit(None, None, None)
