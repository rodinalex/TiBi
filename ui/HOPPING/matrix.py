from PySide6.QtWidgets import (
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from src.tibitypes import State


class HoppingMatrix(QWidget):
    # A Signal notifying which pair of states is being selected for coupling modification
    button_clicked = Signal(State, State)

    def __init__(self):
        super().__init__()
        # Store tuples of (site_name, state_name, state_id).
        # We do NOT need the complete state structure here
        self.states = []

        self.state_info = []
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

    def set_states(self, new_states, new_info):
        """Setter for states that also refreshes the matrix. Occurs on every tree selection"""
        self.states = new_states
        self.state_info = new_info
        self.refresh_matrix()

    def refresh_matrix(self):
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

                # Set tooltip to show both states when hovering.
                state1_info = self.state_info[ii]
                state2_info = self.state_info[jj]
                # Show the state and site names.
                # From second quantization, the hopping goes FROM column INTO row
                # (columns multiply annihilation operators, rows multiply creation)
                btn.setToolTip(
                    f"{state2_info[0]}.{state2_info[1]} → {state1_info[0]}.{state1_info[1]}"
                )

                # Button click can be bound to a function with no arguments.
                # The bound function itself emits a button_clicked signal that carries
                # the states corrsponding to the appropriate grid entry
                # Use lambda with default args to capture correct i,j values
                btn.clicked.connect(
                    lambda checked=False, row=ii, col=jj: self.button_clicked.emit(
                        self.states[row], self.states[col]
                    )
                )

                self.grid_layout.addWidget(btn, ii, jj)
                self.buttons[(ii, jj)] = btn
        # Force update the layout
        # self.content_widget.setLayout(self.grid_layout)
        # self.content_widget.update()
        # self.update()

    # Update button colors based on existing hoppings


#     self.refresh_button_colors()


# def refresh_button_colors(self):
#     """Updates button colors based on whether hoppings exist."""
#     if not hasattr(self, "buttons") or not self.buttons:
#         return

#     # Iterate through all buttons and update their colors
#     for pos, btn in self.buttons.items():
#         i, j = pos
#         if pos in self.hopping_data and self.hopping_data[pos]:
#             # Has hoppings - blue
#             btn.setStyleSheet(
#                 """
#                 QPushButton {
#                     background-color: #4a86e8;
#                     border: 1px solid #2a56b8;
#                     border-radius: 3px;
#                 }
#                 QPushButton:hover {
#                     background-color: #3a76d8;
#                     border: 1px solid #1a46a8;
#                 }
#             """
#             )
#         else:
#             # No hoppings - gray
#             btn.setStyleSheet(
#                 """
#                 QPushButton {
#                     background-color: #e0e0e0;
#                     border: 1px solid #aaaaaa;
#                     border-radius: 3px;
#                 }
#                 QPushButton:hover {
#                     background-color: #d0d0d0;
#                     border: 1px solid #777777;
#                 }
#             """
#             )
