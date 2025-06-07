from pathlib import Path
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QApplication
from string import Template
import sys
import uuid

# View Components
from TiBi.views import (
    BrillouinZonePlotView,
    ComputationView,
    MenuBarView,
    MainWindow,
    MainToolbarView,
    PlotView,
    StatusBarView,
    UnitCellPlotView,
    UnitCellView,
)

# Controller Components
from TiBi.controllers import (
    AppController,
    BrillouinZonePlotController,
    ComputationController,
    MainUIController,
    PlotController,
    UnitCellController,
    UnitCellPlotController,
)

# Models and factories
from TiBi.models import Selection, UnitCell
from TiBi.ui.styles import THEME_SETTINGS


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return Path(sys._MEIPASS) / "TiBi" / relative_path
    else:
        # Development environment
        return Path(__file__).parent / relative_path


class TiBiApplication:
    """
    Main application class that initializes and connects all components.
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
        self.app.setStyle("Fusion")

        # Load and apply the global stylesheet
        qss_path = get_resource_path("ui/styles/main_theme.qss")
        if qss_path.exists():
            with qss_path.open("r") as f:
                qss_template = Template(f.read())
            styled_qss = qss_template.substitute(THEME_SETTINGS)
            self.app.setStyleSheet(styled_qss)
        else:
            print(f"Warning: QSS file not found at {qss_path}")
        # Create an undo stack
        self.undo_stack = QUndoStack()
        self.undo_stack.setUndoLimit(100)

        # Initialize global models
        self.project_path = None
        self.unit_cells: dict[uuid.UUID, UnitCell] = {}
        self.selection = Selection()
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

        self.plot_controller = PlotController(
            self.unit_cells, self.selection, self.plot_view
        )

        self.computation_controller = ComputationController(
            self.unit_cells,
            self.selection,
            self.computation_view,
            self.undo_stack,
        )

        self.main_ui_controller = MainUIController(
            self.project_path,
            self.unit_cells,
            self.selection,
            self.main_window,
            self.menu_bar,
            self.toolbar,
            self.status_bar,
            self.undo_stack,
        )

        # Initialize the top-level application controller
        self.app_controller = AppController(
            self.unit_cells,
            self.selection,
            self.bz_plot_controller,
            self.computation_controller,
            self.main_ui_controller,
            self.plot_controller,
            self.uc_controller,
            self.uc_plot_controller,
        )

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
