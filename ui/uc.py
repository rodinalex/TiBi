from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QStackedWidget,
)
from models.uc_models import UCFormModel
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel
from ui.UC.tree_view import TreeViewPanel

from controllers.uc_cotroller import UCController

# Data Models
unit_cell_model = UCFormModel(
    name="New Unit Cell",
    v1x=1.0,
    v1y=0.0,
    v1z=0.0,
    v2x=0.0,
    v2y=1.0,
    v2z=0.0,
    v3x=0.0,
    v3y=0.0,
    v3z=1.0,
    sites={},
)

site_model = UCFormModel(name="New Site", c1=0.0, c2=0.0, c3=0.0, states={})
state_model = UCFormModel(name="New State", energy=0.0)

# Unit Cell collection
unit_cells = {}

selection = dict(unit_cell=None, site=None, state=None)
# selection = {"unit_cell": None, "site": None, "state": None}


class UnitCellUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Track currently selected items
        self.selection = selection

        # Initialize UI panels
        self.unit_cell_panel = UnitCellPanel(unit_cell_model)
        self.site_panel = SitePanel(site_model)
        self.state_panel = StatePanel(state_model)
        self.tree_view_panel = TreeViewPanel(unit_cells)

        # Initialize controller with tree view
        self.controller = UCController(
            unit_cells,
            self.unit_cell_panel,
            self.site_panel,
            self.state_panel,
            self.tree_view_panel,
            self.selection,
        )

        # Setup panel stack for dynamic content switching depending on the tree selection
        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self.unit_cell_panel)
        self.form_stack.addWidget(self.site_panel)
        self.form_stack.addWidget(self.state_panel)

        layout.addWidget(self.tree_view_panel, stretch=2)
        layout.addWidget(self.form_stack, stretch=1)

        # Connect tree view signals to show appropriate panels
        self.tree_view_panel.unit_cell_selected.connect(self.show_unit_cell_panel)
        self.tree_view_panel.site_selected.connect(self.show_site_panel)
        # self.tree_view_panel.state_selected.connect(self.show_state_panel)

        # Update panel forms whenever the models register an update
        unit_cell_model.signals.updated.connect(self.unit_cell_panel.update_ui)
        site_model.signals.updated.connect(self.site_panel.update_ui)
        state_model.signals.updated.connect(self.state_panel.update_ui)

    def show_unit_cell_panel(self, unit_cell_id):
        """Display the unit cell panel and load selected unit cell data"""
        # Save the current selection
        self.selection["unit_cell"] = unit_cell_id
        self.selection["site"] = None
        self.selection["state"] = None

        uc = unit_cells[unit_cell_id]
        # Update the model based on the selected element.
        # The corresponding update function to update the fields is fired automatically.
        unit_cell_model.update(
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
                "sites": uc.sites,
            }
        )
        self.form_stack.setCurrentWidget(self.unit_cell_panel)

    def show_site_panel(self, unit_cell_id, site_id):
        """Display the site panel and load selected site data"""
        # Save the current selection
        self.selection["unit_cell"] = unit_cell_id
        self.selection["site"] = site_id
        self.selection["state"] = None

        uc = unit_cells[unit_cell_id]
        site = uc.sites[site_id]

        # Update the form model
        # The corresponding update function to update the fields is fired automatically.
        site_model.update(
            {"name": site.name, "c1": site.c1, "c2": site.c2, "c3": site.c3}
        )
        self.form_stack.setCurrentWidget(self.site_panel)

    # def show_state_panel(self, unit_cell_id, site_id, state_id):
    #     """Display the state panel and load selected state data"""
    #     if unit_cell_id in unit_cells:
    #         uc = unit_cells[unit_cell_id]
    #         if site_id in uc.sites:
    #             site = uc.sites[site_id]
    #             if state_id in site.states:
    #                 # Save the current selection
    #                 self.current_unit_cell_id = unit_cell_id
    #                 self.current_site_id = site_id
    #                 self.current_state_id = state_id

    #                 state = site.states[state_id]
    #                 # Update the form model
    #                 state_model.update({"name": state.name, "energy": state.energy})
    #                 self.form_stack.setCurrentWidget(self.state_panel)
