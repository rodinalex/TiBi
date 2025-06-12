import numpy as np
from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal
import uuid

from TiBi.core.band_structure import (
    get_BZ_grid,
    interpolate_k_path,
)
from TiBi.models import Selection, UnitCell
from TiBi.views import ProgressDialog
from TiBi.views.panels import BandsPanel
from TiBi.logic.workers import DiagonalizationWorker


class BandsController(QObject):
    """
    Controller for the hopping parameter interface.

    Attributes
    ----------
    unit_cells : dict[UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : Selection
        Model tracking the currently selected unit cell, site, and state
    bands_panel : BandsPanel
        Main panel for bands and BZ grid calculations

    Methods
    -------
    update_bands_panel()
        Update the `BandsPanel`.
    set_combo()
        Populate the projection dropdown menu with state labels.
    get_projection_indices()
        Get the states selected for projection from the dropdown menu.

    Signals
    -------
    bands_plot_requested
        Request band plots update.
    dos_plot_requested
        Request dos plots update.
    status_updated
        Update the status bar information.
    """

    bands_plot_requested = Signal()
    dos_plot_requested = Signal()
    status_updated = Signal(str)

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: Selection,
        bands_panel: BandsPanel,
    ):
        """
        Initialize the BandsController.

        Parameters
        ----------
        unit_cells : dict[UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection : Selection
            Model tracking the currently selected unit cell, site, and state
        bands_panel : BandsPanel
            Main panel for bands and BZ grid calculations
        """
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.bands_panel = bands_panel
        # Conenct the signals
        self.bands_panel.compute_bands_btn.clicked.connect(self._compute_bands)
        self.bands_panel.compute_grid_btn.clicked.connect(self._compute_grid)
        self.bands_panel.proj_combo.selection_changed.connect(
            lambda _: (
                self.bands_plot_requested.emit()
                if (self.bands_panel.radio_group.checkedId() == 0)
                else self.dos_plot_requested.emit()
            )
        )
        self.bands_panel.select_all_btn.clicked.connect(
            self.bands_panel.proj_combo.select_all
        )
        self.bands_panel.clear_all_btn.clicked.connect(
            self.bands_panel.proj_combo.clear_selection
        )
        # Toggle whether to show bands or DOS:
        self.bands_panel.radio_group.buttonToggled.connect(
            lambda _, checked: (
                (
                    self.bands_plot_requested.emit()
                    if (self.bands_panel.radio_group.checkedId() == 0)
                    else self.dos_plot_requested.emit()
                )
                if checked
                else None
            )
        )
        # Toggle between Histogram and Lorentzian.
        # Only trigger if DOS is selected
        self.bands_panel.presentation_choice_group.buttonToggled.connect(
            lambda _, checked: (
                self.dos_plot_requested.emit()
                if (
                    checked and (self.bands_panel.radio_group.checkedId() == 1)
                )
                else None
            )
        )
        # Trigger plots when changing broadening or bin number
        self.bands_panel.broadening_spinbox.editingConfirmed.connect(
            lambda: (
                None
                if (self.bands_panel.radio_group.checkedId() == 0)
                else self.dos_plot_requested.emit()
            )
        )
        self.bands_panel.num_bins_spinbox.editingConfirmed.connect(
            lambda: (
                None
                if (self.bands_panel.radio_group.checkedId() == 0)
                else self.dos_plot_requested.emit()
            )
        )
        # Update the approximate output sizes
        self.bands_panel.n_points_spinbox.valueChanged.connect(
            self._set_approximate_band_output
        )
        self.bands_panel.v1_points_spinbox.valueChanged.connect(
            self._set_approximate_BZ_output
        )
        self.bands_panel.v2_points_spinbox.valueChanged.connect(
            self._set_approximate_BZ_output
        )
        self.bands_panel.v3_points_spinbox.valueChanged.connect(
            self._set_approximate_BZ_output
        )
        self.selection.selection_changed.connect(
            self._set_approximate_band_output
        )

        self.selection.selection_changed.connect(
            self._set_approximate_BZ_output
        )

    def _set_approximate_band_output(self, _=None):
        """
        Update the approximate output size label.
        """
        n_pts = self.bands_panel.n_points_spinbox.value()
        if self.selection.unit_cell:
            n_states = len(
                self.unit_cells[self.selection.unit_cell].get_states()[0]
            )
            # The multiplication by 10 is due to JSON overhead
            # (not being binary)
            res = n_pts * (16 * n_states**2 + 8 * n_states) * 10
        else:
            res = 0
        self.bands_panel.approximate_band_size.setText(
            f"Approximate output size: {res // 1000} kB"
        )

    def _set_approximate_BZ_output(self, _=None):
        """
        Update the approximate output size label.
        """

        n_pts = [
            y
            for y in [
                x.value() * x.isEnabled()
                for x in [
                    self.bands_panel.v1_points_spinbox,
                    self.bands_panel.v2_points_spinbox,
                    self.bands_panel.v3_points_spinbox,
                ]
            ]
            if y > 0
        ]
        if len(n_pts) == 0:
            n_pts = 0
        else:
            n_pts = np.prod(n_pts)
        if self.selection.unit_cell:
            n_states = len(
                self.unit_cells[self.selection.unit_cell].get_states()[0]
            )
            # The multiplication by 10 is due to JSON overhead
            # (not being binary)
            res = n_pts * (16 * n_states**2 + 8 * n_states) * 10
        else:
            res = 0
        self.bands_panel.approximate_BZ_grid_size.setText(
            f"Approximate output size: {res // 1000} kB"
        )

    def _compute_bands(self):
        """
        Calculate the electronic band structure along a specified k-path.

        The path is defined by the special points in the Brillouin zone.
        """
        # Set the radio toggle to the correct option
        for b in self.bands_panel.radio_group.buttons():
            b.blockSignals(True)

        self.bands_panel.bands_radio.setChecked(True)

        for b in self.bands_panel.radio_group.buttons():
            b.blockSignals(False)

        # Get the selected unit cell
        uc_id = self.selection.unit_cell
        unit_cell = self.unit_cells[uc_id]

        # Check if the coupling is Hermitian and only then calculate
        if not unit_cell.is_hermitian():
            self.status_updated.emit(
                "Computation halted: the system is non-Hermitian"
            )
            return

        num_points = self.bands_panel.n_points_spinbox.value()

        # Get Hamiltonian function
        hamiltonian_func = unit_cell.get_hamiltonian_function()

        # Perform calculation
        k_path = interpolate_k_path(
            unit_cell.bandstructure.special_points, num_points
        )

        # Perform calculation on a separate thread
        self.worker = DiagonalizationWorker(hamiltonian_func, k_path)
        self.thread = QThread()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.do_work)
        self.worker.task_finished.connect(self._handle_band_results)

        self.dialog = ProgressDialog()
        self.worker.progress_updated.connect(self.dialog.update_progress)
        self.worker.task_finished.connect(self.dialog.accept)
        self.worker.task_aborted.connect(self.dialog.reject)
        self.dialog.cancel_requested.connect(
            self.worker.request_abort, Qt.DirectConnection
        )

        # Cleanup
        self.worker.task_finished.connect(self.thread.quit)
        self.worker.task_aborted.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        # Only show the dialog after a delay if it's still running
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)

        def maybe_show_dialog():
            if self.thread.isRunning():
                self.dialog.show()

        self._show_timer.timeout.connect(maybe_show_dialog)
        self._show_timer.start(150)  # Delay in ms

        # Wait for the thread to finish and kill the timer if needed
        self.thread.finished.connect(self._show_timer.stop)

    def _handle_band_results(self, res):
        """
        Handle the results of the band structure calculation.

        Parameters
        ----------
        res : tuple[list[NDArray[np.float64]], \
            list[NDArray[np.float64]], list[NDArray[np.float64]]]
            Contains the eigenvalues, eigenvectors, and k-points
        """
        uc_id = self.selection.unit_cell
        unit_cell = self.unit_cells[uc_id]

        eigenvalues, eigenvectors, k_path = res
        unit_cell.bandstructure.eigenvalues = eigenvalues
        unit_cell.bandstructure.eigenvectors = eigenvectors
        unit_cell.bandstructure.path = k_path
        # Update combo to make sure all sites are selected
        self.update_combo()

    def _compute_grid(self):
        """
        Calculate the BZ grid using the settings from the panel.
        """
        # Set the radio toggle to the correct option
        for b in self.bands_panel.radio_group.buttons():
            b.blockSignals(True)

        self.bands_panel.dos_radio.setChecked(True)

        for b in self.bands_panel.radio_group.buttons():
            b.blockSignals(False)

        # Get the selected unit cell
        uc_id = self.selection.unit_cell
        unit_cell = self.unit_cells[uc_id]

        # Check if the coupling is Hermitian and only then calculate
        if not unit_cell.is_hermitian():
            self.status_updated.emit(
                "Computation halted: the system is non-Hermitian"
            )
            return

        k_points = get_BZ_grid(
            unit_cell=unit_cell,
            n1=self.bands_panel.v1_points_spinbox.value(),
            n2=self.bands_panel.v2_points_spinbox.value(),
            n3=self.bands_panel.v3_points_spinbox.value(),
            typ=self.bands_panel.grid_choice_group.checkedId(),
        )

        # Get Hamiltonian function
        hamiltonian_func = unit_cell.get_hamiltonian_function()

        self.status_updated.emit("Computing the grid")
        # Perform calculation on a separate thread
        self.worker = DiagonalizationWorker(hamiltonian_func, k_points)
        self.thread = QThread()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.do_work)
        self.worker.task_finished.connect(self._handle_grid_results)

        self.dialog = ProgressDialog()
        self.worker.progress_updated.connect(self.dialog.update_progress)
        self.worker.task_finished.connect(self.dialog.accept)
        self.worker.task_aborted.connect(self.dialog.reject)
        self.dialog.cancel_requested.connect(
            self.worker.request_abort, Qt.DirectConnection
        )

        # Cleanup
        self.worker.task_finished.connect(self.thread.quit)
        self.worker.task_aborted.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        # Only show the dialog after a delay if it's still running
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)

        def maybe_show_dialog():
            if self.thread.isRunning():
                self.dialog.show()

        self._show_timer.timeout.connect(maybe_show_dialog)
        self._show_timer.start(150)  # Delay in ms

        # Wait for the thread to finish and kill the timer if needed
        self.thread.finished.connect(self._show_timer.stop)

    def _handle_grid_results(self, res):
        """
        Handle the results of the BZ grid calculation.

        Parameters
        ----------
        res : tuple[list[NDArray[np.float64]], \
            list[NDArray[np.float64]], list[NDArray[np.float64]]]
            Contains the eigenvalues, eigenvectors, and k-points
        """
        uc_id = self.selection.unit_cell
        unit_cell = self.unit_cells[uc_id]

        eigenvalues, eigenvectors, k_points = res

        unit_cell.bz_grid.grid_divs = (
            self.bands_panel.v1_points_spinbox.value(),
            self.bands_panel.v2_points_spinbox.value(),
            self.bands_panel.v3_points_spinbox.value(),
        )
        unit_cell.bz_grid.eigenvalues = eigenvalues
        unit_cell.bz_grid.eigenvectors = eigenvectors
        unit_cell.bz_grid.k_points = k_points
        unit_cell.bz_grid.is_gamma_centered = bool(
            self.bands_panel.grid_choice_group.checkedId()
        )
        # Update combo to make sure all sites are selected
        self.update_combo()

    def update_bands_panel(self):
        """
        Update the `BandsPanel`.

        The UI components are activated/deactivated based on
        the system parameters.
        Projection menu is also updated programmatically.
        Selection is set to "bands"
        """
        # Set the radio toggle to bands
        for b in self.bands_panel.radio_group.buttons():
            b.blockSignals(True)

        self.bands_panel.bands_radio.setChecked(True)

        for b in self.bands_panel.radio_group.buttons():
            b.blockSignals(False)
        uc_id = self.selection.unit_cell
        if uc_id is None:
            dim = 0
        else:
            unit_cell = self.unit_cells[uc_id]
            # Get the system dimensionality
            dim = (
                unit_cell.v1.is_periodic
                + unit_cell.v2.is_periodic
                + unit_cell.v3.is_periodic
            )
            # Fill out the fields
            bandstructure = unit_cell.bandstructure
            bz_grid = unit_cell.bz_grid

            if bandstructure.path:
                self.bands_panel.n_points_spinbox.setValue(
                    len(bandstructure.path)
                )
            else:
                self.bands_panel.n_points_spinbox.setValue(100)
            # Set the type of the grid
            self.bands_panel.grid_choice_group.button(
                bz_grid.is_gamma_centered
            ).setChecked(True)
            self.bands_panel.v1_points_spinbox.setValue(bz_grid.grid_divs[0])
            self.bands_panel.v2_points_spinbox.setValue(bz_grid.grid_divs[1])
            self.bands_panel.v3_points_spinbox.setValue(bz_grid.grid_divs[2])

        # BZ path selection buttons
        # Activate/deactivate buttons based on dimensionality
        self.bands_panel.add_gamma_btn.setEnabled(dim > 0)
        for btn in self.bands_panel.vertex_btns:
            btn.setEnabled(dim > 0)
        for btn in self.bands_panel.edge_btns:
            btn.setEnabled(dim > 1)
        for btn in self.bands_panel.face_btns:
            btn.setEnabled(dim > 2)

        # Computation and BZ path buttons
        if uc_id is None:
            self.bands_panel.remove_last_btn.setEnabled(False)
            self.bands_panel.clear_path_btn.setEnabled(False)
            self.bands_panel.compute_bands_btn.setEnabled(False)

        else:
            self.bands_panel.remove_last_btn.setEnabled(
                len(unit_cell.bandstructure.special_points) > 0
            )
            self.bands_panel.clear_path_btn.setEnabled(
                len(unit_cell.bandstructure.special_points) > 0
            )
            self.bands_panel.compute_bands_btn.setEnabled(
                len(unit_cell.bandstructure.special_points) > 1
            )

        # BZ grid spinboxes
        self.bands_panel.v1_points_spinbox.setEnabled(dim > 0)
        self.bands_panel.v2_points_spinbox.setEnabled(dim > 1)
        self.bands_panel.v3_points_spinbox.setEnabled(dim > 2)

        # BZ grid spinboxes and button
        self.bands_panel.v1_points_spinbox.setEnabled(dim > 0)
        self.bands_panel.v2_points_spinbox.setEnabled(dim > 1)
        self.bands_panel.v3_points_spinbox.setEnabled(dim > 2)
        self.bands_panel.compute_grid_btn.setEnabled(dim > 0)

        # Update the projection combo
        self.update_combo()

        # Update the approximate output size labels
        self._set_approximate_band_output()
        self._set_approximate_BZ_output()

    def update_combo(self):
        """
        Update the states in the combo box.

        Once the items are updated, the selection buttons are activated
        if the number of items is not zero. Additionally, all the items
        are selected programatically.
        """
        uc_id = self.selection.unit_cell
        if uc_id is None:
            items = []
        else:
            unit_cell = self.unit_cells[uc_id]
            _, state_info = unit_cell.get_states()
            items = [f"{s[0]}.{s[2]}" for s in state_info]
        self.bands_panel.proj_combo.refresh_combo(items)
        self.bands_panel.select_all_btn.setEnabled(len(items) > 0)
        self.bands_panel.clear_all_btn.setEnabled(len(items) > 0)
        self.bands_panel.proj_combo.select_all()

    def get_projection_indices(self):
        """
        Get the indices of the selected states from the projection menu.

        Returns
        -------
        list[int]
            Indices of the selected states
        """
        return self.bands_panel.proj_combo.checked_items()

    def get_dos_properties(self):
        """
        Get the DOS properties for the plots.

        Returns
        -------
        tuple[int, int, np.float64]
            Number of bins/points to be used in the plot, the plot type
            (0 for a histogram, 1 for Lorentzian), and Lorentzian broadening
        """
        num_bins = self.bands_panel.num_bins_spinbox.value()
        plot_type = self.bands_panel.presentation_choice_group.checkedId()
        broadening = self.bands_panel.broadening_spinbox.value()
        return (num_bins, plot_type, broadening)
