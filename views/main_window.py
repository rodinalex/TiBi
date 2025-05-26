from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

# View Panels
from views.bz_plot_view import BrillouinZonePlotView
from views.computation_view import ComputationView
from views.plot_view import PlotView
from views.uc_view import UnitCellView
from views.uc_plot_view import UnitCellPlotView

# Main UI View Components
from views.menu_bar_view import MenuBarView
from views.main_toolbar_view import MainToolbarView
from views.status_bar_view import StatusBarView


class MainWindow(QMainWindow):
    """
    Main application window that defines the UI layout.

    This class is purely a view component that arranges the UI elements and
    doesn't contain business logic or model manipulation. It creates a
    four-column layout for organizing the different components of the
    application, along with menu bar, toolbar, and status bar.

    Attributes
    ----------
    uc : UnitCellView
        Unit cell editor view
    uc_plot : UnitCellPlotView
        Unit cell 3D visualization view
    bz_plot : BrillouinonePlotView)
        Brillouin zone 3D visualization view
    plot : PlotView
        2D plot view
    computation : ComputationView
        Multi-tab view used to set up calculations

    Signals
    -------
    window_closed
        Signals the main app to run the cleanup procedure
    """

    window_closed = Signal()

    def __init__(
        self,
        uc: UnitCellView,
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

        Parameters
        ----------
        uc : UnitCellView
            Unit cell editor view
        uc_plot : UnitCellPlotView
            Unit cell 3D visualization view
        bz_plot : BrillouinonePlotView)
            Brillouin zone 3D visualization view
        plot : PlotView
            2D plot view
        computation : ComputationView
            Multi-tab view used to set up calculations
        menu_bar : MenuBarView
            Menu bar view
        toolbar : MainToolbarView
            Main toolbar view
        status_bar : StatusBarView)
            Status bar view
        """
        super().__init__()
        self.setWindowTitle("TiBi")
        self.setFixedSize(QSize(1100, 825))

        # Store references to UI components
        self.uc = uc
        # self.hopping = hopping
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

        # Create three column layouts
        unit_cell_layout = QVBoxLayout()  # UnitCell geometry and Sites
        computation_layout = QVBoxLayout()  # Computation controls
        plots_layout = QVBoxLayout()  # UC 3D plot and 2D plots

        unit_cell_layout.addWidget(self.frame_widget(self.uc), stretch=3)

        computation_layout.addWidget(
            self.frame_widget(self.bz_plot), stretch=1
        )
        computation_layout.addWidget(
            self.frame_widget(self.computation_view), stretch=3
        )
        plots_layout.addWidget(self.frame_widget(self.uc_plot), stretch=1)
        plots_layout.addWidget(self.frame_widget(self.plot), stretch=1)

        main_layout.addLayout(unit_cell_layout, stretch=1)
        main_layout.addLayout(computation_layout, stretch=2)
        main_layout.addLayout(plots_layout, stretch=3)

        # Set as central widget
        self.setCentralWidget(main_view)

    def closeEvent(self, event):
        """Override the parent class closeEvent to emit a signal on closing."""
        self.window_closed.emit()
        super().closeEvent(event)

    def frame_widget(self, widget: QWidget) -> QFrame:
        """
        Enclose a widget in a frame.

        Used to make the layout look more structured.
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(1)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(widget, stretch=1)
        frame.setLayout(layout)
        return frame
