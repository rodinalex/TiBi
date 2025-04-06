from PySide6.QtWidgets import (
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QMenu,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction
import numpy as np


class HoppingMatrix(QWidget):
    """
    A grid of buttons representing possible hopping connections between quantum states.

    Each button in the grid represents a possible hopping between two states.
    The rows represent the destination states and columns represent the source states.
    Buttons are colored differently based on whether a hopping exists or not.
    """

    # Signal emitted when a button is clicked, carrying the source and destination state info
    # Params: (source_state_info, destination_state_info) where each is (site_name, state_name, state_id)
    button_clicked = Signal(object, object)

    # Signal emitted when couplings are modified from right-clicking on the button grid.
    # The signal triggers a table and matrix update
    hoppings_changed = Signal()

    # Button style constants
    BUTTON_STYLE_DEFAULT = """
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

    BUTTON_STYLE_HAS_HOPPING = """
        QPushButton {
            background-color: #56b4e9;
            border: 1px solid #0072b2;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #50a7d9;
            border: 1px solid #015a8c;
        }
    """
    BUTTON_STYLE_NONHERMITIAN = """
        QPushButton {
            background-color: #cc79a7;
            border: 1px solid #d55c00;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #b86593;
            border: 1px solid #b34e02;
        }
    """

    def __init__(self, hopping_data):
        super().__init__()
        # Store tuples of (site_name, state_name, state_id).
        # We do NOT need the complete state structure here
        self.states = []
        self.hopping_data = hopping_data
        # Keep all the grid buttons as we will change their appearance based on the coupling
        self.buttons = {}
        layout = QVBoxLayout(self)

        # Scrollable Area for Matrix
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Content widget for grid
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(3)

        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        title_label = QLabel("Coupling Matrix")
        title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(title_label)
        layout.addWidget(self.scroll_area)

        # Initialize the button matrix
        self.refresh_matrix()

    def set_states(self, new_states):
        """Setter for states that also refreshes the matrix. Occurs on every tree selection"""
        self.states = new_states
        self.refresh_matrix()

    def set_hopping_data(self, new_hopping_data):
        """Setter for hopping data that also refreshes the matrix. Occurs on every tree selection"""
        self.hopping_data = new_hopping_data
        self.refresh_matrix()

    def refresh_matrix(self):
        """
        Refreshes the entire matrix grid by removing all existing buttons and recreating them.
        Updates button colors based on whether hoppings exist between states.
        """
        # Clear existing widgets in grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Configure grid layout to center the content
        self.grid_layout.setAlignment(Qt.AlignCenter)

        # --- Create the button grid ---
        self.buttons = {}
        for ii in range(len(self.states)):
            for jj in range(len(self.states)):
                btn = QPushButton("")
                btn.setFixedSize(20, 20)
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(
                    lambda _, row=ii, col=jj, b=btn: self.add_context_menu(b, row, col)
                )
                # Apply the default style (no hopping initially)
                self.apply_button_style(btn, False)

                # Set tooltip to show both states when hovering.
                state1 = self.states[ii]
                state2 = self.states[jj]
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
                        self.states[row], self.states[col]
                    )
                )

                self.grid_layout.addWidget(btn, ii, jj)
                self.buttons[(ii, jj)] = btn
        # Update button colors based on existing hoppings

        self.refresh_button_colors()

    def apply_button_style(self, button, has_hopping, hermitian=False):
        """
        Apply the appropriate style to a button based on whether it has hoppings.

        Args:
            button: The QPushButton to style
            has_hopping: Boolean indicating whether the button represents a connection with hoppings
            hermitian: Boolean indicating whether the coupling is Hermitian
        """
        if not has_hopping:
            style = self.BUTTON_STYLE_DEFAULT
        else:
            if hermitian:
                style = self.BUTTON_STYLE_HAS_HOPPING
            else:
                style = self.BUTTON_STYLE_NONHERMITIAN

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
            s1 = self.states[ii][2]  # Destination state ID
            s2 = self.states[jj][2]  # Source state ID
            hop = set(self.hopping_data.get((s1, s2), []))
            hop_herm = set(self.hopping_data.get((s2, s1), []))
            has_hopping = bool(hop)

            hop_neg_conj = set(
                ((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop
            )
            is_hermitian = hop_neg_conj == hop_herm
            # Apply the appropriate style based on hopping existence
            self.apply_button_style(btn, has_hopping, is_hermitian)

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
        s1 = self.states[ii][2]  # Destination
        s2 = self.states[jj][2]  # Source
        hop = self.hopping_data.get((s1, s2), [])
        hop_herm = [((-d1, -d2, -d3), np.conj(x)) for ((d1, d2, d3), x) in hop]
        self.hopping_data[(s2, s1)] = hop_herm
        self.hoppings_changed.emit()

    def delete_coupling(self, ii, jj):
        s1 = self.states[ii][2]  # Destination
        s2 = self.states[jj][2]  # Source
        self.hopping_data.pop((s1, s2), None)
        self.hoppings_changed.emit()
