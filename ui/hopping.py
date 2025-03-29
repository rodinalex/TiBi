from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QLabel,
    QFrame,
    QDialog,
    QLineEdit,
    QFormLayout,
)
from PySide6.QtCore import Qt


class HoppingMatrix(QWidget):
    def __init__(self, unit_cell):
        super().__init__()

        #         self.states = states  # List of state names
        #         self.hopping_data = {}  # Stores hopping info for each pair

        layout = QVBoxLayout(self)


#         # --- Scrollable Area ---
#         scroll_area = QScrollArea()
#         scroll_area.setWidgetResizable(True)
#         content_widget = QWidget()
#         grid_layout = QGridLayout(content_widget)

#         # --- Create Fixed Row & Column Headers ---
#         self.labels = []
#         for i, state in enumerate(self.states):
#             lbl_row = QLabel(state)
#             lbl_col = QLabel(state)
#             lbl_row.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
#             lbl_col.setAlignment(Qt.AlignCenter)
#             self.labels.append((lbl_row, lbl_col))

#             grid_layout.addWidget(lbl_row, i + 1, 0)  # Row header
#             grid_layout.addWidget(lbl_col, 0, i + 1)  # Column header

#         # --- Create Square Buttons ---
#         self.buttons = {}
#         for i in range(len(self.states)):
#             for j in range(len(self.states)):
#                 btn = QPushButton("")
#                 btn.setFixedSize(40, 40)  # Ensures square buttons
#                 btn.setStyleSheet("background-color: gray;")  # Default color
#                 btn.clicked.connect(lambda checked, x=i, y=j: self.edit_hopping(x, y))
#                 grid_layout.addWidget(btn, i + 1, j + 1)
#                 self.buttons[(i, j)] = btn

#         content_widget.setLayout(grid_layout)
#         scroll_area.setWidget(content_widget)

#         # --- Styling ---
#         grid_layout.setSpacing(5)
#         scroll_area.setFrameStyle(QFrame.NoFrame)

#         main_layout.addWidget(scroll_area)

#     def edit_hopping(self, i, j):
#         """Opens a small form to edit hopping terms."""
#         dialog = QDialog(self)
#         dialog.setWindowTitle(f"Edit Hopping: {self.states[i]} → {self.states[j]}")
#         layout = QFormLayout(dialog)

#         amp_input = QLineEdit()
#         layout.addRow("Hopping Amplitude:", amp_input)

#         save_btn = QPushButton("Save")
#         save_btn.clicked.connect(lambda: self.save_hopping(i, j, amp_input.text(), dialog))
#         layout.addWidget(save_btn)

#         dialog.setLayout(layout)
#         dialog.exec()

#     def save_hopping(self, i, j, value, dialog):
#         """Stores hopping and updates button color."""
#         if value:
#             self.hopping_data[(i, j)] = float(value)
#             self.buttons[(i, j)].setStyleSheet("background-color: blue;")  # Indicate hopping
#         else:
#             self.hopping_data.pop((i, j), None)
#             self.buttons[(i, j)].setStyleSheet("background-color: gray;")  # Reset
#         dialog.accept()

# if __name__ == "__main__":
#     app = QApplication([])
#     window = HoppingMatrix(["A", "B", "C", "D", "E"])  # Example states
#     window.show()
#     app.exec()
