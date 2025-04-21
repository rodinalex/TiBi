import sys
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from ui.uc_plot import UnitCellPlot
from ui.bz_plot import BrillouinZonePlot
from ui.uc import UnitCellUI
from ui.hopping import HoppingPanel
from ui.band_plot import BandStructurePlot
from ui.placeholder import PlaceholderWidget

from controllers.app_controller import AppController
from controllers.hopping_controller import HoppingController
from controllers.bz_controller import BZController
from controllers.computation_controller import ComputationController

from models.uc_models import DataModel


class MainWindow(QMainWindow):
    """
    Main application window that defines the UI layout.
    
    This class is purely a view component that arranges the UI elements and
    doesn't contain business logic or model manipulation.
    """
    
    def __init__(self, uc_ui, hopping_panel, unit_cell_plot, bz_plot, band_plot):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1500, 900))
        
        # Store references to UI components
        self.uc = uc_ui
        self.hopping = hopping_panel
        self.unit_cell_plot = unit_cell_plot
        self.bz_plot = bz_plot
        self.band_plot = band_plot
        
        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)
        
        # Create three column layouts
        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # Left column for hierarchical view and form panels
        left_layout.addWidget(self.uc, stretch=1)
        left_layout.addWidget(self.hopping, stretch=2)
        
        # 3D visualization for the unit cell
        mid_layout.addWidget(self.unit_cell_plot, stretch=1)
        mid_layout.addWidget(self.bz_plot, stretch=1)
        mid_layout.addWidget(PlaceholderWidget("SPOT"), stretch=1)
        
        # Right column for computation options and band structure
        right_layout.addWidget(self.band_plot, stretch=1)
        right_layout.addWidget(PlaceholderWidget("BAND"), stretch=1)
        
        # Add the columns to the main layout
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(mid_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=2)
        
        # Set as central widget
        self.setCentralWidget(main_view)


class TiBiApplication:
    """
    Main application class that initializes and connects all components.
    
    This class is responsible for:
    1. Creating models
    2. Creating views
    3. Creating controllers
    4. Connecting everything together
    5. Starting the application
    """
    
    def __init__(self):
        """Initialize the application without creating components yet."""
        # Create the Qt application
        self.app = QApplication(sys.argv)
        
        # Will hold references to components
        self.models = {}
        self.views = {}
        self.controllers = {}
        self.main_window = None
    
    def initialize(self):
        """Initialize all application components."""
        self._create_models()
        self._create_views()
        self._create_controllers()
        self._create_main_window()
        return self
    
    def _create_models(self):
        """Create all data models used by the application."""
        # These would ideally be extracted from UnitCellUI and other components
        # For now, we'll create them here but they'll still be duplicated in UnitCellUI
        self.models["unit_cells"] = {}  # Dictionary of unit cells by UUID
        self.models["bz"] = {"bz_vertices": [], "bz_faces": []}  # BZ data
    
    def _create_views(self):
        """Create all UI components."""
        # Initialize UI components
        # These components currently create their own models internally
        # Later we'll refactor them to accept models as parameters
        self.views["uc_ui"] = UnitCellUI()
        self.views["unit_cell_plot"] = UnitCellPlot()
        self.views["bz_plot"] = BrillouinZonePlot()
        self.views["band_plot"] = BandStructurePlot()
        self.views["hopping"] = HoppingPanel(self.views["uc_ui"].unit_cells)
    
    def _create_controllers(self):
        """Create and connect all controllers."""
        # Specialized controllers
        self.controllers["hopping_controller"] = HoppingController(
            self.views["uc_ui"].unit_cells,  # Using the model from UnitCellUI for now
            self.views["hopping"]
        )
        
        self.controllers["bz_controller"] = BZController(
            self.views["bz_plot"]
        )
        
        self.controllers["computation_controller"] = ComputationController(
            self.views["uc_ui"].unit_cells,  # Using the model from UnitCellUI for now
            self.controllers["bz_controller"],
            self.views["band_plot"]
        )
        
        # Main application controller
        self.controllers["app_controller"] = AppController(
            self.views["uc_ui"],
            self.views["hopping"],
            self.views["unit_cell_plot"],
            self.views["bz_plot"],
            self.views["band_plot"]
        )
        
        # Update the AppController with references to specialized controllers
        self.controllers["app_controller"].hopping_controller = self.controllers["hopping_controller"]
        self.controllers["app_controller"].bz_controller = self.controllers["bz_controller"]
        self.controllers["app_controller"].computation_controller = self.controllers["computation_controller"]
        
        # Connect cross-controller signals
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect signals between controllers and views."""
        # Each controller should connect its own internal signals,
        # but cross-controller signals are connected here
        
        # Connect selection changes to controllers
        self.views["uc_ui"].selection.signals.updated.connect(
            lambda: self.controllers["hopping_controller"].set_unit_cell(
                self.views["uc_ui"].selection.get("unit_cell", None)
            )
        )
        
        self.views["uc_ui"].selection.signals.updated.connect(
            lambda: self.controllers["computation_controller"].set_unit_cell(
                self.views["uc_ui"].selection.get("unit_cell", None)
            )
        )
    
    def _create_main_window(self):
        """Create the main application window."""
        self.main_window = MainWindow(
            self.views["uc_ui"],
            self.views["hopping"],
            self.views["unit_cell_plot"],
            self.views["bz_plot"],
            self.views["band_plot"]
        )
    
    def run(self):
        """Run the application."""
        self.main_window.show()
        return self.app.exec()


def main():
    """Application entry point."""
    # Create and initialize the application
    app = TiBiApplication().initialize()
    
    # Run the application
    return app.run()


if __name__ == "__main__":
    sys.exit(main())