from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QSizePolicy,
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
    bz_plot : BrillouinZonePlotView
        Brillouin zone 3D visualization view
    plot : PlotView
        2D plot view
    computation : ComputationView
        Multi-tab view used to set up calculations
    window_closed : Signal
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
        super().__init__()
        self.setWindowTitle("TiBi")
        # self.setMinimumSize(1100, 825)

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
        unit_cell_widget.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Expanding
        )
        unit_cell_layout.addWidget(self._frame_widget(self.uc))

        # Computation controls and BZ
        computation_layout = QVBoxLayout()
        computation_layout.setContentsMargins(0, 0, 0, 0)

        computation_widget = QWidget()
        computation_widget.setLayout(computation_layout)
        computation_widget.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Expanding
        )

        # Set fixed height for computation_view
        computation_splitter = QSplitter(Qt.Vertical)
        inner_height = max(
            self.computation_view.bands_panel.sizeHint().height(),
            self.computation_view.hopping_panel.sizeHint().height(),
        )
        margin_buffer = 20  # adjust if needed
        max_height = inner_height + margin_buffer

        computation_view_framed = self._frame_widget(self.computation_view)
        computation_view_framed.setMaximumHeight(max_height)
        computation_view_framed.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred
        )

        computation_splitter.addWidget(self._frame_widget(self.bz_plot))
        computation_splitter.addWidget(computation_view_framed)

        # Disable expansion of computation_view
        computation_splitter.setStretchFactor(0, 1)
        computation_splitter.setStretchFactor(1, 0)

        computation_splitter.setCollapsible(0, False)
        computation_splitter.setCollapsible(1, False)

        # Prevent computation_view from growing too large
        computation_layout.addWidget(computation_splitter)

        # UC 3D plot and results plots
        plots_splitter = QSplitter(Qt.Vertical)
        plots_splitter.addWidget(
            self._frame_widget(self.uc_plot)
        )  # Top 3D plot
        plots_splitter.addWidget(
            self._frame_widget(self.plot)
        )  # Bottom 2D plot

        # Set initial size ratio
        plots_splitter.setSizes([1, 1])
        # Prevent the panels from collapsing
        plots_splitter.setCollapsible(0, False)
        plots_splitter.setCollapsible(1, False)

        main_layout.addWidget(unit_cell_widget)
        main_layout.addWidget(computation_widget)
        main_layout.addWidget(plots_splitter)
        # Set as central widget
        self.setCentralWidget(main_view)

    def closeEvent(self, event):
        # Override the parent class closeEvent to emit a signal on closing.
        self.window_closed.emit()
        super().closeEvent(event)

    def _frame_widget(self, widget: QWidget) -> QFrame:
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
