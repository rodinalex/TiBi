import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
    QLabel,
    QStackedWidget,
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from models.uc_models import UCFormModel
from src.tibitypes import UnitCell, BasisVector
from controllers.uc_cotroller import UCController
from ui.UC.unit_cell_panel import UnitCellPanel
from ui.UC.site_panel import SitePanel
from ui.UC.state_panel import StatePanel
from ui.UC.tree_view import TreeViewPanel
from ui.UC.unit_cell_plot import UnitCellPlot
from ui.uc import UnitCellUI


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1200, 800))  # Slightly wider to accommodate 3D plot

        # Initialize UI panels
        self.uc = UnitCellUI()
        
        # Initialize the plot
        self.unit_cell_plot = UnitCellPlot()

        # # Connect action buttons to controller methods
        # # Unit cell panel buttons
        # self.unit_cell_panel.add_btn.clicked.connect(self.add_unit_cell)
        # self.unit_cell_panel.apply_btn.clicked.connect(self.apply_unit_cell_changes)
        # self.unit_cell_panel.delete_btn.clicked.connect(self.delete_unit_cell)

        # # Site panel buttons
        # self.site_panel.add_btn.clicked.connect(self.add_site)
        # self.site_panel.apply_btn.clicked.connect(self.apply_site_changes)
        # self.site_panel.delete_btn.clicked.connect(self.delete_site)

        # # State panel buttons
        # self.state_panel.add_btn.clicked.connect(self.add_state)
        # self.state_panel.apply_btn.clicked.connect(self.apply_state_changes)
        # self.state_panel.delete_btn.clicked.connect(self.delete_state)

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left column for hierarchical view and form panels
        # left_layout.addWidget(self.tree_view_panel, stretch=2)
        # left_layout.addWidget(self.form_stack, stretch=1)
        left_layout.addWidget(self.uc)

        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=3)
        
        # Connect signals to update the plot when unit cell or site is selected
        self.uc.tree_view_panel.unit_cell_selected.connect(self.update_plot)
        self.uc.tree_view_panel.site_selected.connect(self.highlight_site)
        
        # Placeholder for hopping parameters (to be implemented later)
        mid_layout.addWidget(PlaceholderWidget("Hopping Parameters"), stretch=1)

        right_layout.addWidget(PlaceholderWidget("Computation Options"))
        right_layout.addWidget(PlaceholderWidget("Computation Input"))

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(mid_layout, stretch=5)
        main_layout.addLayout(right_layout, stretch=3)

        self.setCentralWidget(main_view)
        
    def update_plot(self, unit_cell_id):
        """Update the 3D plot with the selected unit cell"""
        if unit_cell_id in self.uc.controller.model:
            unit_cell = self.uc.controller.model[unit_cell_id]
            self.unit_cell_plot.set_unit_cell(unit_cell)
            
    def highlight_site(self, unit_cell_id, site_id):
        """Highlight the selected site in the 3D plot"""
        # First update the plot with the current unit cell
        self.update_plot(unit_cell_id)
        # Then highlight the specific site
        self.unit_cell_plot.select_site(site_id)
        
    def add_demo_unit_cell(self):
        """Add a demo unit cell with sites for testing visualization"""
        # This method can be called from the Python console after loading the app
        # for easily adding a test unit cell with sites
        
        from src.tibitypes import UnitCell, Site, BasisVector
        
        # Create a simple cubic unit cell
        v1 = BasisVector(1.0, 0.0, 0.0)
        v2 = BasisVector(0.0, 1.0, 0.0)
        v3 = BasisVector(0.0, 0.0, 1.0)
        demo_uc = UnitCell("Demo Cubic Cell", v1, v2, v3)
        
        # Add sites at different positions
        sites = [
            Site("Corner", 0.0, 0.0, 0.0),
            Site("Face Center X", 0.5, 0.0, 0.0),
            Site("Face Center Y", 0.0, 0.5, 0.0),
            Site("Face Center Z", 0.0, 0.0, 0.5),
            Site("Body Center", 0.5, 0.5, 0.5)
        ]
        
        for site in sites:
            demo_uc.sites[site.id] = site
            
        # Add the unit cell to the model
        self.uc.controller.model[demo_uc.id] = demo_uc
        
        # Refresh the tree and select this unit cell
        self.uc.tree_view_panel.refresh_tree()
        self.uc.tree_view_panel.select_unit_cell(demo_uc.id)
        
        return demo_uc.id

    # def add_demo_data(self):
    #     """Add some demo data to show functionality"""
    #     # Add a unit cell
    #     uc_id = self.controller.add_unit_cell("Silicon")

    #     # Add some sites
    #     site1_id = self.controller.add_site(uc_id, "Si1", 0.0, 0.0, 0.0)
    #     site2_id = self.controller.add_site(uc_id, "Si2", 0.25, 0.25, 0.25)

    #     # Add some states
    #     self.controller.add_state(uc_id, site1_id, "s orbital", -10.0)
    #     self.controller.add_state(uc_id, site1_id, "p orbital", -5.0)
    #     self.controller.add_state(uc_id, site2_id, "s orbital", -10.0)
    #     self.controller.add_state(uc_id, site2_id, "p orbital", -5.0)

    # # Action handler methods
    # def add_unit_cell(self):
    #     """Handle adding a new unit cell"""
    #     name = unit_cell_model["name"]
    #     v1 = BasisVector(
    #         float(unit_cell_model["v1x"]),
    #         float(unit_cell_model["v1y"]),
    #         float(unit_cell_model["v1z"]),
    #     )
    #     v2 = BasisVector(
    #         float(unit_cell_model["v2x"]),
    #         float(unit_cell_model["v2y"]),
    #         float(unit_cell_model["v2z"]),
    #     )
    #     v3 = BasisVector(
    #         float(unit_cell_model["v3x"]),
    #         float(unit_cell_model["v3y"]),
    #         float(unit_cell_model["v3z"]),
    #     )

    #     new_uc_id = self.controller.add_unit_cell(name)
    #     self.controller.edit_unit_cell(new_uc_id, name=name, v1=v1, v2=v2, v3=v3)

    # def apply_unit_cell_changes(self):
    #     """Apply changes to the currently selected unit cell"""
    #     if self.current_unit_cell_id:
    #         name = unit_cell_model["name"]
    #         v1 = BasisVector(
    #             float(unit_cell_model["v1x"]),
    #             float(unit_cell_model["v1y"]),
    #             float(unit_cell_model["v1z"]),
    #         )
    #         v2 = BasisVector(
    #             float(unit_cell_model["v2x"]),
    #             float(unit_cell_model["v2y"]),
    #             float(unit_cell_model["v2z"]),
    #         )
    #         v3 = BasisVector(
    #             float(unit_cell_model["v3x"]),
    #             float(unit_cell_model["v3y"]),
    #             float(unit_cell_model["v3z"]),
    #         )

    #         self.controller.edit_unit_cell(
    #             self.current_unit_cell_id, name=name, v1=v1, v2=v2, v3=v3
    #         )

    # def delete_unit_cell(self):
    #     """Handle deleting the selected unit cell"""
    #     if self.current_unit_cell_id:
    #         self.controller.delete_unit_cell(self.current_unit_cell_id)
    #         self.current_unit_cell_id = None
    #         self.current_site_id = None
    #         self.current_state_id = None

    # def add_site(self):
    #     """Handle adding a new site to the selected unit cell"""
    #     if self.current_unit_cell_id:
    #         name = site_model["name"]
    #         c1 = float(site_model["c1"])
    #         c2 = float(site_model["c2"])
    #         c3 = float(site_model["c3"])

    #         self.controller.add_site(self.current_unit_cell_id, name, c1, c2, c3)

    # def apply_site_changes(self):
    #     """Apply changes to the currently selected site"""
    #     if self.current_unit_cell_id and self.current_site_id:
    #         name = site_model["name"]
    #         c1 = float(site_model["c1"])
    #         c2 = float(site_model["c2"])
    #         c3 = float(site_model["c3"])

    #         self.controller.edit_site(
    #             self.current_unit_cell_id, self.current_site_id, name, c1, c2, c3
    #         )

    # def delete_site(self):
    #     """Handle deleting the selected site"""
    #     if self.current_unit_cell_id and self.current_site_id:
    #         self.controller.delete_site(self.current_unit_cell_id, self.current_site_id)
    #         self.current_site_id = None
    #         self.current_state_id = None

    # def add_state(self):
    #     """Handle adding a new state to the selected site"""
    #     if self.current_unit_cell_id and self.current_site_id:
    #         name = state_model["name"]
    #         energy = float(state_model["energy"])

    #         self.controller.add_state(
    #             self.current_unit_cell_id, self.current_site_id, name, energy
    #         )

    # def apply_state_changes(self):
    #     """Apply changes to the currently selected state"""
    #     if self.current_unit_cell_id and self.current_site_id and self.current_state_id:
    #         name = state_model["name"]
    #         energy = float(state_model["energy"])

    #         self.controller.edit_state(
    #             self.current_unit_cell_id,
    #             self.current_site_id,
    #             self.current_state_id,
    #             name,
    #             energy,
    #         )

    # def delete_state(self):
    #     """Handle deleting the selected state"""
    #     if self.current_unit_cell_id and self.current_site_id and self.current_state_id:
    #         self.controller.delete_state(
    #             self.current_unit_cell_id, self.current_site_id, self.current_state_id
    #         )
    #         self.current_state_id = None


class PlaceholderWidget(QWidget):
    """Placeholder widget with a label to show where future components will go"""

    def __init__(self, name):
        super().__init__()
        self.setAutoFillBackground(True)

        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        # Add a label
        layout = QVBoxLayout(self)
        label = QLabel(f"[{name}]")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


app = QApplication(sys.argv)
window = MainWindow()

# Create a demo unit cell for testing the visualization
window.add_demo_unit_cell()

window.show()
app.exec()
