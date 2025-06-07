from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# View Panels
from TiBi.views.bz_plot_view import BrillouinZonePlotView
from TiBi.views.computation_view import ComputationView
from TiBi.views.plot_view import PlotView
from TiBi.views.uc_view import UnitCellView
from TiBi.views.uc_plot_view import UnitCellPlotView

# Main UI View Components
from TiBi.views.menu_bar_view import MenuBarView
from TiBi.views.main_toolbar_view import MainToolbarView
from TiBi.views.status_bar_view import StatusBarView


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
        self.resize(1100, 825)  # Initial size
        self.setMinimumSize(1100, 825)

        # Store references to UI components
        self.uc = uc
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

        # Create three column Layouts and wrap them into Widgets
        # UnitCell geometry and Sites
        unit_cell_layout = QVBoxLayout()
        unit_cell_layout.setContentsMargins(0, 0, 0, 0)
        unit_cell_widget = QWidget()
        unit_cell_widget.setLayout(unit_cell_layout)
        unit_cell_widget.setFixedWidth(200)

        # Computation controls and BZ
        computation_layout = QVBoxLayout()
        computation_layout.setContentsMargins(0, 0, 0, 0)
        computation_layout.setSpacing(7)

        computation_widget = QWidget()
        computation_widget.setLayout(computation_layout)
        computation_widget.setFixedWidth(320)
        # UC 3D plot and results plots
        plots_splitter = QSplitter(Qt.Vertical)
        plots_splitter.addWidget(
            self.frame_widget(self.uc_plot)
        )  # Top 3D plot
        plots_splitter.addWidget(
            self.frame_widget(self.plot)
        )  # Bottom 2D plot

        # Set initial size ratio
        plots_splitter.setSizes([1, 1])
        # Prevent the panels from collapsing
        plots_splitter.setCollapsible(0, False)
        plots_splitter.setCollapsible(1, False)

        unit_cell_layout.addWidget(self.frame_widget(self.uc), stretch=3)

        computation_layout.addWidget(
            self.frame_widget(self.bz_plot), stretch=1
        )
        computation_layout.addWidget(
            self.frame_widget(self.computation_view), stretch=3
        )

        main_layout.addWidget(unit_cell_widget)
        main_layout.addWidget(computation_widget, stretch=2)
        main_layout.addWidget(plots_splitter, 3)
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
