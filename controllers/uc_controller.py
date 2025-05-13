from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QUndoStack
from PySide6.QtWidgets import QColorDialog
import uuid

from commands.uc_commands import (
    AddUnitCellCommand,
    AddSiteCommand,
    AddStateCommand,
    ChangeDimensionalityCommand,
    DeleteItemCommand,
    ReduceBasisCommand,
    RenameTreeItemCommand,
    UpdateSiteParameterCommand,
    UpdateUnitCellParameterCommand,
)
from models.data_models import DataModel
from resources.ui_elements import EnterKeySpinBox
from src.tibitypes import UnitCell
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
        unit_cell_view: UnitCellView,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the controller and connect UI signals to handler methods.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: DataModel tracking the currently selected
            unit cell, site, and state
            unit_cell_view: The main view component containing
            tree view and form panels
            undo_stack: QUndoStack to hold "undo-able" commands
        """
        super().__init__()
        # Store references to UI components and data models
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_view = unit_cell_view
        self.undo_stack = undo_stack

        # Get the fields from unit_cell_view for convenience
        # For the basis vectors, each reference has three spinboxes
        # corresponding to the Cartesian coordinates
        # Unit Cell fields
        self.v1 = self.unit_cell_view.unit_cell_panel.v1
        self.v2 = self.unit_cell_view.unit_cell_panel.v2
        self.v3 = self.unit_cell_view.unit_cell_panel.v3

        # Site fields
        self.R = self.unit_cell_view.site_panel.R
        self.c1 = self.unit_cell_view.site_panel.c1
        self.c2 = self.unit_cell_view.site_panel.c2
        self.c3 = self.unit_cell_view.site_panel.c3

        # Store the tree_view_panel, tree_view and tree_model as
        # parameters for convenience
        self.tree_view_panel = self.unit_cell_view.tree_view_panel
        self.tree_view = self.tree_view_panel.tree_view
        self.tree_model = self.tree_view.tree_model

        # Rebuild the tree view from scratch in the beginning
        self.tree_view.refresh_tree(self.unit_cells)

        # SIGNALS
        # Selection change. Triggered by the change of the selection model
        # to show the appropriate panels and plots
        self.selection.signals.updated.connect(self._show_panels)

        # Tree view signals
        # Triggered when the tree selection changed.
        # Updates the selection dictionary
        self.tree_view.tree_selection_changed.connect(
            lambda x: self.selection.update(x)
        )

        # Triggered when a tree item's name is changed by double clicking on it
        self.tree_view_panel.delegate.name_edit_finished.connect(
            lambda x: self.undo_stack.push(
                RenameTreeItemCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                    signal=self.item_changed,
                    item=self.tree_model.itemFromIndex(x),
                )
            )
        )

        # Triggered when the user presses Del or Backspace while
        # a tree item is highlighted, or clicks the Delete button
        self.unit_cell_view.tree_view_panel.delete_requested.connect(
            lambda: self.undo_stack.push(
                DeleteItemCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                )
            )
        )

        # Unit Cell basis vector signals.
        def connect_vector_fields(
            vector_name, spinboxes: list[EnterKeySpinBox]
        ):
            for ii, axis in enumerate("xyz"):
                spinboxes[ii].editingConfirmed.connect(
                    lambda ii=ii, axis=axis: self.undo_stack.push(
                        UpdateUnitCellParameterCommand(
                            controller=self,
                            vector=vector_name,
                            coordinate=axis,
                            spinbox=spinboxes[ii],
                        )
                    )
                )

        connect_vector_fields("v1", self.v1)
        connect_vector_fields("v2", self.v2)
        connect_vector_fields("v3", self.v3)

        # Dimensionality radio buttons
        self.unit_cell_view.unit_cell_panel.radio0D.toggled.connect(
            lambda: self.undo_stack.push(
                ChangeDimensionalityCommand(controller=self, dim=0)
            )
        )
        self.unit_cell_view.unit_cell_panel.radio1D.toggled.connect(
            lambda: self.undo_stack.push(
                ChangeDimensionalityCommand(controller=self, dim=1)
            )
        )
        self.unit_cell_view.unit_cell_panel.radio2D.toggled.connect(
            lambda: self.undo_stack.push(
                ChangeDimensionalityCommand(controller=self, dim=2)
            )
        )
        self.unit_cell_view.unit_cell_panel.radio3D.toggled.connect(
            lambda: self.undo_stack.push(
                ChangeDimensionalityCommand(controller=self, dim=3)
            )
        )

        # Site panel signals.
        # Site fractional coordinates
        self.c1.editingConfirmed.connect(
            lambda: self.undo_stack.push(
                UpdateSiteParameterCommand(
                    controller=self, param="c1", spinbox=self.c1
                )
            )
        )
        self.c2.editingConfirmed.connect(
            lambda: self.undo_stack.push(
                UpdateSiteParameterCommand(
                    controller=self, param="c2", spinbox=self.c2
                )
            )
        )
        self.c3.editingConfirmed.connect(
            lambda: self.undo_stack.push(
                UpdateSiteParameterCommand(
                    controller=self, param="c3", spinbox=self.c3
                )
            )
        )
        self.R.editingConfirmed.connect(
            lambda: self.undo_stack.push(
                UpdateSiteParameterCommand(
                    controller=self, param="R", spinbox=self.R
                )
            )
        )

        # Button signals
        # New UC button
        self.unit_cell_view.tree_view_panel.new_uc_btn.clicked.connect(
            lambda: self.undo_stack.push(
                AddUnitCellCommand(
                    unit_cells=self.unit_cells, tree_view=self.tree_view
                )
            )
        )
        # New Site button
        self.unit_cell_view.unit_cell_panel.new_site_btn.clicked.connect(
            lambda: self.undo_stack.push(
                AddSiteCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                )
            )
        )
        # New State button
        self.unit_cell_view.site_panel.new_state_btn.clicked.connect(
            lambda: self.undo_stack.push(
                AddStateCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                )
            )
        )
        # Delete button--deletes the highlighted tree item
        self.unit_cell_view.tree_view_panel.delete_btn.clicked.connect(
            lambda: self.undo_stack.push(
                DeleteItemCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                )
            )
        )
        # Reduce button--LLL argorithm to obtain the primitive cell
        self.unit_cell_view.unit_cell_panel.reduce_btn.clicked.connect(
            lambda: self.undo_stack.push(ReduceBasisCommand(controller=self))
        )
        # Opens a color picker to change the color of the selected site
        self.unit_cell_view.site_panel.color_picker_btn.clicked.connect(
            self._pick_site_color
        )

    # Unit Cell/Site/State Modification Functions

    def _show_panels(self):
        """
        Update the UI panels based on the current selection state.

        This method is called whenever the selection changes. It determines
        which panels should be visible and populates them with data from
        the selected items.
        The panels are shown or hidden using a stacked widget approach.

        The method handles all three levels of the hierarchy:
        - When a unit cell is selected, its properties are shown in
        the unit cell panel
        - When a site is selected, its properties are shown in the site panel
        - When a state is selected, no additional panel is shown as the state
        is only described by its name

        Buttons are also enabled/disabled based on the selection context.
        """

        unit_cell_id = self.selection.get("unit_cell", None)
        site_id = self.selection.get("site", None)

        if unit_cell_id:
            # Get the selected unit cell
            uc = self.unit_cells[unit_cell_id]

            # Get the system dimensionality
            dim = uc.v1.is_periodic + uc.v2.is_periodic + uc.v3.is_periodic
            # Set the dimensionality radio button.
            # Suppress the dim_listener since we are updating the radio
            # button programmatically
            self.unit_cell_view.unit_cell_panel.radio_group.button(
                dim
            ).setChecked(True)

            # Set the basis vector fields
            self.v1[0].setValue(uc.v1.x)
            self.v1[1].setValue(uc.v1.y)
            self.v1[2].setValue(uc.v1.z)

            self.v2[0].setValue(uc.v2.x)
            self.v2[1].setValue(uc.v2.y)
            self.v2[2].setValue(uc.v2.z)

            self.v3[0].setValue(uc.v3.x)
            self.v3[1].setValue(uc.v3.y)
            self.v3[2].setValue(uc.v3.z)

            # Show the UnitCellPanel
            self.unit_cell_view.uc_stack.setCurrentWidget(
                self.unit_cell_view.unit_cell_panel
            )

            if site_id:
                site = uc.sites[site_id]
                # Set the fractional coordinates and radius fields
                self.c1.setValue(site.c1)
                self.c2.setValue(site.c2)
                self.c3.setValue(site.c3)
                self.R.setValue(site.R)

                # Set the color for the color picker button
                site_color = site.color

                c = (
                    int(site_color[0] * 255),
                    int(site_color[1] * 255),
                    int(site_color[2] * 255),
                    int(site_color[3] * 255),
                )  # Color in 0-255 component range

                self.unit_cell_view.site_panel.color_picker_btn.setStyleSheet(
                    f"background-color: rgba({c[0]}, {c[1]}, {c[2]}, {c[3]});"
                )

                # Show the SitePanel
                self.unit_cell_view.site_stack.setCurrentWidget(
                    self.unit_cell_view.site_panel
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

            rgba = (
                f"rgba({new_color.red()}, "
                f"{new_color.green()}, "
                f"{new_color.blue()}, "
                f"{new_color.alpha()})"
            )
            self.unit_cell_view.site_panel.color_picker_btn.setStyleSheet(
                f"background-color: {rgba};"
            )

            # Update the color in the dictionary (0-1 scale)
            self.unit_cells[self.selection["unit_cell"]].site_colors[
                self.selection["site"]
            ] = (
                new_color.redF(),
                new_color.greenF(),
                new_color.blueF(),
                new_color.alphaF(),
            )
            self.plot_update_requested.emit()
