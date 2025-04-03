import uuid
from PySide6.QtCore import QObject, Signal
from src.tibitypes import UnitCell, Site, State, BasisVector
from ui.UC.tree_view_panel import TreeViewPanel
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel


class UCController(QObject):
    """Controller to manage UnitCells, Sites, and States with tree view integration."""

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
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]

        current_uc.name = self.unit_cell_panel.model["name"]

        current_uc.v1.x = float(self.unit_cell_panel.model["v1x"])
        current_uc.v1.y = float(self.unit_cell_panel.model["v1y"])
        current_uc.v1.z = float(self.unit_cell_panel.model["v1z"])
        current_uc.v1.periodic = self.unit_cell_panel.model["v1periodic"]

        current_uc.v2.x = float(self.unit_cell_panel.model["v2x"])
        current_uc.v2.y = float(self.unit_cell_panel.model["v2y"])
        current_uc.v2.z = float(self.unit_cell_panel.model["v2z"])
        current_uc.v2.periodic = self.unit_cell_panel.model["v2periodic"]

        current_uc.v3.x = float(self.unit_cell_panel.model["v3x"])
        current_uc.v3.y = float(self.unit_cell_panel.model["v3y"])
        current_uc.v3.z = float(self.unit_cell_panel.model["v3z"])
        current_uc.v3.periodic = self.unit_cell_panel.model["v3periodic"]

        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(selected_uc_id)

    def delete_unit_cell(self):
        selected_uc_id = self.selection["unit_cell"]
        del self.unit_cells[selected_uc_id]
        self.tree_view.refresh_tree()

    def add_site(self):
        name = "New Site"
        c1 = 0
        c2 = 0
        c3 = 0
        new_site = Site(name, c1, c2, c3)

        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]

        current_uc.sites[new_site.id] = new_site
        self.tree_view.refresh_tree()
        self.tree_view.select_site(selected_uc_id, new_site.id)

    def save_site(self):
        # Store the current selection
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]

        current_site.name = self.site_panel.model["name"]
        current_site.c1 = float(self.site_panel.model["c1"])
        current_site.c2 = float(self.site_panel.model["c2"])
        current_site.c3 = float(self.site_panel.model["c3"])

        self.tree_view.refresh_tree()
        self.tree_view.select_site(selected_uc_id, selected_site_id)

    def delete_site(self):
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        del self.unit_cells[selected_uc_id].sites[selected_site_id]
        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(selected_uc_id)

    def add_state(self):
        name = "New State"
        energy = 0
        new_state = State(name, energy)

        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]

        current_site.states[new_state.id] = new_state
        self.tree_view.refresh_tree()
        self.tree_view.select_state(selected_uc_id, selected_site_id, new_state.id)

    def save_state(self):
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_state = current_site.states[selected_state_id]

        current_state.name = self.state_panel.model["name"]
        current_state.energy = self.state_panel.model["energy"]

        self.tree_view.refresh_tree()
        self.tree_view.select_state(selected_uc_id, selected_site_id, selected_state_id)

    def delete_state(self):
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]
        del (
            self.unit_cells[selected_uc_id]
            .sites[selected_site_id]
            .states[selected_state_id]
        )
        self.tree_view.refresh_tree()
        self.tree_view.select_site(selected_uc_id, selected_site_id)
