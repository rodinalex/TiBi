from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QUndoStack
from PySide6.QtWidgets import QColorDialog
import uuid

from TiBi.logic.commands import (
    AddUnitCellCommand,
    AddSiteCommand,
    AddStateCommand,
    ChangeDimensionalityCommand,
    ChangeSiteColorCommand,
    DeleteItemCommand,
    ReduceBasisCommand,
    RenameTreeItemCommand,
    UpdateSiteParameterCommand,
    UpdateUnitCellParameterCommand,
)
from TiBi.models import Selection, UnitCell
from TiBi.views.widgets import EnterKeySpinBox
from TiBi.views.uc_view import UnitCellView


class UnitCellController(QObject):
    """
    Controller managing the `UnitCell`, `Site`, and `State` creation panel.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
    unit_cell_view : UnitCellView
        The main view component
    undo_stack : QUndoStack
        `QUndoStack` to hold "undo-able" commands
    v1, v2, v3 : list[EnterKeySpinBox]
        Lists of spinboxes for basis vector components
    R, c1, c2, c3 : EnterKeySpinBox
        Spinboxes for site properties
    tree_view_panel : TreeViewPanel
        The tree view panel component
    tree_view : SystemTree
        The tree view component
    tree_model : QStandardItemModel
        The model backing the tree view

    Methods
    -------
    refresh_tree()
        Refresh the system tree using the current state.
    select_item(uuid.UUID, uuid.UUID, uuid.UUID):
        Select a tree item using the ID's.

    Signals
    -------
    unit_cell_parameter_changed
        Signal emitted when a unit cell parameter is changed.
        This triggers a redraw of the panels orchestrated by
        the app_controller. Whenever unit cell parameter changes,
        the derived quantities (band structure, BZ grid, etc),
        are discarded due to being stale. The clearing is handled
        by the associated commands
    site_parameter_changed
        Signal emitted when a site parameter is changed.
        This triggers a redraw only of the unit cell plot.
        Changing site parameters does not invalidate the derived quantities
        since the site parameters are purely cosmetic.
    hopping_projection_update_requested
        Signal emitted when a tree item is renamed or the structure of the
        unit cell changes (adding/removing states), requiring
        an update of the hopping matrix and the projection selection.
    """

    unit_cell_parameter_changed = Signal()
    site_parameter_changed = Signal()
    hopping_projection_update_requested = Signal()

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        unit_cell_view: UnitCellView,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the controller and connect UI signals to handler methods.

        Parameters
        ----------
        unit_cells : dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
        unit_cell_view : UnitCellView
            The main view component
        undo_stack : QUndoStack
            `QUndoStack` to hold "undo-able" commands
        """
        super().__init__()
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
        # attributes for convenience
        self.tree_view_panel = self.unit_cell_view.tree_view_panel
        self.tree_view = self.tree_view_panel.tree_view
        self.tree_model = self.tree_view.tree_model

        # Rebuild the tree view from scratch in the beginning
        self.tree_view.refresh_tree(self.unit_cells)

        # SIGNALS
        # Selection change.
        self.selection.selection_changed.connect(self._show_panels)

        # Tree view signals
        # When the tree selection changes, the selection model is updated
        self.tree_view.tree_selection_changed.connect(
            lambda x: self.selection.set_selection(
                uc_id=x["unit_cell"], site_id=x["site"], state_id=x["state"]
            )
        )

        # Triggered when a tree item's name is changed by double clicking on it
        self.tree_view_panel.name_edit_finished.connect(
            lambda x: self.undo_stack.push(
                RenameTreeItemCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                    signal=self.hopping_projection_update_requested,
                    item=self.tree_model.itemFromIndex(x),
                )
            )
        )

        # Triggered when the user presses Del or Backspace while
        # a tree item is highlighted, or clicks the Delete button
        # The signal is emitted only when there are states that are deleted
        # (either directly or as part of a site). If a state is deleted,
        # derived quantities (bands, BZ grid, etc.) are discarded
        # due to being stale.
        # If a unit cell is deleted,
        # the signal is not emitted as the unit cell deletion changes the
        # selection, which is handled separately.
        self.tree_view_panel.delete_requested.connect(
            lambda: self.undo_stack.push(
                DeleteItemCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                    signal=self.hopping_projection_update_requested,
                )
            )
        )
        # New item creation using the tree delegate.
        self.tree_view_panel.new_unit_cell_requested.connect(
            lambda: self.undo_stack.push(
                AddUnitCellCommand(
                    unit_cells=self.unit_cells, tree_view=self.tree_view
                )
            )
        )

        self.tree_view_panel.new_site_requested.connect(
            lambda: self.undo_stack.push(
                AddSiteCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                )
            )
        )
        self.tree_view_panel.new_state_requested.connect(
            lambda: self.undo_stack.push(
                AddStateCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    tree_view=self.tree_view,
                    signal=self.hopping_projection_update_requested,
                )
            )
        )

        # Unit Cell basis vector signals. Emitted when the user confirms
        # the change in the corresponding field but pressing Enter.
        def connect_vector_fields(
            vector_name, spinboxes: list[EnterKeySpinBox]
        ):
            for ii, axis in enumerate("xyz"):
                spinboxes[ii].editingConfirmed.connect(
                    lambda ii=ii, axis=axis: self.undo_stack.push(
                        UpdateUnitCellParameterCommand(
                            unit_cells=self.unit_cells,
                            selection=self.selection,
                            vector=vector_name,
                            coordinate=axis,
                            spinbox=spinboxes[ii],
                            signal=self.unit_cell_parameter_changed,
                        )
                    )
                )

        # Connect the fields for the three basis vectors
        connect_vector_fields("v1", self.v1)
        connect_vector_fields("v2", self.v2)
        connect_vector_fields("v3", self.v3)

        # Dimensionality radio buttons
        self.radio_buttons = [
            self.unit_cell_view.unit_cell_panel.radio0D,
            self.unit_cell_view.unit_cell_panel.radio1D,
            self.unit_cell_view.unit_cell_panel.radio2D,
            self.unit_cell_view.unit_cell_panel.radio3D,
        ]
        # Dimensionality change signals from the radio buttons.
        # Changes in dimensionality trigger the same response
        # as in the basis vector coordinates.
        for dim, radio in enumerate(self.radio_buttons):
            radio.toggled.connect(
                lambda checked, d=dim: (
                    self.undo_stack.push(
                        ChangeDimensionalityCommand(
                            unit_cells=self.unit_cells,
                            selection=self.selection,
                            unit_cell_view=self.unit_cell_view,
                            signal=self.unit_cell_parameter_changed,
                            dim=d,
                            buttons=self.radio_buttons,
                        )
                    )
                    if checked
                    else None
                )
            )

        # Site panel signals.
        # Signals for fractional site coordinates.
        for param in ["c1", "c2", "c3"]:
            spinbox: EnterKeySpinBox = getattr(self, param)
            spinbox.editingConfirmed.connect(
                lambda p=param, s=spinbox: self.undo_stack.push(
                    UpdateSiteParameterCommand(
                        unit_cells=self.unit_cells,
                        selection=self.selection,
                        param=p,
                        spinbox=s,
                        signal=self.site_parameter_changed,
                    )
                )
            )

        # Site radius
        self.R.editingConfirmed.connect(
            lambda: self.undo_stack.push(
                UpdateSiteParameterCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    param="R",
                    spinbox=self.R,
                    signal=self.site_parameter_changed,
                )
            )
        )

        # Button signals
        # Reduce button--LLL argorithm to obtain the primitive cell.
        self.unit_cell_view.unit_cell_panel.reduce_btn.clicked.connect(
            lambda: self.undo_stack.push(
                ReduceBasisCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    unit_cell_view=self.unit_cell_view,
                    signal=self.unit_cell_parameter_changed,
                )
            )
        )
        # Opens a color picker to change the color of the selected site
        self.unit_cell_view.site_panel.color_picker_btn.clicked.connect(
            self._pick_site_color
        )

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
        unit_cell_id = self.selection.unit_cell
        site_id = self.selection.site
        if unit_cell_id:
            # Get the selected unit cell
            uc = self.unit_cells[unit_cell_id]

            # Get the system dimensionality
            dim = uc.v1.is_periodic + uc.v2.is_periodic + uc.v3.is_periodic
            # Set the dimensionality radio button.
            # Suppress the dim_listener since we are updating the radio
            # button programmatically
            for btn in self.radio_buttons:
                btn.blockSignals(True)
            self.unit_cell_view.unit_cell_panel.radio_group.button(
                dim
            ).setChecked(True)
            # Enable the coordinate fields depending on the dimensionality
            self.unit_cell_view.unit_cell_panel.v1[0].setEnabled(True)
            self.unit_cell_view.unit_cell_panel.v1[1].setEnabled(dim > 1)
            self.unit_cell_view.unit_cell_panel.v1[2].setEnabled(dim > 2)

            self.unit_cell_view.unit_cell_panel.v2[0].setEnabled(dim > 1)
            self.unit_cell_view.unit_cell_panel.v2[1].setEnabled(True)
            self.unit_cell_view.unit_cell_panel.v2[2].setEnabled(dim > 2)

            self.unit_cell_view.unit_cell_panel.v3[0].setEnabled(dim > 2)
            self.unit_cell_view.unit_cell_panel.v3[1].setEnabled(dim > 2)
            self.unit_cell_view.unit_cell_panel.v3[2].setEnabled(True)

            for btn in self.radio_buttons:
                btn.blockSignals(False)

            # Set the basis vector fields
            self.unit_cell_view.unit_cell_panel.set_basis_vectors(
                uc.v1, uc.v2, uc.v3
            )

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
        Open a color dialog to select a color for the selected site.

        After the color is picked, an undoable command is issued.
        """
        old_color = (
            self.unit_cells[self.selection.unit_cell]
            .sites[self.selection.site]
            .color
        )

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
            self.undo_stack.push(
                ChangeSiteColorCommand(
                    unit_cells=self.unit_cells,
                    selection=self.selection,
                    new_color=new_color,
                    old_color=start_color,
                    unit_cell_view=self.unit_cell_view,
                    signal=self.site_parameter_changed,
                )
            )

    def refresh_tree(self):
        """
        Refresh the system tree using the current state.
        """
        self.tree_view.refresh_tree(self.unit_cells)

    def select_item(self, uc_id, site_id, state_id):
        """
        Select a tree item using the ID's.
        """
        self.tree_view._select_item_by_id(uc_id, site_id, state_id)
