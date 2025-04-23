import uuid
from PySide6.QtCore import QObject, Qt, Signal, QPoint
from PySide6.QtWidgets import QPushButton, QSpinBox, QDoubleSpinBox, QMenu
from PySide6.QtGui import QAction
from src.tibitypes import UnitCell
from models.data_models import DataModel
from views.hopping_view import HoppingView
from resources.button_styles import (
    BUTTON_STYLE_DEFAULT,
    BUTTON_STYLE_HAS_HOPPING,
    BUTTON_STYLE_NONHERMITIAN,
)
import numpy as np


class HoppingController(QObject):

    # Signal emitted when a button is clicked, carrying the source and destination state info
    # Params: (source_state_info, destination_state_info) where each is (site_name, state_name, state_id)
    button_clicked = Signal(object, object)

    # Signal emitted when couplings are modified from right-clicking on the button grid.
    # The signal triggers a table and matrix update
    hoppings_changed = Signal()

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        hopping_data: DataModel,
        state_info,
        pair_selection,
        state_coupling,
        hopping_view: HoppingView,
    ):

        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.hopping_data = hopping_data
        self.state_info = state_info
        self.pair_selection = pair_selection
        self.state_coupling = state_coupling
        self.hopping_view = hopping_view

        # Connect Signals
        self.selection.signals.updated.connect(self.set_unit_cell)
        self.button_clicked.connect(self.set_pair)

        self.hopping_view.table_panel.add_row_btn.clicked.connect(self.add_empty_row)
        self.hopping_view.table_panel.remove_row_btn.clicked.connect(
            self.remove_selected_coupling
        )
        self.hopping_view.table_panel.save_btn.clicked.connect(self.save_couplings)
        self.hoppings_changed.connect(self.handle_matrix_interaction)

    def set_unit_cell(self):
        """
        Called when the selection changes in the tree view.
        Updates the hopping data model with the selected unit cell's hoppings.
        """
        uc_id = self.selection.get("unit_cell")
        self.hopping_data = DataModel()
        self.state_info = []
        self.pair_selection[0] = None
        self.pair_selection[1] = None
        self.hopping_view.table_stack.setCurrentWidget(
            self.hopping_view.table_info_label
        )  # Hide the table until a pair is selected

        # Clear the table since no state pair is selected yet
        self.state_coupling = []
        self.hopping_view.table_panel.table_title.setText("")
        # If no unit cell selected, hide the panels
        if uc_id == None:
            self.hopping_view.panel_stack.setCurrentWidget(self.hopping_view.info_label)

        else:
            uc = self.unit_cells[uc_id]

            # Get the states and their "info" from inside the unit cell
            _, new_info = uc.get_states()

            # Use the states and the info to construct the hopping matrix grid
            # Extract the hopping data
            self.hopping_data = DataModel(uc.hoppings)
            # If there are no states in the unit cell, hide the panels
            if new_info == []:
                self.hopping_view.panel_stack.setCurrentWidget(
                    self.hopping_view.info_label
                )
            else:
                self.hopping_view.panel_stack.setCurrentWidget(self.hopping_view.panel)
            self.state_info = new_info

        self.refresh_matrix()

    def refresh_matrix(self):
        """
        Refreshes the entire matrix grid by removing all existing buttons and recreating them.
        Updates button colors based on whether hoppings exist between states.
        """
        # Clear existing widgets in grid layout
        while self.hopping_view.matrix_panel.grid_layout.count():
            item = self.hopping_view.matrix_panel.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Configure grid layout to center the content
        self.hopping_view.matrix_panel.grid_layout.setAlignment(Qt.AlignCenter)

        # --- Create the button grid ---
        self.buttons = {}
        for ii in range(len(self.state_info)):
            for jj in range(len(self.state_info)):
                btn = QPushButton("")
                btn.setFixedSize(20, 20)
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(
                    lambda _, row=ii, col=jj, b=btn: self.add_context_menu(b, row, col)
                )
                # Apply the default style (no hopping initially)
                self.apply_button_style(btn, False)

                # Set tooltip to show both states when hovering.
                state1 = self.state_info[ii]
                state2 = self.state_info[jj]
                # Show the state and site names.
                # From second quantization, the hopping goes FROM column INTO row
                # (columns multiply annihilation operators, rows multiply creation)
                btn.setToolTip(f"{state2[0]}.{state2[1]} → {state1[0]}.{state1[1]}")

                # Button click handler implementation:
                # 1. Qt buttons can only connect to argumentless functions
                # 2. We use a lambda with default arguments to capture the current ii,jj values
                # 3. When button is clicked, the lambda emits a signal with the source and destination states
                # 4. This approach avoids the "closure capture" problem with lambda in loops
                btn.clicked.connect(
                    lambda checked=False, row=ii, col=jj: self.button_clicked.emit(
                        self.state_info[row], self.state_info[col]
                    )
                )

                self.hopping_view.matrix_panel.grid_layout.addWidget(btn, ii, jj)
                self.buttons[(ii, jj)] = btn

            # Update button colors based on existing hoppings
            self.refresh_button_colors()

    def apply_button_style(self, button: QPushButton, has_hopping, hermitian=False):
        """
        Apply the appropriate style to a button based on whether it has hoppings.

        Args:
            button: The QPushButton to style
            has_hopping: Boolean indicating whether the button represents a connection with hoppings
            hermitian: Boolean indicating whether the coupling is Hermitian
        """
        if not has_hopping:
            style = BUTTON_STYLE_DEFAULT
        else:
            if hermitian:
                style = BUTTON_STYLE_HAS_HOPPING
            else:
                style = BUTTON_STYLE_NONHERMITIAN

        button.setStyleSheet(style)

    def refresh_button_colors(self):
        """
        Updates button colors based on whether hoppings exist between states.

        Iterates through all buttons in the grid and applies the appropriate style
        based on whether there are any hopping terms defined for the corresponding
        state pair.

        The pair is also checked against its transpose element to determine whether
        the couplings are Hermitian.
        """
        if not self.buttons:
            return

        # Iterate through all buttons and update their colors
        for pos, btn in self.buttons.items():
            ii, jj = pos
            s1 = self.state_info[ii][2]  # Destination state ID
            s2 = self.state_info[jj][2]  # Source state ID
            hop = set(self.hopping_data.get((s1, s2), []))
            hop_herm = set(self.hopping_data.get((s2, s1), []))
            has_hopping = bool(hop)

            hop_neg_conj = set(
                ((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop
            )
            is_hermitian = hop_neg_conj == hop_herm
            # Apply the appropriate style based on hopping existence
            self.apply_button_style(btn, has_hopping, is_hermitian)

    def set_pair(self, s1, s2):
        """
        Called when a button is clicked in the hopping matrix.
        Updates the table to display hopping terms between the selected states.

        Args:
            s1: Tuple of (site_name, state_name, state_id) for the destination state (row)
            s2: Tuple of (site_name, state_name, state_id) for the source state (column)
        """
        # Store the UUIDs of the selected states
        self.pair_selection = [s1[2], s2[2]]
        self.hopping_view.table_stack.setCurrentWidget(self.hopping_view.table_panel)

        # Retrieve existing hopping terms between these states, or empty list if none exist
        self.state_coupling = self.hopping_data.get((s1[2], s2[2]), [])

        # Update the table title to show the selected states (source → destination)
        self.hopping_view.table_panel.table_title.setText(
            f"{s2[0]}.{s2[1]} → {s1[0]}.{s1[1]}"
        )
        self.refresh_table()

    def refresh_table(self):
        """Clear the table and repopulate it with the latest hopping terms"""
        self.hopping_view.table_panel.hopping_table.setRowCount(
            0
        )  # Clear existing data

        for (d1, d2, d3), amplitude in self.state_coupling:
            row_index = self.hopping_view.table_panel.hopping_table.rowCount()
            self.hopping_view.table_panel.hopping_table.insertRow(row_index)

            # Use cell widgets instead of QTableWidgetItem
            spinbox_d1 = self.make_spinbox(value=d1)
            spinbox_d2 = self.make_spinbox(value=d2)
            spinbox_d3 = self.make_spinbox(value=d3)
            re_box = self.make_doublespinbox(value=np.real(amplitude))
            im_box = self.make_doublespinbox(value=np.imag(amplitude))

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

    def make_spinbox(self, value=0, minimum=-99, maximum=99):
        box = QSpinBox()
        box.setRange(minimum, maximum)
        box.setValue(value)
        return box

    def make_doublespinbox(self, value=0.0, minimum=-1e6, maximum=1e6, decimals=3):
        box = QDoubleSpinBox()
        box.setRange(minimum, maximum)
        box.setDecimals(decimals)
        box.setValue(value)
        return box

    def add_empty_row(self):
        """Add a new empty row to the table"""
        row_index = self.hopping_view.table_panel.hopping_table.rowCount()
        self.hopping_view.table_panel.hopping_table.insertRow(row_index)

        # Pre-fill with default values
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 0, self.make_spinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 1, self.make_spinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 2, self.make_spinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 3, self.make_doublespinbox()
        )
        self.hopping_view.table_panel.hopping_table.setCellWidget(
            row_index, 4, self.make_doublespinbox()
        )

    def remove_selected_coupling(self):
        """Remove selected row(s) from the table"""
        selected_rows = set()

        # Get the selection model from the table
        selection_model = self.hopping_view.table_panel.hopping_table.selectionModel()

        # Get the selected rows
        selected_indexes = selection_model.selectedRows()

        # Extract the row numbers from the selected indexes
        for index in selected_indexes:
            selected_rows.add(index.row())

        # Remove the rows from the table in reverse order to avoid shifting issues
        for row in sorted(selected_rows, reverse=True):
            self.hopping_view.table_panel.hopping_table.removeRow(row)

    def save_couplings(self):
        """
        Extracts data from the hopping table and saves it to the unit cell model.

        Reads all rows from the table, converting cell values to the appropriate types:
        - First 3 columns (d₁,d₂,d₃) to integers (displacement vector)
        - Last 2 columns (Re(t), Im(t)) to floats (complex amplitude)

        If the same triplet (d₁,d₂,d₃) appears more than once, the amplitudes are summed
        """
        new_couplings = {}
        # Extract values from each row in the table
        for row in range(self.hopping_view.table_panel.hopping_table.rowCount()):
            # Get displacement vector components (integers)
            d1 = self.hopping_view.table_panel.hopping_table.cellWidget(row, 0).value()
            d2 = self.hopping_view.table_panel.hopping_table.cellWidget(row, 1).value()
            d3 = self.hopping_view.table_panel.hopping_table.cellWidget(row, 2).value()

            # Get complex amplitude components (floats)
            re = self.hopping_view.table_panel.hopping_table.cellWidget(row, 3).value()
            im = self.hopping_view.table_panel.hopping_table.cellWidget(row, 4).value()

            # Create the complex amplitude
            amplitude = np.complex128(re + im * 1j)

            # Create a tuple for the displacement vector (d₁, d₂, d₃)
            triplet = (d1, d2, d3)
            # If the triplet already exists, merge amplitudes by adding the new amplitude
            if triplet in new_couplings:
                new_couplings[triplet] += amplitude
            else:
                new_couplings[triplet] = amplitude

        # Convert the dictionary to the expected format of the list of tuples
        merged_couplings = [
            ((d1, d2, d3), amplitude)
            for (d1, d2, d3), amplitude in new_couplings.items()
        ]
        # Update the data model with the new couplings
        self.hopping_data[(self.pair_selection[0], self.pair_selection[1])] = (
            merged_couplings
        )
        self.unit_cells[self.selection["unit_cell"]].hoppings = self.hopping_data

        # Refresh the table with the new data
        self.state_coupling = merged_couplings

        # Update the matrix and the table to show the new coupling state
        self.refresh_matrix()
        self.refresh_table()

    def add_context_menu(self, button, ii, jj):
        menu = QMenu()
        # Send hopping data to the transpose element
        action_send_hoppings = QAction("Set transpose element", self)
        action_send_hoppings.triggered.connect(
            lambda: self.create_hermitian_partner(ii, jj)
        )
        menu.addAction(action_send_hoppings)

        # Get hopping data from the transpose element
        action_get_hoppings = QAction("Get transpose element", self)
        action_get_hoppings.triggered.connect(
            lambda: self.create_hermitian_partner(jj, ii)
        )
        menu.addAction(action_get_hoppings)

        # Clear hoppings
        action_clear_hoppings = QAction("Clear hoppings", self)
        action_clear_hoppings.triggered.connect(lambda: self.delete_coupling(ii, jj))
        menu.addAction(action_clear_hoppings)

        menu.exec_(button.mapToGlobal(QPoint(0, button.height())))

    def create_hermitian_partner(self, ii, jj):
        s1 = self.state_info[ii][2]  # Destination
        s2 = self.state_info[jj][2]  # Source
        hop = self.hopping_data.get((s1, s2), [])
        hop_herm = [((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop]
        self.hopping_data[(s2, s1)] = hop_herm
        self.hoppings_changed.emit()

    def delete_coupling(self, ii, jj):
        s1 = self.state_info[ii][2]  # Destination
        s2 = self.state_info[jj][2]  # Source
        self.hopping_data.pop((s1, s2), None)
        self.hoppings_changed.emit()

    def handle_matrix_interaction(self):
        self.refresh_button_colors()
        updated_couplings = self.hopping_data.get(
            (self.pair_selection[0], self.pair_selection[1]), []
        )
        self.state_coupling = updated_couplings

        self.refresh_matrix()
        self.refresh_table()
