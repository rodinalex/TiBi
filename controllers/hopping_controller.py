import numpy as np
from PySide6.QtCore import QObject, Qt, QPoint, Signal
from PySide6.QtGui import QAction, QUndoStack
from PySide6.QtWidgets import QDoubleSpinBox, QMenu, QPushButton, QSpinBox
import uuid

from logic.commands import SaveHoppingsCommand
from models import Selection, UnitCell
from ui.styles.button_styles import (
    BUTTON_STYLE_DEFAULT,
    BUTTON_STYLE_HAS_HOPPING,
    BUTTON_STYLE_NONHERMITIAN,
)
from views.panels import HoppingPanel


class HoppingController(QObject):
    """
    Controller for the hopping parameter interface.

    This controller manages the creation and editing of hopping parameters
    (tight-binding matrix elements) between quantum states. It handles:

    1. The interactive matrix grid where each button represents a possible
       hopping between two states
    2. The detailed parameter table for editing specific hopping values
    3. The right-click context menu for performing operations like creating
       Hermitian partners

    Attributes
    ----------
    unit_cells : dict[UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
    hopping_view : HoppingPanel
        The main view component
    undo_stack : QUndoStack
        `QUndoStack` to hold "undo-able" commands
    state_info : list[tuple]
        List of tuples with state information \
        (site_name, site_id, state_name, state_id)\
        for each `State` in the `UnitCell`
    pair_selection : list[tuple]
        2-element list of tuples containing the selected state pair
    hoppings : dict[tuple[uuid, uuid],\
            list[tuple[tuple[int, int, int], np.complex128]]]
        Dictionary containing the hopping parameters for the `UnitCell`.
        The keys are `State` UUID tuples. The values are lists of hoppings.
        Each hopping is a tuple of a displacement tuple, given in
        terms of lattice vectors, and a complex amplitude.

    Methods
    -------
    update_unit_cell()
        Updates the hopping data model with the `UnitCell`'s hoppings

    Signals
    -------
    btn_clicked
        Emitted when a hopping button is clicked. The Signal carries the source
        and destination state info following the
        (site_name, site_id, state_name, state_id) format.
    hoppings_changed
        Emitted by the command when couplings are modified.
        The signal carries the information about the current item selection,
        as well as the selection of the state pair. It triggers
        a table and matrix update.
    hopping_segments_requested
        Emitted when the coupling table is updated, triggering an
        update of hopping segments.
    selection_requested
        Emitted when the selection change in the tree is required,
        carrying the unit cell, site, and state IDs.
    """

    btn_clicked = Signal(object, object)
    hoppings_changed = Signal(object, object, object, object, object)
    hopping_segments_requested = Signal()
    selection_requested = Signal(object, object, object)

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        hopping_view: HoppingPanel,
        undo_stack: QUndoStack,
    ):
        """
        Initialize the hopping controller.

        Parameters
        ----------
        unit_cells : dict[UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
        hopping_view : HoppingPanel
            The main view component
        undo_stack : QUndoStack
            `QUndoStack` to hold "undo-able" commands
        """
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.hopping_view = hopping_view
        self.undo_stack = undo_stack

        # Internal controller state
        self.state_info = []
        self.pair_selection = [
            None,
            None,
        ]
        self.hoppings = {}

        # Connect Signals
        self.btn_clicked.connect(self._update_pair_selection)
        self.hopping_view.table_panel.add_row_btn.clicked.connect(
            self._add_empty_row
        )
        self.hopping_view.table_panel.remove_row_btn.clicked.connect(
            self._remove_selected_coupling
        )
        self.hopping_view.table_panel.save_btn.clicked.connect(
            self._save_couplings
        )
        self.hoppings_changed.connect(self._handle_hoppings_changed)

    def update_unit_cell(self):
        """
        Update the hopping data model with the selected `UnitCell`'s hoppings.

        This method is called when the selection changes in the tree view.
        It retrieves the currently selected unit cell and its hoppings,
        refreshing the matrix.
        """
        uc_id = self.selection.unit_cell
        # Deselect the previous states
        self._update_pair_selection(None, None)

        # If no unit cell selected, hide the panels and exit early
        if uc_id is None:
            self.hopping_view.panel_stack.setCurrentWidget(
                self.hopping_view.info_label
            )
            return

        else:
            uc = self.unit_cells[uc_id]

            # Get the states and their "info" from inside the unit cell
            _, new_info = uc.get_states()

            # Use the states and the info to construct the hopping matrix grid
            self.hoppings = uc.hoppings
            self.state_info = new_info
            # If there are no states in the unit cell, hide the panels
            if new_info == []:
                self.hopping_view.panel_stack.setCurrentWidget(
                    self.hopping_view.info_label
                )
            else:
                self.hopping_view.panel_stack.setCurrentWidget(
                    self.hopping_view.panel
                )
                self._refresh_matrix()

    def _refresh_matrix(self):
        """
        Refresh the matrix grid.

        Button colors are updated based on whether hoppings
        exist between states.
        """
        # Clear existing widgets in grid layout
        while self.hopping_view.matrix_panel.grid_layout.count():
            item = self.hopping_view.matrix_panel.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Configure grid layout to center the content
        self.hopping_view.matrix_panel.grid_layout.setAlignment(Qt.AlignCenter)

        # Create the button grid
        self.buttons = {}
        for ii in range(len(self.state_info)):
            for jj in range(len(self.state_info)):
                btn = QPushButton("")
                btn.setFixedSize(20, 20)
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(
                    lambda _, row=ii, col=jj, b=btn: self._add_context_menu(
                        b, row, col
                    )
                )
                # Get the states
                state1 = self.state_info[ii]
                state2 = self.state_info[jj]
                # Apply button styles

                hop = set(self.hoppings.get((state1[3], state2[3]), []))
                hop_herm = set(self.hoppings.get((state2[3], state1[3]), []))
                has_hopping = bool(hop)
                hop_neg_conj = set(
                    ((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop
                )
                is_hermitian = hop_neg_conj == hop_herm
                self._apply_button_style(btn, has_hopping, is_hermitian)

                # Set tips to show both states when hovering.
                # Show the state and site names.
                # From second quantization, the hopping goes FROM column INTO
                # row (columns multiply annihilation operators,
                # rows multiply creation)
                btn.setToolTip(
                    f"{state2[0]}.{state2[2]} → {state1[0]}.{state1[2]}"
                )
                btn.setStatusTip(
                    f"{state2[0]}.{state2[2]} → {state1[0]}.{state1[2]}"
                )

                # Button click handler implementation:
                btn.clicked.connect(
                    lambda checked=False, r=ii, c=jj: self.btn_clicked.emit(
                        self.state_info[r],
                        self.state_info[c],  # Format (TO_state, FROM_state)
                    )
                )
                # Add the button to the grid
                self.hopping_view.matrix_panel.grid_layout.addWidget(
                    btn, ii, jj
                )
                # Save to the button dictionary
                self.buttons[(ii, jj)] = btn

    def _apply_button_style(
        self, button: QPushButton, has_hopping, hermitian=False
    ):
        """
        Apply the appropriate style to a button based on its hoppings.

        Parameters
        ----------
        button : QPushButton
            The button to style
        has_hopping : bool
            Indicator whether the button marks a connection with hoppings
        hermitian : bool
            Boolean indicating whether the coupling is Hermitian
        """
        if not has_hopping:
            style = BUTTON_STYLE_DEFAULT
        else:
            if hermitian:
                style = BUTTON_STYLE_HAS_HOPPING
            else:
                style = BUTTON_STYLE_NONHERMITIAN

        button.setStyleSheet(style)

    def _update_pair_selection(self, s1, s2):
        """
        Update the pair selection and the table to display hopping terms.

        Parameters
        ----------
        s1 : tuple[str, uuid.UUID, str, uuid.UUID] | None
            Information tuple for the destination `State` (row)
        s2 : tuple[str, uuid.UUID, str, uuid.UUID] | None
            Information tuple for the source `State` (column)
        """

        # Store the UUIDs of the selected states
        self.pair_selection = [s1, s2]
        if (s1 is None) or (s2 is None):
            self.hopping_view.table_stack.setCurrentWidget(
                self.hopping_view.table_info_label
            )
        else:
            self.hopping_view.table_stack.setCurrentWidget(
                self.hopping_view.table_panel
            )

            # Update the table title to show the selected states
            # (source → destination)
            self.hopping_view.table_panel.table_title.setText(
                f"{s2[0]}.{s2[2]} → {s1[0]}.{s1[2]}"
            )
            self._refresh_table()

    def _refresh_table(self):
        """Clear the table and repopulate it with the latest hopping terms"""
        self.hopping_view.table_panel.hopping_table.setRowCount(
            0
        )  # Clear existing data
        for (d1, d2, d3), amplitude in self.hoppings.get(
            (self.pair_selection[0][3], self.pair_selection[1][3]), []
        ):
            row_index = self.hopping_view.table_panel.hopping_table.rowCount()
            self.hopping_view.table_panel.hopping_table.insertRow(row_index)

            # Use cell widgets instead of QTableWidgetItem
            spinbox_d1 = self._make_spinbox(value=d1)
            spinbox_d2 = self._make_spinbox(value=d2)
            spinbox_d3 = self._make_spinbox(value=d3)
            re_box = self._make_doublespinbox(value=np.real(amplitude))
            im_box = self._make_doublespinbox(value=np.imag(amplitude))

            self.hopping_view.table_panel.hopping_table.setCellWidget(
                row_index, 0, spinbox_d1
            )
            self.hopping_view.table_panel.hopping_table.setCellWidget(
                row_index, 1, spinbox_d2
            )
            self.hopping_view.table_panel.hopping_table.setCellWidget(
                row_index, 2, spinbox_d3
            )
            self.hopping_view.table_panel.hopping_table.setCellWidget(
                row_index, 3, re_box
            )
            self.hopping_view.table_panel.hopping_table.setCellWidget(
                row_index, 4, im_box
            )
        self.hopping_segments_requested.emit()

    def _make_spinbox(self, value=0, minimum=-99, maximum=99):
        """Auxiliary function to create a spinbox for hopping displacement"""
        box = QSpinBox()
        box.setRange(minimum, maximum)
        box.setValue(value)
        box.setButtonSymbols(QSpinBox.NoButtons)
        return box

    def _make_doublespinbox(
        self, value=0.0, minimum=-1e6, maximum=1e6, decimals=3
    ):
        """
        Auxiliary function to create a double spinbox for hopping amplitude
        """
        box = QDoubleSpinBox()
        box.setRange(minimum, maximum)
        box.setDecimals(decimals)
        box.setValue(value)
        box.setButtonSymbols(QDoubleSpinBox.NoButtons)

        return box

    def _add_empty_row(self):
        """Add a new empty row to the table"""
        row_index = self.hopping_view.table_panel.hopping_table.rowCount()
        self.hopping_view.table_panel.hopping_table.insertRow(row_index)

        # Pre-fill with default values
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 0, self._make_spinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 1, self._make_spinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 2, self._make_spinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 3, self._make_doublespinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 4, self._make_doublespinbox()
        )

    def _remove_selected_coupling(self):
        """Remove selected row(s) from the table"""
        selected_rows = set()

        # Get the selection model from the table
        selection_model = (
            self.hopping_view.table_panel.hopping_table.selectionModel()
        )

        # Get the selected rows
        selected_indexes = selection_model.selectedRows()

        # Extract the row numbers from the selected indexes
        for index in selected_indexes:
            selected_rows.add(index.row())

        # Remove the rows from the table in reverse order to avoid
        # shifting issues
        for row in sorted(selected_rows, reverse=True):
            self.hopping_view.table_panel.hopping_table.removeRow(row)

    def _save_couplings(self):
        """
        Extract data from the hopping table and save it to the `UnitCell`.

        Read all rows from the table, converting cell values to the
        appropriate types:
        - First 3 columns (d₁,d₂,d₃) to integers (displacement vector)
        - Last 2 columns (Re(t), Im(t)) to floats (complex amplitude)

        If the same triplet (d₁,d₂,d₃) appears more than once,
        the amplitudes are summed. The data is then passed to the
        `SaveHoppingsCommand` to update the unit cell model.
        """
        new_couplings: dict[tuple[int, int, int], np.complex128] = {}
        # Extract values from each row in the table
        for row in range(
            self.hopping_view.table_panel.hopping_table.rowCount()
        ):
            d1, d2, d3, re, im = [
                self.hopping_view.table_panel.hopping_table.cellWidget(
                    row, n
                ).value()
                for n in range(5)
            ]

            # Create the complex amplitude
            amplitude = np.complex128(re + im * 1j)

            # Create a tuple for the displacement vector (d₁, d₂, d₃)
            triplet = (d1, d2, d3)
            # If the triplet already exists, merge amplitudes by adding
            # the new amplitude
            if triplet in new_couplings:
                new_couplings[triplet] += amplitude
            else:
                new_couplings[triplet] = amplitude

        # Convert the dictionary to the expected format of the list of tuples.
        # Remove any entries with non-finite or zero amplitudes
        merged_couplings = [
            ((d1, d2, d3), amplitude)
            for (d1, d2, d3), amplitude in new_couplings.items()
            if np.isfinite(amplitude.real)
            and np.isfinite(amplitude.imag)
            and not np.isclose(amplitude, 0)
        ]
        # Only update the model if the hoppings have changed
        if set(merged_couplings) == set(
            self.unit_cells[self.selection.unit_cell].hoppings.get(
                (self.pair_selection[0][3], self.pair_selection[1][3]), []
            )
        ):
            # No changes detected, just refresh the table in case the user
            # rearranged the rows without actually changing the data or
            # added rows with zero amplitude
            self._refresh_table()
            return

        # Update the data model with the new couplings and emit the signal
        self.undo_stack.push(
            SaveHoppingsCommand(
                unit_cells=self.unit_cells,
                selection=self.selection,
                pair_selection=self.pair_selection,
                new_hoppings=merged_couplings,
                signal=self.hoppings_changed,
            )
        )

    def _add_context_menu(self, button, ii, jj):
        """
        Create a context menu for the button to manage hoppings.

        Parameters
        ----------
        button : QPushButton
            The button that was right-clicked
        ii : int
            Row index of the button in the matrix
        jj : int
            Column index of the button in the matrix
        """
        menu = QMenu()
        # Send hopping data to the transpose element
        action_send_hoppings = QAction("Set transpose element", self)
        action_send_hoppings.triggered.connect(
            lambda: self._create_hermitian_partner(ii, jj)
        )
        menu.addAction(action_send_hoppings)

        # Get hopping data from the transpose element
        action_get_hoppings = QAction("Get transpose element", self)
        action_get_hoppings.triggered.connect(
            lambda: self._create_hermitian_partner(jj, ii)
        )
        menu.addAction(action_get_hoppings)

        # Clear hoppings
        action_clear_hoppings = QAction("Clear hoppings", self)
        action_clear_hoppings.triggered.connect(
            lambda: self._delete_coupling(ii, jj)
        )
        menu.addAction(action_clear_hoppings)

        menu.exec_(button.mapToGlobal(QPoint(0, button.height())))

    def _create_hermitian_partner(self, ii, jj):
        """
        Create a Hermitian partner for the selected hopping.

        The Hermitian partner is created by negating the displacement vector
        and taking the complex conjugate of the amplitude.

        Parameters
        ----------
        ii : int
            Index of the destination state in the matrix
        jj : int
            Index of the source state in the matrix
        """
        s1 = self.state_info[ii]  # Destination
        s2 = self.state_info[jj]  # Source
        hop = self.hoppings.get((s1[3], s2[3]), [])
        hop_herm = [((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop]
        self.pair_selection = [s2, s1]

        self.undo_stack.push(
            SaveHoppingsCommand(
                unit_cells=self.unit_cells,
                selection=self.selection,
                pair_selection=self.pair_selection,
                new_hoppings=hop_herm,
                signal=self.hoppings_changed,
            )
        )

    def _delete_coupling(self, ii, jj):
        """
        Delete the coupling between two states.

        Parameters
        ----------
        ii : int
            Index of the destination state in the matrix (row index)
        jj : int
            Index of the source state in the matrix (column index)
        """
        s1 = self.state_info[ii]  # Destination
        s2 = self.state_info[jj]  # Source

        self._update_pair_selection(s1, s2)

        self.undo_stack.push(
            SaveHoppingsCommand(
                unit_cells=self.unit_cells,
                selection=self.selection,
                pair_selection=self.pair_selection,
                new_hoppings=[],
                signal=self.hoppings_changed,
            )
        )

    def _handle_hoppings_changed(self, uc_id, site_id, state_id, s1, s2):
        """
        Redraw the matrix and table when hoppings are modified.

        If the selection at the point of the hopping change is different
        from the current one, emit a signal to update the selection in
        the tree. Otherwise, refresh the matrix. Additionally, select
        the pair of states and update the table.

        Parameters
        ----------
        uc_id : uuid.UUID
            UUID of the unit cell
        site_id : uuid.UUID
            UUID of the site
        state_id : uuid.UUID
            UUID of the state
        s1 : tuple[str, uuid.UUID, str, uuid.UUID]
            Information tuple for the destination `State` (row)
        s2 : tuple[str, uuid.UUID, str, uuid.UUID]
            Information tuple for the source `State` (column)
        """
        # If the unit cell selection needs to change, matrix redrawing
        # will be handled by the app controller as all panels are updated
        # Otherwise, we need to refresh the matrix manually.

        if self.selection.unit_cell == uc_id:
            self._refresh_matrix()

        if (
            self.selection.unit_cell != uc_id
            or self.selection.site != site_id
            or self.selection.state != state_id
        ):
            self.selection_requested.emit(uc_id, site_id, state_id)

        # Update Pair Selection
        self._update_pair_selection(s1, s2)
