from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from models.uc_models import DataModel
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel
from ui.UC.tree_view_panel import TreeViewPanel
from ui.placeholder import PlaceholderWidget


from controllers.uc_cotroller import UCController


class UnitCellUI(QWidget):
    """
    Main UI component for managing unit cells, sites, and states.

    This widget combines a tree view of the unit cell hierarchy with dynamically
    swappable panels for editing properties of the selected tree node. It handles
    the data models and coordinates interactions between the tree view and detail panels.

    The UI consists of two main parts:
    1. Tree view panel showing the hierarchy of unit cells, sites, and states
    2. Form panel that changes depending on what is selected in the tree
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Initialize the data models for fields and tick boxes
        self.unit_cell_model = DataModel(
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
            v1periodic=False,
            v2periodic=False,
            v3periodic=False,
        )

        self.site_model = DataModel(name="New Site", c1=0.0, c2=0.0, c3=0.0)
        self.state_model = DataModel(name="New State", energy=0.0)

        # Track currently selected items
        self.selection = DataModel(unit_cell=None, site=None, state=None)

        # Existing unit cells
        self.unit_cells = {}

        # Initialize UI panels
        self.unit_cell_panel = UnitCellPanel(self.unit_cell_model)
        self.site_panel = SitePanel(self.site_model)
        self.state_panel = StatePanel(self.state_model)
        self.tree_view_panel = TreeViewPanel(
            self.unit_cells, self.unit_cell_panel, self.site_panel, self.state_panel
        )

        # Initialize controller
        self.controller = UCController(
            self.unit_cells,
            self.unit_cell_panel,
            self.site_panel,
            self.state_panel,
            self.tree_view_panel,
            self.selection,
        )

        # Info label
        self.info_label = QLabel("Add/Select a Unit Cell")
        self.info_label.setAlignment(Qt.AlignCenter)

        # Setup panel stack for dynamic content switching depending on the tree selection.
        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self.info_label)
        self.form_stack.addWidget(self.unit_cell_panel)
        self.form_stack.addWidget(self.site_panel)
        self.form_stack.addWidget(self.state_panel)

        # Create the interface

        top_panel = QHBoxLayout()
        top_panel.addWidget(self.tree_view_panel, stretch=2)
        top_panel.addWidget(PlaceholderWidget("Tst"), stretch=1)

        layout.addLayout(top_panel, stretch=3)
        layout.addWidget(self.form_stack, stretch=1)

        # Connect tree view signals to show appropriate panels
        self.tree_view_panel.none_selected.connect(self.show_info_panel)
        self.tree_view_panel.unit_cell_selected.connect(self.show_unit_cell_panel)
        self.tree_view_panel.site_selected.connect(self.show_site_panel)
        self.tree_view_panel.state_selected.connect(self.show_state_panel)

        # Save data whenever the models register an update
        self.unit_cell_model.signals.updated.connect(self.controller.save_unit_cell)
        self.site_model.signals.updated.connect(self.controller.save_site)
        self.state_model.signals.updated.connect(self.controller.save_state)

        # Update panel forms whenever the models register an update
        self.unit_cell_model.signals.updated.connect(self.unit_cell_panel.update_ui)
        self.site_model.signals.updated.connect(self.site_panel.update_ui)
        self.state_model.signals.updated.connect(self.state_panel.update_ui)

    def show_info_panel(self):
        """Display the info panel and deselect all"""
        self.selection["unit_cell"] = None
        self.selection["site"] = None
        self.selection["state"] = None
        self.form_stack.setCurrentWidget(self.info_label)

    def show_unit_cell_panel(self, unit_cell_id):
        """
        Display the unit cell panel and load selected unit cell data.

        This method is called when a unit cell is selected in the tree view.
        It updates the selection model, populates the unit cell form with data
        from the selected unit cell, and switches the stacked widget to show
        the unit cell editing panel.

        The reactive data binding system ensures that when the model is updated,
        the UI components are automatically refreshed to match.

        Args:
            unit_cell_id: UUID of the selected unit cell
        """
        # Update the current selection state
        self.selection["unit_cell"] = unit_cell_id
        self.selection["site"] = None
        self.selection["state"] = None

        # Get the selected unit cell
        uc = self.unit_cells[unit_cell_id]

        # Update the form model with all unit cell properties
        # The form will automatically update due to the reactive data binding
        self.unit_cell_model.update(
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
        # Switch to the unit cell panel
        self.form_stack.setCurrentWidget(self.unit_cell_panel)

    def show_site_panel(self, unit_cell_id, site_id):
        """Display the site panel and load selected site data"""
        # Save the current selection
        self.selection["unit_cell"] = unit_cell_id
        self.selection["site"] = site_id
        self.selection["state"] = None

        uc = self.unit_cells[unit_cell_id]
        site = uc.sites[site_id]
        # Update the form model
        # The corresponding update function to update the fields is fired automatically.
        self.site_model.update(
            {
                "name": site.name,
                "c1": site.c1,
                "c2": site.c2,
                "c3": site.c3,
            }
        )
        # Set the appropriate panel
        self.form_stack.setCurrentWidget(self.site_panel)

    def show_state_panel(self, unit_cell_id, site_id, state_id):
        """Display the state panel and load selected state data"""
        # Save the current selection
        self.selection["unit_cell"] = unit_cell_id
        self.selection["site"] = site_id
        self.selection["state"] = state_id

        uc = self.unit_cells[unit_cell_id]
        site = uc.sites[site_id]
        state = site.states[state_id]

        # Update the form model
        # The corresponding update function to update the fields is fired automatically.
        self.state_model.update({"name": state.name, "energy": state.energy})
        self.form_stack.setCurrentWidget(self.state_panel)
