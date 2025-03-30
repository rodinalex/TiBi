from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QLabel,
    QFrame,
    QDialog,
    QLineEdit,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import numpy as np
from src.tibitypes import Hopping


class HoppingMatrix(QWidget):
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

        # Table for hopping details
        self.hopping_table = QTableWidget(0, 4)  # 4 columns: d1, d2, d3, amplitude
        self.hopping_table.setHorizontalHeaderLabels(["d₁", "d₂", "d₃", "Amplitude"])
        self.hopping_table.setColumnWidth(0, 40)  # d₁
        self.hopping_table.setColumnWidth(1, 40)  # d₂
        self.hopping_table.setColumnWidth(2, 40)  # d₃

        # Make the table columns resize to content
        self.hopping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        details_layout.addWidget(self.hopping_table)

        # Form for adding new hopping
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)

        # Displacement vector inputs
        d_layout = QHBoxLayout()

        self.d1_spin = QSpinBox()
        self.d2_spin = QSpinBox()
        self.d3_spin = QSpinBox()

        d_layout.addWidget(QLabel("d<sub>1</sub>:"))
        d_layout.addWidget(self.d1_spin)
        d_layout.addWidget(QLabel("d<sub>2</sub>:"))
        d_layout.addWidget(self.d2_spin)
        d_layout.addWidget(QLabel("d<sub>3</sub>:"))
        d_layout.addWidget(self.d3_spin)

        # Add the grouped row to the form layout
        form_layout.addRow(d_layout)

        # Complex amplitude inputs
        amp_layout = QHBoxLayout()

        self.amp_real = QDoubleSpinBox()
        self.amp_real.setSingleStep(0.1)

        self.amp_imag = QDoubleSpinBox()
        self.amp_imag.setSingleStep(0.1)

        amp_layout.addWidget(self.amp_real)
        amp_layout.addWidget(QLabel("+ i"))
        amp_layout.addWidget(self.amp_imag)
        form_layout.addRow("Amplitude:", amp_layout)
        # Add and remove buttons
        button_layout = QHBoxLayout()

        self.add_hopping_btn = QPushButton("Add")
        self.add_hopping_btn.clicked.connect(self.add_hopping)
        button_layout.addWidget(self.add_hopping_btn)

        self.remove_hopping_btn = QPushButton("Remove")
        self.remove_hopping_btn.clicked.connect(self.remove_selected_hopping)
        button_layout.addWidget(self.remove_hopping_btn)

        form_layout.addRow(button_layout)
        details_layout.addWidget(form_widget)

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

    def add_hopping(self):
        """Adds a new hopping between the selected states."""
        if not self.selected_state1 or not self.selected_state2:
            return

        # Get values from input fields
        displacement = (
            self.d1_spin.value(),
            self.d2_spin.value(),
            self.d3_spin.value(),
        )

        amplitude = complex(self.amp_real.value(), self.amp_imag.value())

        # Create new hopping
        new_hopping = Hopping(
            s1=self.selected_state1,
            s2=self.selected_state2,
            displacement=displacement,
            amplitude=amplitude,
        )

        # Find row and col for the selected states
        row = self.states.index(self.selected_state1)
        col = self.states.index(self.selected_state2)

        # Add to hopping data
        if (row, col) not in self.hopping_data:
            self.hopping_data[(row, col)] = []

        self.hopping_data[(row, col)].append(new_hopping)

        # Also add the hermitian conjugate hopping to ensure symmetry
        if row != col:  # Only if not on diagonal
            # Create conjugate hopping
            conj_displacement = (-displacement[0], -displacement[1], -displacement[2])
            conj_amplitude = amplitude.conjugate()

            conj_hopping = Hopping(
                s1=self.selected_state2,
                s2=self.selected_state1,
                displacement=conj_displacement,
                amplitude=conj_amplitude,
            )

            # Add to hopping data
            if (col, row) not in self.hopping_data:
                self.hopping_data[(col, row)] = []

            self.hopping_data[(col, row)].append(conj_hopping)

        # Update UI
        self.refresh_button_colors()
        self.populate_hopping_table(row, col)

        # Emit signal
        self.hopping_added.emit(new_hopping)

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
