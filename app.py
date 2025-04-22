import sys
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from views.placeholder import PlaceholderWidget
from views.uc import UnitCellView
from views.hopping import HoppingView

from controllers.app_controller import AppController
from controllers.hopping_controller import HoppingController
from controllers.uc_controller import UnitCellController

# from controllers.bz_controller import BZController
# from controllers.computation_controller import ComputationController

from models.data_models import DataModel


class MainWindow(QMainWindow):
    """
    Main application window that defines the UI layout.

    This class is purely a view component that arranges the UI elements and
    doesn't contain business logic or model manipulation.
    """

    def __init__(self, uc, hopping):
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1500, 900))

        # Store references to UI components
        self.uc = uc
        self.hopping = hopping
        # self.unit_cell_plot = unit_cell_plot
        # self.bz_plot = bz_plot
        # self.band_plot = band_plot

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
        mid_layout.addWidget(PlaceholderWidget("TEST"), stretch=1)
        mid_layout.addWidget(PlaceholderWidget("TEST"), stretch=1)
        mid_layout.addWidget(PlaceholderWidget("SPOT"), stretch=1)

        # Right column for computation options and band structure
        right_layout.addWidget(PlaceholderWidget("TEST"), stretch=1)
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

        # References to components
        self.models = {}
        self.views = {}
        self.controllers = {}
        self.main_window = None

        # Set models
        self.models["unit_cells"] = {}  # Dictionary of unit cells by UUID

        self.models["selection"] = DataModel(
            unit_cell=None, site=None, state=None
        )  # UUID's of the selected unit cell, site, and state

        self.models["unit_cell_data"] = DataModel(
            name="New Unit Cell",
            v1x=1.0,
            v1y=0.0,
            v1z=0.0,
            v2x=0.0,
            v2y=1.0,
            v2z=0.0,
            v3x=0.0,
            v3y=0.0,
            v3z=1.0,
            v1periodic=False,
            v2periodic=False,
            v3periodic=False,
        )  # Unit cell data of the selected unit cell

        self.models["site_data"] = DataModel(
            name="New Site", c1=0.0, c2=0.0, c3=0.0
        )  # Site data of the selected unit cell

        self.models["state_data"] = DataModel(
            name="New State"
        )  # State data of the selected unit cell

        self.models["bz"] = {
            "bz_vertices": [],
            "bz_faces": [],
        }  # Coordinates of BZ vertices and points bounding the BZ faces for the selected unit cell

        self.models["hopping_data"] = (
            DataModel()
        )  # A dictionary of hoppings for the selected unit cell.
        # The keys are Tuple[uuid, uuid] and the values are list[Tuple[int, int, int], np.complex128]

        self.models["state_info"] = (
            []
        )  # Tuples of (site_name, state_name, state_id) for the states in the selected unit cell

        self.models["pair_selection"] = [
            None,
            None,
        ]  # Selected pair of states in the hopping matrix.
        self.models["state_coupling"] = (
            []
        )  # List of couplings list[Tuple[int, int, int], np.complex128]
        # Set views
        self.views["uc"] = UnitCellView()

        self.views["hopping"] = HoppingView()

        # Set controllers
        self.controllers["app"] = AppController()

        self.controllers["uc"] = UnitCellController(
            self.models["unit_cells"],
            self.models["selection"],
            self.models["unit_cell_data"],
            self.models["site_data"],
            self.models["state_data"],
            self.views["uc"],
        )

        self.controllers["hopping"] = HoppingController(
            self.models["unit_cells"],
            self.models["selection"],
            self.models["hopping_data"],
            self.models["state_info"],
            self.models["pair_selection"],
            self.models["state_coupling"],
            self.views["hopping"],
        )

    def initialize(self):
        """Initialize all application components."""
        self._create_main_window()
        return self

    def _create_main_window(self):
        """Create the main application window."""
        self.main_window = MainWindow(
            self.views["uc"],
            self.views["hopping"],
            # self.views["unit_cell_plot"],
            # self.views["bz_plot"],
            # self.views["band_plot"],
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
