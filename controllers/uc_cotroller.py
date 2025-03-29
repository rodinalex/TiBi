import uuid
from PySide6.QtCore import QObject, Signal
from src.tibitypes import UnitCell, Site, State, BasisVector
from ui.UC.tree_view import TreeViewPanel

from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel


class UCController(QObject):
    """Controller to manage UnitCells, Sites, and States with tree view integration."""

    # Define signals
    model_updated = Signal()

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],  # All the unit cells in the system
        unit_cell_panel: UnitCellPanel,
        site_panel: SitePanel,
        state_panel: StatePanel,
        tree_view: TreeViewPanel,
        selection,
    ):
        super().__init__()
        self.unit_cells = unit_cells
        self.unit_cell_panel = unit_cell_panel
        self.site_panel = site_panel
        self.state_panel = state_panel
        self.tree_view = tree_view
        self.selection = selection

        # Connect UI signals
        self.tree_view.add_unit_cell_btn.clicked.connect(self.add_unit_cell)

        self.unit_cell_panel.save_btn.clicked.connect(self.save_unit_cell)
        self.unit_cell_panel.delete_btn.clicked.connect(self.delete_unit_cell)
        self.unit_cell_panel.add_btn.clicked.connect(self.add_site)

        self.site_panel.save_btn.clicked.connect(self.save_site)
        self.site_panel.delete_btn.clicked.connect(self.delete_site)
        self.site_panel.add_btn.clicked.connect(self.add_state)

        self.state_panel.save_btn.clicked.connect(self.save_state)
        self.state_panel.delete_btn.clicked.connect(self.delete_state)

    def add_unit_cell(self):
        name = "New Unit Cell"
        v1 = BasisVector(1, 0, 0)
        v2 = BasisVector(0, 1, 0)
        v3 = BasisVector(0, 0, 1)

        new_cell = UnitCell(name, v1, v2, v3)

        self.unit_cells[new_cell.id] = new_cell
        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(new_cell.id)

    def save_unit_cell(self):
        # Store current selection
        selected_uc = self.selection["unit_cell"]

        name = self.unit_cell_panel.model["name"]

        v1 = BasisVector(
            float(self.unit_cell_panel.model["v1x"]),
            float(self.unit_cell_panel.model["v1y"]),
            float(self.unit_cell_panel.model["v1z"]),
            self.unit_cell_panel.model["v1periodic"],
        )
        v2 = BasisVector(
            float(self.unit_cell_panel.model["v2x"]),
            float(self.unit_cell_panel.model["v2y"]),
            float(self.unit_cell_panel.model["v2z"]),
            self.unit_cell_panel.model["v2periodic"],
        )

        v3 = BasisVector(
            float(self.unit_cell_panel.model["v3x"]),
            float(self.unit_cell_panel.model["v3y"]),
            float(self.unit_cell_panel.model["v3z"]),
            self.unit_cell_panel.model["v3periodic"],
        )

        sites = self.unit_cell_panel.model["sites"]

        updated_uc = UnitCell(name, v1, v2, v3, sites, selected_uc)

        self.unit_cells[selected_uc] = updated_uc
        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(selected_uc)

    def delete_unit_cell(self):
        selected_uc = self.selection["unit_cell"]
        del self.unit_cells[selected_uc]
        self.tree_view.refresh_tree()

    def add_site(self):
        name = "New Site"
        c1 = 0
        c2 = 0
        c3 = 0
        new_site = Site(name, c1, c2, c3)

        unit_cell = self.unit_cells[self.selection["unit_cell"]]
        unit_cell.sites[new_site.id] = new_site
        self.tree_view.refresh_tree()
        self.tree_view.select_site(unit_cell.id, new_site.id)

    def save_site(self):
        # Store the current selection
        selected_uc = self.selection["unit_cell"]
        selected_site = self.selection["site"]
        name = self.site_panel.model["name"]
        c1 = float(self.site_panel.model["c1"])
        c2 = float(self.site_panel.model["c2"])
        c3 = float(self.site_panel.model["c3"])
        states = self.site_panel.model["states"]

        updated_site = Site(name, c1, c2, c3, states, selected_site)

        self.unit_cells[selected_uc].sites[selected_site] = updated_site
        self.tree_view.refresh_tree()
        self.tree_view.select_site(selected_uc, selected_site)

    def delete_site(self):
        selected_uc = self.selection["unit_cell"]
        selected_site = self.selection["site"]
        del self.unit_cells[selected_uc].sites[selected_site]
        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(selected_uc)

    def add_state(self):
        name = "New State"
        energy = 0
        new_state = State(name, energy)
        unit_cell = self.unit_cells[self.selection["unit_cell"]]
        site = unit_cell.sites[self.selection["site"]]
        site.states[new_state.id] = new_state
        self.tree_view.refresh_tree()
        self.tree_view.select_state(unit_cell.id, site.id, new_state.id)

    def save_state(self):
        selected_uc = self.selection["unit_cell"]
        selected_site = self.selection["site"]
        selected_state = self.selection["state"]
        name = self.state_panel.model["name"]
        energy = self.state_panel.model["energy"]

        updated_state = State(name, energy)

        self.unit_cells[selected_uc].sites[selected_site].states[
            selected_state
        ] = updated_state
        self.tree_view.refresh_tree()
        self.tree_view.select_state(selected_uc, selected_site, selected_state)

    def delete_state(self):
        selected_uc = self.selection["unit_cell"]
        selected_site = self.selection["site"]
        selected_state = self.selection["state"]
        del self.unit_cells[selected_uc].sites[selected_site].states[selected_state]
        self.tree_view.refresh_tree()
        self.tree_view.select_site(selected_uc, selected_site)
