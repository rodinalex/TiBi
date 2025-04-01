from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import numpy as np
from src.tibitypes import Hopping

from ui.HOPPING.matrix import HoppingMatrix


class HoppingPanel(QWidget):
    """
    Widget for displaying and editing hopping terms between states in a unit cell.
    Displays a grid of buttons, where each button corresponds to a pair of states.
    """

    hopping_added = Signal(Hopping)
    hopping_removed = Signal(Hopping)

    def __init__(self, unit_cell=None):
        super().__init__()
        self.unit_cell = unit_cell
        self.hopping_data = {}  # Dictionary to store hopping data for each state pair

        # Main layout
        main_layout = QVBoxLayout(self)

        # Info label
        self.info_label = QLabel("Select a unit cell to view hopping parameters")
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)

        # Container for matrix and table
        self.content_container = QWidget()
        container_layout = QHBoxLayout(self.content_container)

        # --- Matrix Panel ---
        # self.matrix_panel = HoppingMatrix()
        self.matrix_panel = QWidget()
        matrix_layout = QVBoxLayout(self.matrix_panel)

        # Scrollable Area for Matrix
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Content widget for grid
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(3)

        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        matrix_layout.addWidget(self.scroll_area)

        # --- Hopping Details Panel ---
        self.details_panel = QWidget()
        details_layout = QVBoxLayout(self.details_panel)

        self.details_label = QLabel("Select a cell to edit hopping parameters")
        details_layout.addWidget(self.details_label)

        # Table manipulation buttons at the top
        table_buttons_layout = QHBoxLayout()

        self.add_row_btn = QPushButton("Add")
        self.add_row_btn.clicked.connect(self.add_empty_row)
        table_buttons_layout.addWidget(self.add_row_btn)

        self.remove_row_btn = QPushButton("Remove")
        self.remove_row_btn.clicked.connect(self.remove_selected_hopping)
        table_buttons_layout.addWidget(self.remove_row_btn)

        details_layout.addLayout(table_buttons_layout)

        # Table for hopping details
        self.hopping_table = QTableWidget(0, 4)  # 4 columns: d1, d2, d3, amplitude
        self.hopping_table.setHorizontalHeaderLabels(["d₁", "d₂", "d₃", "Amplitude"])
        self.hopping_table.setColumnWidth(0, 40)  # d₁
        self.hopping_table.setColumnWidth(1, 40)  # d₂
        self.hopping_table.setColumnWidth(2, 40)  # d₃

        # Make the table columns resize to content
        self.hopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Enable editing in the table
        self.hopping_table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed
        )
        self.hopping_table.cellChanged.connect(self.on_table_cell_changed)

        details_layout.addWidget(self.hopping_table, stretch=1)

        # Add both panels to container
        container_layout.addWidget(self.matrix_panel, 1)
        container_layout.addWidget(self.details_panel, 1)

        main_layout.addWidget(self.content_container)

        # Initially hide the content container
        self.content_container.setVisible(False)

        # Current selection
        self.selected_state1 = None
        self.selected_state2 = None

    def set_unit_cell(self, unit_cell):
        """Updates the matrix with states from the given unit cell."""
        self.unit_cell = unit_cell
        self.refresh_matrix()

    def refresh_matrix(self):
        """Rebuilds the hopping matrix based on current unit cell data."""
        # Clear existing widgets in grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.unit_cell:
            self.info_label.setText("Select a unit cell to view hopping parameters")
            self.content_container.setVisible(False)
            return

        # Show the content container
        self.content_container.setVisible(True)
        self.info_label.setText(f"Hopping Matrix for: {self.unit_cell.name}")

        # Collect all states from all sites
        self.states = []
        self.state_info = []  # Store tuples of (site_name, state_name, state_id)

        print("HoppingMatrix.refresh_matrix(): Unit Cell =", self.unit_cell.name)
        print("Number of sites in unit cell:", len(self.unit_cell.sites))

        for site_id, site in self.unit_cell.sites.items():
            print(f"Processing site {site.name} with {len(site.states)} states")
            for state_id, state in site.states.items():
                print(f"  Adding state: {state.name}")
                self.states.append(state)
                self.state_info.append((site.name, state.name, state_id))

        print(f"Total states collected: {len(self.states)}")

        if not self.states:
            print("No states found, showing empty message")
            self.info_label.setText("No states available in this unit cell")
            # Still show the container but with an informative message
            self.content_container.setVisible(False)
            return

        # --- Create Fixed Row & Column Headers ---
        # Add empty corner cell
        corner_label = QLabel("")
        self.grid_layout.addWidget(corner_label, 0, 0)

        # Helper function to create a circle indicator
        def create_circle_indicator(site_name, state_name, color="#4a86e8"):
            from PySide6.QtGui import QPainter, QBrush, QPen, QColor
            from PySide6.QtCore import QRect, QSize

            class CircleIndicator(QWidget):
                def __init__(self, site_name, state_name, color):
                    super().__init__()
                    self.color = QColor(color)
                    self.setToolTip(f"{site_name}: {state_name}")
                    self.setFixedSize(15, 15)  # Small circle

                def paintEvent(self, event):
                    painter = QPainter(self)
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setPen(QPen(QColor("#333333")))
                    painter.setBrush(QBrush(self.color))
                    rect = QRect(1, 1, self.width() - 2, self.height() - 2)
                    painter.drawEllipse(rect)

                def sizeHint(self):
                    return QSize(15, 15)

            return CircleIndicator(site_name, state_name, color)

        # Create color map for states (to help visually distinguish them)
        colors = [
            "#4a86e8",
            "#ff9900",
            "#d5a6bd",
            "#93c47d",
            "#8e7cc3",
            "#f1c232",
            "#6fa8dc",
            "#e06666",
            "#a64d79",
            "#674ea7",
            "#f6b26b",
            "#e69138",
        ]

        # Add column headers with circle indicators
        for j, (site_name, state_name, _) in enumerate(self.state_info):
            color_idx = j % len(colors)
            indicator = create_circle_indicator(
                site_name, state_name, colors[color_idx]
            )
            self.grid_layout.addWidget(indicator, 0, j + 1, Qt.AlignCenter)

        # Add row headers with circle indicators
        for i, (site_name, state_name, _) in enumerate(self.state_info):
            color_idx = i % len(colors)
            indicator = create_circle_indicator(
                site_name, state_name, colors[color_idx]
            )
            row_container = QWidget()
            row_layout = QHBoxLayout(row_container)
            row_layout.setContentsMargins(0, 0, 5, 0)
            row_layout.addWidget(indicator, alignment=Qt.AlignRight)
            self.grid_layout.addWidget(row_container, i + 1, 0)

        # --- Create the button grid ---
        self.buttons = {}
        for i in range(len(self.states)):
            for j in range(len(self.states)):
                btn = QPushButton("")
                btn.setFixedSize(25, 25)  # Smaller square buttons
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #e0e0e0;
                        border: 1px solid #aaaaaa;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                        border: 1px solid #777777;
                    }
                """
                )

                # Set tooltip to show both states when hovering
                state1_info = self.state_info[i]
                state2_info = self.state_info[j]
                btn.setToolTip(
                    f"{state1_info[0]}.{state1_info[1]} → {state2_info[0]}.{state2_info[1]}"
                )

                # Use lambda with default args to capture correct i,j values
                btn.clicked.connect(
                    lambda checked=False, row=i, col=j: self.show_hopping_details(
                        row, col
                    )
                )

                self.grid_layout.addWidget(btn, i + 1, j + 1)
                self.buttons[(i, j)] = btn

        # Update button colors based on existing hoppings
        self.refresh_button_colors()

    def refresh_button_colors(self):
        """Updates button colors based on whether hoppings exist."""
        if not hasattr(self, "buttons") or not self.buttons:
            return

        # Iterate through all buttons and update their colors
        for pos, btn in self.buttons.items():
            i, j = pos
            if pos in self.hopping_data and self.hopping_data[pos]:
                # Has hoppings - blue
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #4a86e8;
                        border: 1px solid #2a56b8;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #3a76d8;
                        border: 1px solid #1a46a8;
                    }
                """
                )
            else:
                # No hoppings - gray
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #e0e0e0;
                        border: 1px solid #aaaaaa;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                        border: 1px solid #777777;
                    }
                """
                )

    def show_hopping_details(self, row, col):
        """Shows details for hopping between states at row,col positions."""
        if not self.states:
            return

        # Update selected states
        self.selected_state1 = self.states[row]
        self.selected_state2 = self.states[col]

        # Highlight the selected button
        for pos, btn in self.buttons.items():
            i, j = pos
            if i == row and j == col:
                # Highlight selected button
                if pos in self.hopping_data and self.hopping_data[pos]:
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #4a86e8;
                            border: 2px solid #2a56b8;
                            border-radius: 3px;
                        }
                    """
                    )
                else:
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #e0e0e0;
                            border: 2px solid #2a56b8;
                            border-radius: 3px;
                        }
                    """
                    )
            else:
                # Reset other buttons using the refresh method
                if pos in self.hopping_data and self.hopping_data[pos]:
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #4a86e8;
                            border: 1px solid #2a56b8;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #3a76d8;
                            border: 1px solid #1a46a8;
                        }
                    """
                    )
                else:
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #e0e0e0;
                            border: 1px solid #aaaaaa;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #d0d0d0;
                            border: 1px solid #777777;
                        }
                    """
                    )

        # Update details label
        state1_info = self.state_info[row]
        state2_info = self.state_info[col]
        self.details_label.setText(
            f"Hopping: {state1_info[0]}.{state1_info[1]} → {state2_info[0]}.{state2_info[1]}"
        )

        # Populate table with existing hopping data
        self.populate_hopping_table(row, col)

    def populate_hopping_table(self, row, col):
        """Fills the table with hopping data for the selected state pair."""
        self.hopping_table.setRowCount(0)  # Clear existing rows

        if (row, col) not in self.hopping_data:
            self.hopping_data[(row, col)] = []

        for idx, hopping in enumerate(self.hopping_data.get((row, col), [])):
            self.hopping_table.insertRow(idx)

            # Add displacement vector components
            d1_item = QTableWidgetItem(str(hopping.displacement[0]))
            d2_item = QTableWidgetItem(str(hopping.displacement[1]))
            d3_item = QTableWidgetItem(str(hopping.displacement[2]))

            # Add amplitude (format as complex number)
            amp_item = QTableWidgetItem(
                f"{hopping.amplitude.real:.2f} + {hopping.amplitude.imag:.2f}j"
            )

            self.hopping_table.setItem(idx, 0, d1_item)
            self.hopping_table.setItem(idx, 1, d2_item)
            self.hopping_table.setItem(idx, 2, d3_item)
            self.hopping_table.setItem(idx, 3, amp_item)

    def add_empty_row(self):
        """Adds an empty row to the hopping table for user input."""
        if not self.selected_state1 or not self.selected_state2:
            return

        # Temporarily disconnect cell changed signal to prevent triggering while adding cells
        self.hopping_table.cellChanged.disconnect(self.on_table_cell_changed)

        try:
            # Get the current row count and add a new row
            row_idx = self.hopping_table.rowCount()
            self.hopping_table.insertRow(row_idx)

            # Add default items (editable)
            for col in range(3):  # displacement columns
                item = QTableWidgetItem("0")
                self.hopping_table.setItem(row_idx, col, item)

            # Add default amplitude
            amp_item = QTableWidgetItem("0.0 + 0.0j")
            self.hopping_table.setItem(row_idx, 3, amp_item)

            # Select the newly added row
            self.hopping_table.selectRow(row_idx)

            # Create a new hopping with default values
            matrix_row = self.states.index(self.selected_state1)
            matrix_col = self.states.index(self.selected_state2)

            displacement = (0, 0, 0)
            amplitude = complex(0.0, 0.0)

            # Create new hopping
            new_hopping = Hopping(
                s1=self.selected_state1,
                s2=self.selected_state2,
                displacement=displacement,
                amplitude=amplitude,
            )

            # Add to hopping data
            if (matrix_row, matrix_col) not in self.hopping_data:
                self.hopping_data[(matrix_row, matrix_col)] = []

            self.hopping_data[(matrix_row, matrix_col)].append(new_hopping)

            # Add hermitian conjugate if needed
            if matrix_row != matrix_col:
                conj_hopping = Hopping(
                    s1=self.selected_state2,
                    s2=self.selected_state1,
                    displacement=(0, 0, 0),
                    amplitude=complex(0.0, 0.0),
                )

                if (matrix_col, matrix_row) not in self.hopping_data:
                    self.hopping_data[(matrix_col, matrix_row)] = []

                self.hopping_data[(matrix_col, matrix_row)].append(conj_hopping)

            # Update UI
            self.refresh_button_colors()

            # Emit signal
            self.hopping_added.emit(new_hopping)
        finally:
            # Reconnect signal
            self.hopping_table.cellChanged.connect(self.on_table_cell_changed)

    def on_table_cell_changed(self, row, column):
        """Handle edits in the table cells."""
        # Temporarily disconnect to prevent recursive calls
        self.hopping_table.cellChanged.disconnect(self.on_table_cell_changed)

        try:
            if not self.selected_state1 or not self.selected_state2:
                return

            matrix_row = self.states.index(self.selected_state1)
            matrix_col = self.states.index(self.selected_state2)

            # Ensure hopping_data dictionary has an entry for this cell
            if (matrix_row, matrix_col) not in self.hopping_data:
                self.hopping_data[(matrix_row, matrix_col)] = []

            # Ensure we have all cells in this row populated before proceeding
            all_cells_populated = True
            for col in range(4):
                item = self.hopping_table.item(row, col)
                if item is None:
                    all_cells_populated = False
                    # Create default cell if missing
                    default_value = "0" if col < 3 else "0.0 + 0.0j"
                    self.hopping_table.setItem(
                        row, col, QTableWidgetItem(default_value)
                    )

            # Only continue processing if all cells are now available
            if all_cells_populated:
                # If we're modifying an existing row
                if row < len(self.hopping_data[(matrix_row, matrix_col)]):
                    self.update_existing_hopping(row, column, matrix_row, matrix_col)
                else:
                    # If we're dealing with a new row, create a new hopping
                    self.create_new_hopping_from_row(row, matrix_row, matrix_col)

                # Update UI
                self.refresh_button_colors()
        finally:
            # Reconnect the signal
            self.hopping_table.cellChanged.connect(self.on_table_cell_changed)

    def update_existing_hopping(self, row, column, matrix_row, matrix_col):
        """Update an existing hopping based on table cell edit."""
        # Get the current hopping
        hopping = self.hopping_data[(matrix_row, matrix_col)][row]

        # Get values from all cells in this row
        try:
            d1 = int(self.hopping_table.item(row, 0).text())
            d2 = int(self.hopping_table.item(row, 1).text())
            d3 = int(self.hopping_table.item(row, 2).text())

            # Parse complex amplitude
            amp_text = self.hopping_table.item(row, 3).text()
            # Handle complex number formats like "1.0 + 2.0j" or "1.0+2.0j" or "1.0,2.0"
            amp_text = amp_text.replace(" ", "").replace("j", "").replace("i", "")

            if "+" in amp_text:
                parts = amp_text.split("+")
                real = float(parts[0])
                imag = float(parts[1])
            elif "," in amp_text:
                parts = amp_text.split(",")
                real = float(parts[0])
                imag = float(parts[1])
            else:
                real = float(amp_text)
                imag = 0.0

            amplitude = complex(real, imag)

            # Create displacement tuple
            displacement = (d1, d2, d3)

            # Update hopping
            old_hopping = hopping

            # Create new hopping with updated values
            new_hopping = Hopping(
                s1=self.selected_state1,
                s2=self.selected_state2,
                displacement=displacement,
                amplitude=amplitude,
            )

            # Replace the old hopping
            self.hopping_data[(matrix_row, matrix_col)][row] = new_hopping

            # Update the conjugate hopping for symmetry
            if matrix_row != matrix_col:
                self.update_conjugate_hopping(
                    old_hopping, new_hopping, matrix_row, matrix_col
                )

            # Emit signal
            self.hopping_added.emit(new_hopping)

        except (ValueError, IndexError) as e:
            print(f"Error updating hopping: {e}")
            # Revert to previous values if parsing fails
            self.populate_hopping_table(matrix_row, matrix_col)

    def create_new_hopping_from_row(self, row, matrix_row, matrix_col):
        """Create a new hopping from a table row."""
        try:
            # Safety checks for items
            for col in range(4):
                if self.hopping_table.item(row, col) is None:
                    default_value = "0" if col < 3 else "0.0 + 0.0j"
                    self.hopping_table.setItem(
                        row, col, QTableWidgetItem(default_value)
                    )

            # Get values from the table cells
            d1 = int(self.hopping_table.item(row, 0).text())
            d2 = int(self.hopping_table.item(row, 1).text())
            d3 = int(self.hopping_table.item(row, 2).text())

            # Parse complex amplitude
            amp_text = self.hopping_table.item(row, 3).text()
            amp_text = amp_text.replace(" ", "").replace("j", "").replace("i", "")

            try:
                if "+" in amp_text:
                    parts = amp_text.split("+")
                    real = float(parts[0])
                    imag = float(parts[1])
                elif "," in amp_text:
                    parts = amp_text.split(",")
                    real = float(parts[0])
                    imag = float(parts[1])
                else:
                    real = float(amp_text)
                    imag = 0.0
            except (ValueError, IndexError):
                # If parsing fails, default to zero
                real = 0.0
                imag = 0.0

            amplitude = complex(real, imag)
            displacement = (d1, d2, d3)

            # Check if this is a duplicate displacement
            is_duplicate = False
            for existing_hopping in self.hopping_data.get((matrix_row, matrix_col), []):
                if existing_hopping.displacement == displacement:
                    is_duplicate = True
                    break

            if is_duplicate:
                print(
                    f"Duplicate displacement {displacement} - updating existing entry"
                )
                # Find and update the existing entry instead of creating a new one
                for idx, existing_hopping in enumerate(
                    self.hopping_data[(matrix_row, matrix_col)]
                ):
                    if existing_hopping.displacement == displacement:
                        new_hopping = Hopping(
                            s1=self.selected_state1,
                            s2=self.selected_state2,
                            displacement=displacement,
                            amplitude=amplitude,
                        )
                        self.hopping_data[(matrix_row, matrix_col)][idx] = new_hopping

                        # Update the conjugate if needed
                        if matrix_row != matrix_col:
                            self.update_conjugate_for_displacement(
                                displacement, amplitude, matrix_row, matrix_col
                            )
                        break
            else:
                # Create new hopping
                new_hopping = Hopping(
                    s1=self.selected_state1,
                    s2=self.selected_state2,
                    displacement=displacement,
                    amplitude=amplitude,
                )

                # Add to hopping data
                self.hopping_data[(matrix_row, matrix_col)].append(new_hopping)

                # Add the hermitian conjugate for symmetry
                if matrix_row != matrix_col:
                    conj_displacement = (-d1, -d2, -d3)
                    conj_amplitude = amplitude.conjugate()

                    conj_hopping = Hopping(
                        s1=self.selected_state2,
                        s2=self.selected_state1,
                        displacement=conj_displacement,
                        amplitude=conj_amplitude,
                    )

                    if (matrix_col, matrix_row) not in self.hopping_data:
                        self.hopping_data[(matrix_col, matrix_row)] = []

                    self.hopping_data[(matrix_col, matrix_row)].append(conj_hopping)

            # Emit signal for either case
            self.hopping_added.emit(new_hopping)

            # Format the display of the amplitude nicely
            amp_item = self.hopping_table.item(row, 3)
            amp_item.setText(f"{amplitude.real:.2f} + {amplitude.imag:.2f}j")

        except (ValueError, IndexError, AttributeError) as e:
            print(f"Error creating hopping: {e}")
            # Don't remove the row, just populate with defaults
            for col in range(4):
                if self.hopping_table.item(row, col) is None:
                    default_value = "0" if col < 3 else "0.0 + 0.0j"
                    self.hopping_table.setItem(
                        row, col, QTableWidgetItem(default_value)
                    )

    def update_conjugate_for_displacement(
        self, displacement, amplitude, matrix_row, matrix_col
    ):
        """Update the conjugate hopping for a specific displacement."""
        conj_displacement = (-displacement[0], -displacement[1], -displacement[2])
        conj_amplitude = amplitude.conjugate()

        # Look for existing conjugate with this displacement
        found = False

        if (matrix_col, matrix_row) in self.hopping_data:
            for idx, hopping in enumerate(self.hopping_data[(matrix_col, matrix_row)]):
                if hopping.displacement == conj_displacement:
                    # Update the existing conjugate
                    new_conj = Hopping(
                        s1=self.selected_state2,
                        s2=self.selected_state1,
                        displacement=conj_displacement,
                        amplitude=conj_amplitude,
                    )

                    self.hopping_data[(matrix_col, matrix_row)][idx] = new_conj
                    found = True
                    break

        # If not found, create new conjugate
        if not found:
            new_conj = Hopping(
                s1=self.selected_state2,
                s2=self.selected_state1,
                displacement=conj_displacement,
                amplitude=conj_amplitude,
            )

            if (matrix_col, matrix_row) not in self.hopping_data:
                self.hopping_data[(matrix_col, matrix_row)] = []

            self.hopping_data[(matrix_col, matrix_row)].append(new_conj)

    def update_conjugate_hopping(
        self, old_hopping, new_hopping, matrix_row, matrix_col
    ):
        """Update the conjugate hopping when the original is modified."""
        # Find the conjugate hopping
        old_conj_displacement = (
            -old_hopping.displacement[0],
            -old_hopping.displacement[1],
            -old_hopping.displacement[2],
        )

        if (matrix_col, matrix_row) in self.hopping_data:
            for i, h in enumerate(self.hopping_data[(matrix_col, matrix_row)]):
                if h.displacement == old_conj_displacement:
                    # Create new conjugate
                    new_conj_displacement = (
                        -new_hopping.displacement[0],
                        -new_hopping.displacement[1],
                        -new_hopping.displacement[2],
                    )
                    new_conj_amplitude = new_hopping.amplitude.conjugate()

                    new_conj_hopping = Hopping(
                        s1=self.selected_state2,
                        s2=self.selected_state1,
                        displacement=new_conj_displacement,
                        amplitude=new_conj_amplitude,
                    )

                    # Replace the old conjugate
                    self.hopping_data[(matrix_col, matrix_row)][i] = new_conj_hopping
                    break

    def remove_selected_hopping(self):
        """Removes the selected hopping from the table."""
        current_row = self.hopping_table.currentRow()
        if current_row < 0:
            return

        if not self.selected_state1 or not self.selected_state2:
            return

        # Find row and col for the selected states
        row = self.states.index(self.selected_state1)
        col = self.states.index(self.selected_state2)

        if (row, col) in self.hopping_data and current_row < len(
            self.hopping_data[(row, col)]
        ):
            # Get the hopping to be removed
            hopping = self.hopping_data[(row, col)][current_row]

            # Remove from hopping data
            self.hopping_data[(row, col)].pop(current_row)

            # Find and remove the hermitian conjugate hopping if it exists
            if row != col:  # Only if not on diagonal
                conj_displacement = (
                    -hopping.displacement[0],
                    -hopping.displacement[1],
                    -hopping.displacement[2],
                )

                # Find the matching conjugate hopping
                if (col, row) in self.hopping_data:
                    for i, h in enumerate(self.hopping_data[(col, row)]):
                        if h.displacement == conj_displacement:
                            self.hopping_data[(col, row)].pop(i)
                            break

            # Update UI
            self.refresh_button_colors()
            self.populate_hopping_table(row, col)

            # Emit signal
            self.hopping_removed.emit(hopping)
