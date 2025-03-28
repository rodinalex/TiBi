import uuid
from PySide6.QtCore import QObject, Signal
from src.tibitypes import UnitCell, Site, State, BasisVector
from ui.UC.tree_view import TreeViewPanel

# from models.uc_models import UCFormModel
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel


class UCController(QObject):
    """Controller to manage UnitCells, Sites, and States with tree view integration."""

    # Define signals
    model_updated = Signal()

    def __init__(
        self,
        model: dict[uuid.UUID, UnitCell],  # All the unit cells in the system
        unit_cell_panel: UnitCellPanel,
        site_panel: SitePanel,
        state_panel: StatePanel,
        tree_view: TreeViewPanel,
        selection,
    ):
        super().__init__()
        self.model = model
        self.unit_cell_panel = unit_cell_panel
        self.site_panel = site_panel
        self.state_panel = state_panel
        self.tree_view = tree_view
        self.selection = selection

        # Connect UI signals
        self.tree_view.add_unit_cell_btn.clicked.connect(self.add_unit_cell)
        self.unit_cell_panel.save_btn.clicked.connect(self.save_unit_cell)
        self.unit_cell_panel.delete_btn.clicked.connect(self.delete_unit_cell)

    def add_unit_cell(self):
        name = "New Unit Cell"
        v1 = BasisVector(1, 0, 0)
        v2 = BasisVector(0, 1, 0)
        v3 = BasisVector(0, 0, 1)
        new_cell = UnitCell(name, v1, v2, v3)
        self.model[new_cell.id] = new_cell
        new_cell_id = new_cell.id
        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(new_cell_id)

    def save_unit_cell(self):
        # Store current selection
        selected_id = self.selection["unit_cell"]

        name = self.unit_cell_panel.model["name"]
        v1 = BasisVector(
            float(self.unit_cell_panel.model["v1x"]),
            float(self.unit_cell_panel.model["v1y"]),
            float(self.unit_cell_panel.model["v1z"]),
        )
        v2 = BasisVector(
            float(self.unit_cell_panel.model["v2x"]),
            float(self.unit_cell_panel.model["v2y"]),
            float(self.unit_cell_panel.model["v2z"]),
        )
        v3 = BasisVector(
            float(self.unit_cell_panel.model["v3x"]),
            float(self.unit_cell_panel.model["v3y"]),
            float(self.unit_cell_panel.model["v3z"]),
        )
        sites = self.unit_cell_panel.model["sites"]
        id = self.selection["unit_cell"]
        updated_uc = UnitCell(name, v1, v2, v3, sites, id)
        self.model[updated_uc.id] = updated_uc
        self.tree_view.refresh_tree()
        self.tree_view.select_unit_cell(selected_id)

    def delete_unit_cell(self):
        del self.model[self.selection["unit_cell"]]
        self.tree_view.refresh_tree()

    # def add_unit_cell(self, name="New Unit Cell"):
    #     """Add a new unit cell to the model"""
    #     v1 = BasisVector(1, 0, 0)
    #     v2 = BasisVector(0, 1, 0)
    #     v3 = BasisVector(0, 0, 1)

    #     new_cell = UnitCell(name, v1, v2, v3)
    #     self.model[new_cell.id] = new_cell

    #     if self.tree_view:
    #         self.tree_view.add_unit_cell_item(new_cell)

    #     self.model_updated.emit()
    #     return new_cell.id

    # def edit_unit_cell(
    #     self, unit_cell_id: uuid.UUID, name=None, v1=None, v2=None, v3=None
    # ):
    #     """Edit an existing unit cell"""
    #     if unit_cell_id not in self.model:
    #         return False

    #     unit_cell = self.model[unit_cell_id]

    #     if name is not None:
    #         unit_cell.name = name

    #     if v1 is not None:
    #         unit_cell.v1 = v1

    #     if v2 is not None:
    #         unit_cell.v2 = v2

    #     if v3 is not None:
    #         unit_cell.v3 = v3

    #     if self.tree_view:
    #         self.tree_view.refresh_tree()

    #     self.model_updated.emit()
    #     return True

    # def delete_unit_cell(self, unit_cell_id: uuid.UUID):
    #     """Delete a unit cell from the model"""
    #     if unit_cell_id not in self.model:
    #         return False

    #     del self.model[unit_cell_id]

    #     if self.tree_view:
    #         self.tree_view.refresh_tree()

    #     self.model_updated.emit()
    #     return True

    # def add_site(
    #     self, unit_cell_id: uuid.UUID, name="New Site", c1=0.0, c2=0.0, c3=0.0
    # ):
    #     """Add a new site to a unit cell"""
    #     if unit_cell_id not in self.model:
    #         return None

    #     unit_cell = self.model[unit_cell_id]
    #     new_site = Site(name, c1, c2, c3)
    #     unit_cell.sites[new_site.id] = new_site

    #     if self.tree_view:
    #         self.tree_view.add_site_item(unit_cell_id, new_site)

    #     self.model_updated.emit()
    #     return new_site.id

    # def edit_site(
    #     self,
    #     unit_cell_id: uuid.UUID,
    #     site_id: uuid.UUID,
    #     name=None,
    #     c1=None,
    #     c2=None,
    #     c3=None,
    # ):
    #     """Edit an existing site"""
    #     if unit_cell_id not in self.model:
    #         return False

    #     unit_cell = self.model[unit_cell_id]

    #     if site_id not in unit_cell.sites:
    #         return False

    #     site = unit_cell.sites[site_id]

    #     if name is not None:
    #         site.name = name

    #     if c1 is not None:
    #         site.c1 = c1

    #     if c2 is not None:
    #         site.c2 = c2

    #     if c3 is not None:
    #         site.c3 = c3

    #     if self.tree_view:
    #         self.tree_view.refresh_tree()

    #     self.model_updated.emit()
    #     return True

    # def delete_site(self, unit_cell_id: uuid.UUID, site_id: uuid.UUID):
    #     """Delete a site from a unit cell"""
    #     if unit_cell_id not in self.model:
    #         return False

    #     unit_cell = self.model[unit_cell_id]

    #     if site_id not in unit_cell.sites:
    #         return False

    #     del unit_cell.sites[site_id]

    #     if self.tree_view:
    #         self.tree_view.refresh_tree()

    #     self.model_updated.emit()
    #     return True

    # def add_state(
    #     self, unit_cell_id: uuid.UUID, site_id: uuid.UUID, name="New State", energy=0.0
    # ):
    #     """Add a new state to a site"""
    #     if unit_cell_id not in self.model:
    #         return None

    #     unit_cell = self.model[unit_cell_id]

    #     if site_id not in unit_cell.sites:
    #         return None

    #     site = unit_cell.sites[site_id]
    #     new_state = State(name, energy)
    #     site.states[new_state.id] = new_state

    #     if self.tree_view:
    #         self.tree_view.add_state_item(unit_cell_id, site_id, new_state)

    #     self.model_updated.emit()
    #     return new_state.id

    # def edit_state(
    #     self,
    #     unit_cell_id: uuid.UUID,
    #     site_id: uuid.UUID,
    #     state_id: uuid.UUID,
    #     name=None,
    #     energy=None,
    # ):
    #     """Edit an existing state"""
    #     if unit_cell_id not in self.model:
    #         return False

    #     unit_cell = self.model[unit_cell_id]

    #     if site_id not in unit_cell.sites:
    #         return False

    #     site = unit_cell.sites[site_id]

    #     if state_id not in site.states:
    #         return False

    #     state = site.states[state_id]

    #     if name is not None:
    #         state.name = name

    #     if energy is not None:
    #         state.energy = energy

    #     if self.tree_view:
    #         self.tree_view.refresh_tree()

    #     self.model_updated.emit()
    #     return True

    # def delete_state(
    #     self, unit_cell_id: uuid.UUID, site_id: uuid.UUID, state_id: uuid.UUID
    # ):
    #     """Delete a state from a site"""
    #     if unit_cell_id not in self.model:
    #         return False

    #     unit_cell = self.model[unit_cell_id]

    #     if site_id not in unit_cell.sites:
    #         return False

    #     site = unit_cell.sites[site_id]

    #     if state_id not in site.states:
    #         return False

    #     del site.states[state_id]

    #     if self.tree_view:
    #         self.tree_view.refresh_tree()

    #     self.model_updated.emit()
    #     return True
