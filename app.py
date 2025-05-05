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

# View Panels
from views.bz_plot_view import BrillouinZonePlotView
from views.computation_view import ComputationView
from views.hopping_view import HoppingView
from views.plot_view import PlotView
from views.uc_view import UnitCellView
from views.uc_plot_view import UnitCellPlotView

# Main UI View Components
from views.menu_bar_view import MenuBarView
from views.main_toolbar_view import MainToolbarView
from views.status_bar_view import StatusBarView

# Temporary placeholder
from views.placeholder import PlaceholderWidget

# Controller Components
from controllers.app_controller import AppController
from controllers.bz_plot_controller import BrillouinZonePlotController
from controllers.computation_controller import ComputationController
from controllers.hopping_controller import HoppingController
from controllers.main_ui_controller import MainUIController
from controllers.plot_controller import PlotController
from controllers.uc_controller import UnitCellController
from controllers.uc_plot_controller import UnitCellPlotController

# Custom Dictionaries
from models.data_models import DataModel, AlwaysNotifyDataModel

# Constants
from resources.constants import (
    unit_cell_data_init,
    selection_init,
    active_band_structure_init,
)


class MainWindow(QMainWindow):
    """
    Main application window that defines the UI layout.

    This class is purely a view component that arranges the UI elements and
    doesn't contain business logic or model manipulation. It creates a
    four-column layout for organizing the different components of the
    application, along with menu bar, toolbar, and status bar.

    Following the MVC pattern, this class is restricted to presentation
    concerns only.
    """

    def __init__(
        self,
        uc: UnitCellView,
        hopping: HoppingView,
        uc_plot: UnitCellPlotView,
        bz_plot: BrillouinZonePlotView,
        plot: PlotView,
        computation_view: ComputationView,
        menu_bar: MenuBarView,
        toolbar: MainToolbarView,
        status_bar: StatusBarView,
    ):
        """
        Initialize the main window with views for different components.

        Args:
            uc: Unit cell editor view
            hopping: Hopping parameter editor view
            uc_plot: Unit cell 3D visualization view
            bz_plot: Brillouin zone 3D visualization view
            plot: 2D plot view
            computation: Multi-tab view used to set up calculations
            menu_bar: Menu bar view
            toolbar: Main toolbar view
            status_bar: Status bar view
        """
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1400, 825))

        # Store references to UI components
        self.uc = uc
        self.hopping = hopping
        self.uc_plot = uc_plot
        self.bz_plot = bz_plot
        self.plot = plot
        self.computation_view = computation_view
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
        column1_layout = QVBoxLayout()  # Unit cell creation
        column2_layout = QVBoxLayout()  # Hopping creation
        column3_layout = QVBoxLayout()  # UC 3D plot and 2D plots
        column4_layout = QVBoxLayout()  # BZ 3D plot and computation

        column1_layout.addWidget(self.frame_widget(self.uc), stretch=3)

        column2_layout.addWidget(self.frame_widget(self.hopping), stretch=5)
        column2_layout.addWidget(
            self.frame_widget(PlaceholderWidget("[SPOT]")), stretch=1
        )

        column3_layout.addWidget(self.frame_widget(self.uc_plot), stretch=1)
        column3_layout.addWidget(self.frame_widget(self.plot), stretch=1)

        column4_layout.addWidget(self.frame_widget(self.bz_plot), stretch=6)
        column4_layout.addWidget(
            self.frame_widget(self.computation_view), stretch=10
        )
        column4_layout.addWidget(
            self.frame_widget(PlaceholderWidget("[PROGRESS]")), stretch=1
        )

        main_layout.addLayout(column1_layout, stretch=1)
        main_layout.addLayout(column2_layout, stretch=6)
        main_layout.addLayout(column3_layout, stretch=9)
        main_layout.addLayout(column4_layout, stretch=4)

        # Set as central widget
        self.setCentralWidget(main_view)

    def frame_widget(self, widget: QWidget) -> QFrame:
        """
        Enclose a widget in a frame. Used to make the layout look more
        structured.
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(1)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(widget, stretch=1)
        frame.setLayout(layout)
        return frame


class TiBiApplication:
    """
    Main application class that initializes and connects all components.

    This class serves as the application composition root, responsible for:
    1. Creating global data models
    2. Creating views
    3. Creating controllers
    4. Wiring everything together
    5. Starting the application

    The application follows the MVC architecture with reactive data binding:
    - Models store application state and emit signals when they change
    - Views display data and capture user input without knowledge of models
    - Controllers link models and views, handling user actions and
    model updates
    """

    def __init__(self):
        """
        Initialize the application by creating and connecting all components.

        Sets up global models, views, and controllers, and establishes the
        connections between them according to the MVC pattern. Each component
        is also stored in a dictionary for easy access.

        The global models are:
        - project_path: the file to which the dictionary containing the unit
        cell objects is saved
        - unit_cells: a UUID to UnitCell dictionary
        - unit_cell_data: a dictionary with data used in the creation/editing
        of unit cells and sites.
        - selection: a dictionary with UUID's of the selected
        unit cells/sites/states
        - bz_path: a list of arrays of length D, where D is the system
        dimensionality, defining a path throught the Brillouing zone
        Used for band computation. Shared by the bz_plot_controller
        and computation_controller.
        - active_band_structure: a dictionary containing the band
        structure data of the currently-selected unit cell.
        - band_structures: A dictionary of the band structures that
        have been obtained in the current sessions for the unit cells.
        The keys are unit cells UUID's and the values are
        BandStructure objects. Storing the band structures allows
        the user to quickly switch between different unit cells to
        compare their band structures.

        The view components are:
        - uc: used to construct unit cells/sites/states
        - hopping: used to add hoppings between states in the unit cell
        - uc_plot: shows a 3D plot of the unit cell and its sites
        - bz_plot: shows the Brillouin zone of the unit cell
        - plot: shows 2D plots (e.g., band structures, density of states)
        - computation: a multi-tab view used to set up calculations
        - menu_bar: standard menu bar
        - toolbar: toolbar at the top of the window
        - status_bar: status bar at the bottom of the window

        The views are passed as arguments to the MainWindow widget

        Each view has its corresponding controller, with the main UI
        views directed by a single main_ui_controller.

        app_controller has access to all the models and controllers
        and is used to direct cross-controller communication
        """
        # Create the Qt application
        self.app = QApplication(sys.argv)

        # Initialize global models
        self.project_path = None
        self.unit_cells = {}
        self.unit_cell_data = DataModel(unit_cell_data_init)
        self.selection = DataModel(selection_init)
        self.bz_path = []
        self.active_band_structure = AlwaysNotifyDataModel(
            active_band_structure_init
        )
        self.band_structures = AlwaysNotifyDataModel()

        # Store the models in a dictionary
        self.models = {
            "project_path": self.project_path,
            "unit_cells": self.unit_cells,
            "unit_cell_data": self.unit_cell_data,
            "selection": self.selection,
            "bz_path": self.bz_path,
            "active_band_structure": self.active_band_structure,
            "band_structures": self.band_structures,
        }

        # Initialize views
        # Panel views
        self.uc_view = UnitCellView()
        self.hopping_view = HoppingView()
        self.uc_plot_view = UnitCellPlotView()
        self.bz_plot_view = BrillouinZonePlotView()
        self.plot_view = PlotView()
        self.computation_view = ComputationView()
        # Main UI Views
        self.menu_bar = MenuBarView()
        self.toolbar = MainToolbarView()
        self.status_bar = StatusBarView()

        # Store the views in a dictionary
        self.views = {
            "uc": self.uc_view,
            "hopping": self.hopping_view,
            "uc_plot": self.uc_plot_view,
            "bz_plot": self.bz_plot_view,
            "plot": self.plot_view,
            "computation": self.computation_view,
            "menu_bar": self.menu_bar,
            "toolbar": self.toolbar,
            "status_bar": self.status_bar,
        }

        # Initialize the main window
        self.main_window = MainWindow(
            self.uc_view,
            self.hopping_view,
            self.uc_plot_view,
            self.bz_plot_view,
            self.plot_view,
            self.computation_view,
            self.menu_bar,
            self.toolbar,
            self.status_bar,
        )

        # Initialize contollers
        self.uc_controller = UnitCellController(
            self.unit_cells,
            self.selection,
            self.unit_cell_data,
            self.uc_view,
        )

        self.hopping_controller = HoppingController(
            self.unit_cells,
            self.selection,
            self.hopping_view,
        )

        self.uc_plot_controller = UnitCellPlotController(
            self.unit_cells,
            self.selection,
            self.uc_plot_view,
        )

        self.bz_plot_controller = BrillouinZonePlotController(
            self.unit_cells,
            self.selection,
            self.bz_path,
            self.bz_plot_view,
            self.computation_view,
        )

        self.plot_controller = PlotController(
            self.active_band_structure, self.plot_view
        )

        self.computation_controller = ComputationController(
            self.models, self.computation_view
        )

        self.main_ui_controller = MainUIController(
            self.models,
            self.main_window,
            self.menu_bar,
            self.toolbar,
            self.status_bar,
        )

        self.controllers = {
            "uc": self.uc_controller,
            "hopping": self.hopping_controller,
            "uc_plot": self.uc_plot_controller,
            "bz_plot": self.bz_plot_controller,
            "plot": self.plot_controller,
            "computation": self.computation_controller,
            "main_ui": self.main_ui_controller,
        }

        # Initialize the top-level application controller
        self.app_controller = AppController(self.models, self.controllers)

        # Set initial status message
        self.main_ui_controller.update_status("Application started")

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
