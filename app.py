from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QApplication
import sys
import uuid

# View Panels
from views.bz_plot_view import BrillouinZonePlotView
from views.computation_view import ComputationView
from views.plot_view import PlotView
from views.uc_view import UnitCellView
from views.uc_plot_view import UnitCellPlotView

# Main UI View Components
from views.menu_bar_view import MenuBarView
from views.main_window import MainWindow
from views.main_toolbar_view import MainToolbarView
from views.status_bar_view import StatusBarView

# Controller Components
from controllers.app_controller import AppController
from controllers.bz_plot_controller import BrillouinZonePlotController
from controllers.computation_controller import ComputationController
from controllers.main_ui_controller import MainUIController
from controllers.plot_controller import PlotController
from controllers.uc_controller import UnitCellController
from controllers.uc_plot_controller import UnitCellPlotController

# Custom Dictionaries
from models.data_model import DataModel

# Constants
from resources.constants import selection_init

# Types
from src.tibitypes import UnitCell


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
        of unit cells and sites.
        - selection: a dictionary with UUID's of the selected
        unit cells/sites/states

        The view components are:
        - uc: used to construct unit cells/sites/states
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

        # Create an undo stack
        self.undo_stack = QUndoStack()
        self.undo_stack.setUndoLimit(100)

        # Initialize global models
        self.project_path = None
        self.unit_cells: dict[uuid.UUID, UnitCell] = {}
        self.selection = DataModel(selection_init())

        # Store the models in a dictionary
        self.models = {
            "project_path": self.project_path,
            "unit_cells": self.unit_cells,
            "selection": self.selection,
        }

        # Initialize views
        # Panel views
        self.uc_view = UnitCellView()
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
            self.uc_view,
            self.undo_stack,
        )

        self.uc_plot_controller = UnitCellPlotController(
            self.unit_cells,
            self.selection,
            self.uc_plot_view,
        )

        self.bz_plot_controller = BrillouinZonePlotController(
            self.unit_cells,
            self.selection,
            self.bz_plot_view,
            self.computation_view,
            self.undo_stack,
        )

        self.plot_controller = PlotController(self.plot_view)

        self.computation_controller = ComputationController(
            self.models, self.undo_stack, self.computation_view
        )

        self.main_ui_controller = MainUIController(
            self.models,
            self.main_window,
            self.menu_bar,
            self.toolbar,
            self.status_bar,
            self.undo_stack,
        )

        # Store controllers in a dictionary
        self.controllers = {
            "uc": self.uc_controller,
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

        # Connect the shutdown signal from the main window
        self.main_window.window_closed.connect(self._cleanup)

    def run(self):
        """
        Run the application.

        Shows the main window and starts the Qt event loop.

        Returns
        -------
        int
            Application exit code
        """
        self.main_window.show()
        return self.app.exec()

    def _cleanup(self):
        """
        Tasks performed when the app is shut down.

        - Disconnect the undo/redo stack signals
        """
        self.main_ui_controller.action_manager.disconnect_undo_redo()


def main():
    """
    Application entry point.

    Creates and runs the TiBi application.

    Returns
    -------
    int
        Application exit code
    """
    # Create and initialize the application
    app = TiBiApplication()

    # Run the application
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
