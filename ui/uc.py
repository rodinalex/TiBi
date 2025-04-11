from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from models.uc_models import DataModel
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.tree_view_panel import TreeViewPanel
from ui.UC.button_panel import ButtonPanel

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
        self.state_model = DataModel(name="New State")

        # Track currently selected items
        self.selection = DataModel(unit_cell=None, site=None, state=None)

        # Existing unit cells
        self.unit_cells = {}

        # Initialize UI panels
        self.unit_cell_panel = UnitCellPanel(self.unit_cell_model)
        self.site_panel = SitePanel(self.site_model)
        self.tree_view_panel = TreeViewPanel(
            self.unit_cells,
            self.unit_cell_model,
            self.site_model,
            self.state_model,
        )
        self.button_panel = ButtonPanel()
        # Initialize controller
        self.controller = UCController(
            self.unit_cells,
            self.tree_view_panel,
            self.button_panel,
            self.selection,
        )

        # Info labels
        self.uc_info_label = QLabel("Add/Select a Unit Cell")
        self.uc_info_label.setAlignment(Qt.AlignCenter)

        self.site_info_label = QLabel("Add/Select a Site")
        self.site_info_label.setAlignment(Qt.AlignCenter)

        # Panel stacks
        self.uc_stack = QStackedWidget()
        self.uc_stack.addWidget(self.uc_info_label)
        self.uc_stack.addWidget(self.unit_cell_panel)

        self.site_stack = QStackedWidget()
        self.site_stack.addWidget(self.site_info_label)
        self.site_stack.addWidget(self.site_panel)

        # Create the interface

        top_panel = QHBoxLayout()
        top_panel.addWidget(self.tree_view_panel, stretch=2)
        top_panel.addWidget(self.button_panel, stretch=1)

        layout.addLayout(top_panel, stretch=6)
        layout.addWidget(self.uc_stack, stretch=2)
        layout.addWidget(self.site_stack, stretch=1)
        layout.setSpacing(5)

        # Connect tree view signals to show appropriate panels
        self.tree_view_panel.selection_changed_signal.connect(self.show_panels)

        # Save data whenever the models register an update
        self.unit_cell_model.signals.updated.connect(self.controller.save_unit_cell)
        self.site_model.signals.updated.connect(self.controller.save_site)
        self.state_model.signals.updated.connect(self.controller.save_state)

        # Update panel forms whenever the models register an update
        self.unit_cell_model.signals.updated.connect(self.unit_cell_panel.update_ui)
        self.site_model.signals.updated.connect(self.site_panel.update_ui)

    def show_panels(self, unit_cell_id, site_id, state_id):
        self.selection["unit_cell"] = unit_cell_id
        self.selection["site"] = site_id
        self.selection["state"] = state_id

        if unit_cell_id:
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
            self.uc_stack.setCurrentWidget(self.unit_cell_panel)
            self.button_panel.new_site_btn.setEnabled(True)
            if site_id:
                site = uc.sites[site_id]
                # Update the form model with all site properties
                # The corresponding update function to update the fields is fired automatically.
                self.site_model.update(
                    {
                        "name": site.name,
                        "c1": site.c1,
                        "c2": site.c2,
                        "c3": site.c3,
                    }
                )
                self.site_stack.setCurrentWidget(self.site_panel)
                self.button_panel.new_state_btn.setEnabled(True)

                if state_id:
                    state = site.states[state_id]

                    # Update the form model with the state properties
                    # The corresponding update function to update the fields is fired automatically.
                    self.state_model.update(
                        {
                            "name": state.name,
                        }
                    )
            else:
                self.site_stack.setCurrentWidget(self.site_info_label)
                self.button_panel.new_state_btn.setEnabled(False)
        else:
            self.uc_stack.setCurrentWidget(self.uc_info_label)
            self.button_panel.new_site_btn.setEnabled(False)
            self.button_panel.new_state_btn.setEnabled(False)
