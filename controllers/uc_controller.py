from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QUndoStack
from PySide6.QtWidgets import QColorDialog, QDoubleSpinBox
import uuid

from commands.uc_commands import (
    AddUnitCellCommand,
    AddSiteCommand,
    AddStateCommand,
    DeleteItemCommand,
    RenameTreeItemCommand,
)
from models.data_models import DataModel
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
        unit_cell_data: DataModel,
        unit_cell_view: UnitCellView,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the controller and connect UI signals to handler methods.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: DataModel tracking the currently selected
            unit cell, site, and state
            unit_cell_data: DataModel tracking the parameters of
            the selected unit cell and site
            unit_cell_view: The main view component containing
            tree view and form panels
            undo_stack: QUndoStack to hold "undo-able" commands
        """
        super().__init__()
        # Store references to UI components and data models
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_data = unit_cell_data
        self.unit_cell_view = unit_cell_view
        self.undo_stack = undo_stack

        # Get the fields from unit_cell_view for convenience
        # For the basis vectors, each reference has three spinboxes
        # corresponding to the Cartesian coordinates
        self.v1 = self.unit_cell_view.unit_cell_panel.v1
        self.v2 = self.unit_cell_view.unit_cell_panel.v2
        self.v3 = self.unit_cell_view.unit_cell_panel.v3

        self.R = self.unit_cell_view.site_panel.R
        self.c1 = self.unit_cell_view.site_panel.c1
        self.c2 = self.unit_cell_view.site_panel.c2
        self.c3 = self.unit_cell_view.site_panel.c3

        # Store the tree_view and tree_model as parameters for convenience
        self.tree_view = self.unit_cell_view.tree_view_panel.tree_view
        self.tree_model = (
            self.unit_cell_view.tree_view_panel.tree_view.tree_model
        )

        # A flag to suppress the change of dimensionality listener.
        # Used when the dimensionality radio buttons are triggered
        # programmatically to avoid unnecessary update cycles.
        self._suppress_dim_listener = False
        # Rebuild the tree view from scratch in the beginning
        self.tree_view.refresh_tree({})

        # Sync UI with data models
        self._update_unit_cell_ui()

        # Connect signals
        # Tree view signals
        # Triggered when the tree selection changed,
        # either manually or programmatically
        self.tree_view.tree_selection_changed.connect(
            lambda x: self.selection.update(x)
        )
        # Triggered when a tree item's name is changed by double clicking on it
        self.tree_model.itemChanged.connect(
            lambda x: self.undo_stack.push(
                RenameTreeItemCommand(controller=self, item=x)
            )
        )
        # Triggered when the user presses Del or Backspace while
        # a tree item is highlighted, or clicks the Delete button
        self.unit_cell_view.tree_view_panel.delete_requested.connect(
            lambda: self.undo_stack.push(DeleteItemCommand(controller=self))
        )

        # Unit Cell basis vector signals.
        def connect_vector_fields(
            vector_name, spinboxes: list[QDoubleSpinBox]
        ):
            for ii, axis in enumerate("xyz"):
                spinboxes[ii].editingFinished.connect(
                    lambda ii=ii, axis=axis: self._update_unit_cell_data(
                        f"{vector_name}{axis}", spinboxes[ii].value()
                    )
                )

        connect_vector_fields("v1", self.v1)
        connect_vector_fields("v2", self.v2)
        connect_vector_fields("v3", self.v3)

        # Dimensionality radio buttons
        self.unit_cell_view.unit_cell_panel.radio0D.toggled.connect(
            self._dimensionality_change
        )
        self.unit_cell_view.unit_cell_panel.radio1D.toggled.connect(
            self._dimensionality_change
        )
        self.unit_cell_view.unit_cell_panel.radio2D.toggled.connect(
            self._dimensionality_change
        )
        self.unit_cell_view.unit_cell_panel.radio3D.toggled.connect(
            self._dimensionality_change
        )

        # Site panel signals.
        # Site Radius
        self.R.editingFinished.connect(lambda: self._update_site_size())

        # Site fractional coordinates
        self.c1.editingFinished.connect(
            lambda: self._update_site_data("c1", self.c1.value())
        )
        self.c2.editingFinished.connect(
            lambda: self._update_site_data("c2", self.c2.value())
        )
        self.c3.editingFinished.connect(
            lambda: self._update_site_data("c3", self.c3.value())
        )

        # Button signals
        # New UC button
        self.unit_cell_view.tree_view_panel.new_uc_btn.clicked.connect(
            lambda: self.undo_stack.push(AddUnitCellCommand(controller=self))
        )
        # New Site button
        self.unit_cell_view.unit_cell_panel.new_site_btn.clicked.connect(
            lambda: self.undo_stack.push(AddSiteCommand(controller=self))
        )
        # New State button
        self.unit_cell_view.site_panel.new_state_btn.clicked.connect(
            lambda: self.undo_stack.push(AddStateCommand(controller=self))
        )
        # Delete button--deletes the highlighted tree item
        self.unit_cell_view.tree_view_panel.delete_btn.clicked.connect(
            lambda: self.undo_stack.push(DeleteItemCommand(controller=self))
        )
        # Reduce button--LLL argorithm to obtain the primitive cell
        self.unit_cell_view.unit_cell_panel.reduce_btn.clicked.connect(
            self._reduce_uc_basis
        )
        # Opens a color picker to change the color of the selected site
        self.unit_cell_view.site_panel.color_picker_btn.clicked.connect(
            self._pick_site_color
        )

        # Selection change. Triggered by the change of the selection model
        # to show the appropriate panels and plots
        self.selection.signals.updated.connect(self._show_panels)

        # When model changes, update UI. If the model changes
        # programmatically, the updates fill out the relevant fields
        self.unit_cell_data.signals.updated.connect(self._update_unit_cell_ui)

    # Unit Cell/Site/State Modification Functions
    def _save_unit_cell(self):
        """
        Save changes from the unit cell data model to the selected unit cell.

        This method is automatically triggered when the unit_cell_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        Because the updates in the fields do not change the unit cell name,
        there is no update required for the tree.
        """
        # Get the currently selected unit cell
        selected_uc_id = self.selection["unit_cell"]
        current_uc = self.unit_cells[selected_uc_id]

        # Update name and basic properties
        current_uc.name = self.unit_cell_data["unit_cell_name"]

        # Update first basis vector (v1)
        current_uc.v1.x = float(self.unit_cell_data["v1x"])
        current_uc.v1.y = float(self.unit_cell_data["v1y"])
        current_uc.v1.z = float(self.unit_cell_data["v1z"])
        current_uc.v1.is_periodic = self.unit_cell_data["v1periodic"]

        # Update second basis vector (v2)
        current_uc.v2.x = float(self.unit_cell_data["v2x"])
        current_uc.v2.y = float(self.unit_cell_data["v2y"])
        current_uc.v2.z = float(self.unit_cell_data["v2z"])
        current_uc.v2.is_periodic = self.unit_cell_data["v2periodic"]

        # Update third basis vector (v3)
        current_uc.v3.x = float(self.unit_cell_data["v3x"])
        current_uc.v3.y = float(self.unit_cell_data["v3y"])
        current_uc.v3.z = float(self.unit_cell_data["v3z"])
        current_uc.v3.is_periodic = self.unit_cell_data["v3periodic"]

        # After unit cell object is updated, notify plot controllers
        self.plot_update_requested.emit()

    def _save_site(self):
        """
        Save changes from the site data model to the selected site.

        This method is automatically triggered when the site_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        Because the updates in the fields do not change the site name,
        there is no update required for the tree.
        """
        # Get the currently selected site
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]

        # Update site properties
        current_site.name = self.unit_cell_data["site_name"]
        current_site.c1 = float(self.unit_cell_data["c1"])
        current_site.c2 = float(self.unit_cell_data["c2"])
        current_site.c3 = float(self.unit_cell_data["c3"])

        # After site object is updated, notify plot controllers
        self.plot_update_requested.emit()

    def _save_state(self):
        """
        Save changes from the state data model to the selected state.

        This method is automatically triggered when the site_data model
        emits an updated signal following a user interaction, ensuring that UI
        changes are immediately reflected in the underlying data model.
        Because the updates in the fields do not change the state name,
        there is no update required for the tree.
        """
        # Get the currently selected state
        selected_uc_id = self.selection["unit_cell"]
        selected_site_id = self.selection["site"]
        selected_state_id = self.selection["state"]
        current_uc = self.unit_cells[selected_uc_id]
        current_site = current_uc.sites[selected_site_id]
        current_state = current_site.states[selected_state_id]

        # Update state properties
        current_state.name = self.unit_cell_data["state_name"]

    def _reduce_uc_basis(self):
        """
        Reduce the basis vectors of the selected unit cell.

        This method applies the Lenstra-Lenstra-Lovász (LLL) lattice
        reduction algorithm to find a more orthogonal set of basis
        vectors that spans the same lattice.
        This is useful for finding a 'nicer' representation of the unit cell
        with basis vectors that are shorter and more orthogonal to each other.

        The method only affects the periodic directions of the unit cell. After
        reduction, the UI is updated to reflect the new basis vectors.
        """
        selected_uc_id = self.selection.get("unit_cell", None)
        if selected_uc_id:
            uc = self.unit_cells[selected_uc_id]
            reduced_basis = uc.reduced_basis()

            # Run a model update
            v1 = reduced_basis[0]
            v2 = reduced_basis[1]
            v3 = reduced_basis[2]
            self.unit_cell_data.update(
                {
                    "v1x": v1.x,
                    "v1y": v1.y,
                    "v1z": v1.z,
                    "v2x": v2.x,
                    "v2y": v2.y,
                    "v2z": v2.z,
                    "v3x": v3.x,
                    "v3y": v3.y,
                    "v3z": v3.z,
                }
            )
            self._save_unit_cell()

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
        state_id = self.selection.get("state", None)

        unit_cell_updated_data = {}
        site_updated_data = {}
        state_updated_data = {}
        if unit_cell_id:
            # Get the selected unit cell
            uc = self.unit_cells[unit_cell_id]

            # Get the system dimensionality
            dim = uc.v1.is_periodic + uc.v2.is_periodic + uc.v3.is_periodic
            # Set the dimensionality radio button.
            # Suppress the dim_listener since we are updating the radio
            # button programmatically
            self._suppress_dim_listener = True
            self.unit_cell_view.unit_cell_panel.radio_group.button(
                dim
            ).setChecked(True)
            self._suppress_dim_listener = False

            # Get the model fields that are going to be updated from the
            # selected unit cell.
            # Update the empty unit_cell_updated_data dictionary
            unit_cell_updated_data.update(
                {
                    "unit_cell_name": uc.name,
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
            # Show the UnitCellPanel
            self.unit_cell_view.uc_stack.setCurrentWidget(
                self.unit_cell_view.unit_cell_panel
            )

            if site_id:
                site = uc.sites[site_id]
                # Get the model fields that are going to be updated from
                # the selected site.
                # Update the empty site_updated_data dictionary
                site_updated_data.update(
                    {
                        "site_name": site.name,
                        "c1": site.c1,
                        "c2": site.c2,
                        "c3": site.c3,
                    }
                )

                # Set the site radius field and the color swatch
                site_radius = self.unit_cells[unit_cell_id].site_sizes[site_id]
                self.R.setValue(site_radius)

                site_color = self.unit_cells[unit_cell_id].site_colors[site_id]

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
                if state_id:
                    state = site.states[state_id]
                    # Get the model fields that are going to be updated from
                    # the selected state.
                    # Update the empty state_updated_data dictionary
                    state_updated_data.update(
                        {
                            "state_name": state.name,
                        }
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
        # Combine the update dictionaries and use the combination
        # to update the model
        self.unit_cell_data.update(
            unit_cell_updated_data | site_updated_data | state_updated_data
        )
        # Request a plot update
        self.plot_update_requested.emit()

    def _dimensionality_change(self):
        """
        Handle changes in the dimensionality selection (0D, 1D, 2D, 3D).

        This method is called when the user selects a different dimensionality
        radio button.
        It updates the unit cell's periodicity flags and enables/disables
        appropriate basis vector components based on
        the selected dimensionality.

        For example:
        - 0D: All directions are non-periodic (isolated system)
        - 1D: First direction is periodic, others are not
        - 2D: First and second directions are periodic, third is not
        - 3D: All directions are periodic (fully periodic crystal)
        """
        btn = self.sender()
        if btn.isChecked():
            selected_dim = int(btn.text())

            self.v1[0].setEnabled(True)
            self.v1[1].setEnabled(selected_dim > 1)
            self.v1[2].setEnabled(selected_dim > 2)

            self.v2[0].setEnabled(selected_dim > 1)
            self.v2[1].setEnabled(True)
            self.v2[2].setEnabled(selected_dim > 2)

            self.v3[0].setEnabled(selected_dim > 2)
            self.v3[1].setEnabled(selected_dim > 2)
            self.v3[2].setEnabled(True)

            if selected_dim == 0:

                self.unit_cell_data.update(
                    {
                        "v1x": 1.0,
                        "v1y": 0.0,
                        "v1z": 0.0,
                        "v2x": 0.0,
                        "v2y": 1.0,
                        "v2z": 0.0,
                        "v3x": 0.0,
                        "v3y": 0.0,
                        "v3z": 1.0,
                        "v1periodic": False,
                        "v2periodic": False,
                        "v3periodic": False,
                    }
                )

            elif selected_dim == 1:

                self.unit_cell_data.update(
                    {
                        # "v1x": 1.0,
                        "v1y": 0.0,
                        "v1z": 0.0,
                        "v2x": 0.0,
                        # "v2y": 1.0,
                        "v2z": 0.0,
                        "v3x": 0.0,
                        "v3y": 0.0,
                        # "v3z": 1.0,
                        "v1periodic": True,
                        "v2periodic": False,
                        "v3periodic": False,
                    }
                )

            elif selected_dim == 2:

                self.unit_cell_data.update(
                    {
                        # "v1x": 1.0,
                        # "v1y": 0.0,
                        "v1z": 0.0,
                        # "v2x": 0.0,
                        # "v2y": 1.0,
                        "v2z": 0.0,
                        "v3x": 0.0,
                        "v3y": 0.0,
                        # "v3z": 1.0,
                        "v1periodic": True,
                        "v2periodic": True,
                        "v3periodic": False,
                    }
                )

            elif selected_dim == 3:

                self.unit_cell_data.update(
                    {
                        # "v1x": 1.0,
                        # "v1y": 0.0,
                        # "v1z": 0.0,
                        # "v2x": 0.0,
                        # "v2y": 1.0,
                        # "v2z": 0.0,
                        # "v3x": 0.0,
                        # "v3y": 0.0,
                        # "v3z": 1.0,
                        "v1periodic": True,
                        "v2periodic": True,
                        "v3periodic": True,
                    }
                )
            # If the listener is suppressed (when the dimensionality
            # was set programmatically), do not run the save cycle
            if self._suppress_dim_listener:
                return
            self._save_unit_cell()

    def _update_unit_cell_data(self, key, value):
        """
        Update the unit cell data model with new values.

        This method is called when the user edits a unit cell property in the
        unit cell form panel.
        It updates the reactive data model, which will trigger a signal that
        causes the _save_unit_cell method to update the actual UnitCell object.

        Args:
            key: The property name to update (e.g., "v1x", "v2y")
            value: The new value for the property
        """
        self.unit_cell_data[key] = value
        self._save_unit_cell()

    def _update_site_data(self, key, value):
        """
        Update the unit cell data model with new values pertaining to the site

        This method is called when the user edits a site property in the
        site form panel.
        It updates the reactive data model, which will trigger a signal that
        causes the _save_site method to update the actual Site object.

        Args:
            key: The property name to update (e.g., "c1", "c2"
            value: The new value for the property
        """
        self.unit_cell_data[key] = value
        self._save_site()

    def _update_unit_cell_ui(self):
        """
        Update the UI with the current unit cell data.
        This method sets the values of the spinboxes in the unit cell panel
        based on the current values in the unit_cell_data dictionary.
        These updates do not trigger any signals as the values change using
        setValue and not using direct input.
        """

        self.v1[0].setValue(self.unit_cell_data["v1x"])
        self.v1[1].setValue(self.unit_cell_data["v1y"])
        self.v1[2].setValue(self.unit_cell_data["v1z"])

        self.v2[0].setValue(self.unit_cell_data["v2x"])
        self.v2[1].setValue(self.unit_cell_data["v2y"])
        self.v2[2].setValue(self.unit_cell_data["v2z"])

        self.v3[0].setValue(self.unit_cell_data["v3x"])
        self.v3[1].setValue(self.unit_cell_data["v3y"])
        self.v3[2].setValue(self.unit_cell_data["v3z"])

        self.c1.setValue(self.unit_cell_data["c1"])
        self.c2.setValue(self.unit_cell_data["c2"])
        self.c3.setValue(self.unit_cell_data["c3"])

    def _update_site_size(self):
        """
        Update the size of the site marker. First, the data from the
        spinbox is saved to the dictionary of sizes. Next, a UC plot
        update is requested.
        """
        self.unit_cells[self.selection["unit_cell"]].site_sizes[
            self.selection["site"]
        ] = self.R.value()
        self.plot_update_requested.emit()

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
