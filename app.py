import sys
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from views.placeholder import PlaceholderWidget
from views.bands_plot_view import BandStructurePlotView
from views.bz_plot_view import BrillouinZonePlotView
from views.hopping_view import HoppingView
from views.uc_view import UnitCellView
from views.uc_plot_view import UnitCellPlotView
from views.menu_bar_view import MenuBarView
from views.main_toolbar_view import MainToolbarView
from views.status_bar_view import StatusBarView

from controllers.app_controller import AppController
from controllers.bands_plot_controller import BandStructurePlotController
from controllers.bz_plot_controller import BrillouinZonePlotController
from controllers.hopping_controller import HoppingController
from controllers.uc_controller import UnitCellController
from controllers.uc_plot_controller import UnitCellPlotController
from controllers.computation_controller import ComputationController
from controllers.main_ui_controller import MainUIController

from models.data_models import DataModel, AlwaysNotifyDataModel


class MainWindow(QMainWindow):
    """
    Main application window that defines the UI layout.

    This class is purely a view component that arranges the UI elements and
    doesn't contain business logic or model manipulation. It creates a three-column
    layout for organizing the different components of the application, along with
    menu bar, toolbar, and status bar.

    Following the MVC pattern, this class is restricted to presentation concerns only.
    """

    def __init__(
        self, uc, hopping, uc_plot, bz_plot, band_plot, menu_bar, toolbar, status_bar
    ):
        """
        Initialize the main window with views for different components.

        Args:
            uc: Unit cell editor view
            hopping: Hopping parameter editor view
            uc_plot: Unit cell 3D visualization view
            bz_plot: Brillouin zone 3D visualization view
            band_plot: Band structure plot view
            menu_bar: Menu bar view
            toolbar: Main toolbar view
            status_bar: Status bar view
        """
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1600, 950))

        # Store references to UI components
        self.uc = uc
        self.hopping = hopping
        self.uc_plot = uc_plot
        self.bz_plot = bz_plot
        self.band_plot = band_plot

        # Set menu bar
        self.setMenuBar(menu_bar)

        # Add toolbar
        self.addToolBar(toolbar)

        # Set status bar
        self.setStatusBar(status_bar)

        # Main Layout
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)

        # Create four column layouts
        column1_layout = QVBoxLayout()
        column2_layout = QVBoxLayout()
        column3_layout = QVBoxLayout()
        column4_layout = QVBoxLayout()

        column1_layout.addWidget(self.frame_widget(self.uc), stretch=3)

        column2_layout.addWidget(self.frame_widget(self.hopping), stretch=5)
        column2_layout.addWidget(self.frame_widget(self.bz_plot), stretch=2)

        column3_layout.addWidget(self.frame_widget(self.uc_plot), stretch=1)
        column3_layout.addWidget(self.frame_widget(self.band_plot), stretch=1)

        column4_layout.addWidget(
            self.frame_widget(PlaceholderWidget("SPOT")), stretch=3
        )

        main_layout.addLayout(column1_layout, stretch=1)
        main_layout.addLayout(column2_layout, stretch=2)
        main_layout.addLayout(column3_layout, stretch=3)
        main_layout.addLayout(column4_layout, stretch=2)

        # Set as central widget
        self.setCentralWidget(main_view)

    def frame_widget(self, widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(1)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(widget)
        frame.setLayout(layout)
        return frame


class TiBiApplication:
    """
    Main application class that initializes and connects all components.

    This class serves as the application composition root, responsible for:
    1. Creating data models
    2. Creating views
    3. Creating controllers
    4. Wiring everything together
    5. Starting the application

    The application follows a strict MVC architecture with reactive data binding:
    - Models store application state and emit signals when they change
    - Views display data and capture user input without direct knowledge of models
    - Controllers connect models and views, handling user actions and model updates
    """

    def __init__(self):
        """
        Initialize the application by creating and connecting all components.

        Sets up all models, views, and controllers, and establishes the connections
        between them according to the MVC pattern. Each component is stored in a
        dictionary for easy access.
        """
        # Create the Qt application
        self.app = QApplication(sys.argv)

        # References to components
        self.models = {}
        self.views = {}
        self.controllers = {}
        self.main_window = None

        # Initialize models
        self._init_models()

        # Initialize views
        self._init_views()

        # Initialize the main window
        self.main_window = MainWindow(
            self.views["uc"],
            self.views["hopping"],
            self.views["uc_plot"],
            self.views["bz_plot"],
            self.views["band_plot"],
            self.views["menu_bar"],
            self.views["toolbar"],
            self.views["status_bar"],
        )

        # Initialize controllers
        self._init_controllers()

        # Initialize the top-level application controller
        self.app_controller = AppController(self.models, self.controllers)

        # Set initial status message
        self.controllers["main_ui"].update_status("Application started")

    def _init_models(self):
        """
        Initialize all data models used in the application.

        Creates reactive data models for different aspects of the application state,
        including unit cells, selection state, form data, and calculation results.
        """
        # Dictionary mapping UUIDs to UnitCell objects
        self.models["unit_cells"] = {}

        # Current selection state (tracks which items are selected in the UI)
        self.models["selection"] = DataModel(unit_cell=None, site=None, state=None)

        # Form data for the currently selected unit cell
        self.models["unit_cell_data"] = DataModel(
            name="",
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
        )

        # Form data for the currently selected site
        self.models["site_data"] = DataModel(name="", c1=0.0, c2=0.0, c3=0.0)

        # Form data for the currently selected state
        self.models["state_data"] = DataModel(name="")

        # Band structure calculation results
        # Uses AlwaysNotifyDataModel to ensure UI updates on every change
        self.models["band_structure"] = AlwaysNotifyDataModel(
            k_path=None, bands=None, special_points=None
        )

    def _init_views(self):
        """
        Initialize all views used in the application.

        Creates the UI components for different parts of the application,
        including editors, 3D visualizations, plots, and main UI elements.
        """
        # Core visualizations and editors
        self.views["uc"] = UnitCellView()
        self.views["hopping"] = HoppingView()
        self.views["uc_plot"] = UnitCellPlotView()
        self.views["bz_plot"] = BrillouinZonePlotView()
        self.views["band_plot"] = BandStructurePlotView()

        # Main UI components
        self.views["menu_bar"] = MenuBarView()
        self.views["toolbar"] = MainToolbarView()
        self.views["status_bar"] = StatusBarView()

    def _init_controllers(self):
        """
        Initialize all controllers used in the application.

        Creates controllers that connect models and views, handling the application
        logic. Each controller is responsible for a specific aspect of functionality.
        """
        # Unit Cell Editor Controller
        self.controllers["uc"] = UnitCellController(
            self.models["unit_cells"],
            self.models["selection"],
            self.models["unit_cell_data"],
            self.models["site_data"],
            self.models["state_data"],
            self.views["uc"],
        )

        # Hopping Parameter Editor Controller
        self.controllers["hopping"] = HoppingController(
            self.models["unit_cells"],
            self.models["selection"],
            self.views["hopping"],
        )

        # Unit Cell 3D Visualization Controller
        self.controllers["uc_plot"] = UnitCellPlotController(
            self.models["unit_cells"],
            self.models["selection"],
            self.views["uc_plot"],
        )

        # Brillouin Zone Visualization Controller
        self.controllers["bz_plot"] = BrillouinZonePlotController(
            self.models["unit_cells"],
            self.models["selection"],
            self.views["bz_plot"],
        )

        # Band Structure Plot Controller
        self.controllers["band_plot"] = BandStructurePlotController(
            self.models["band_structure"], self.views["band_plot"]
        )

        # Physics Computation Controller
        self.controllers["computation"] = ComputationController(
            self.models["band_structure"]
        )

        # Main UI Controller (menu bar, toolbar, status bar)
        self.controllers["main_ui"] = MainUIController(
            self.models,
            self.main_window,
            self.views["menu_bar"],
            self.views["toolbar"],
            self.views["status_bar"],
        )

    def run(self):
        """
        Run the application.

        Shows the main window and starts the Qt event loop.

        Returns:
            int: Application exit code
        """
        self.main_window.show()
        return self.app.exec()


def main():
    """
    Application entry point.

    Creates and runs the TiBi application.

    Returns:
        int: Application exit code
    """
    # Create and initialize the application
    app = TiBiApplication()

    # Run the application
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
