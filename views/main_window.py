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
    hopping : HoppingView)
        Hopping parameter editor view
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

        Parameters
        ----------
        uc : UnitCellView
            Unit cell editor view
        hopping : HoppingView)
            Hopping parameter editor view
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
