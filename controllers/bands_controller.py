from PySide6.QtCore import QObject, Signal
import uuid

from core.band_structure import (
    diagonalize_hamitonian,
    get_BZ_grid,
    interpolate_k_path,
)
from models import Selection, UnitCell
from views.panels import BandsPanel


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
        self.status_updated.emit("Computing the bands")

        eigenvalues, eigenvectors = diagonalize_hamitonian(
            hamiltonian_func, k_path
        )
        self.status_updated.emit("Bands computation complete")

        # Update the band structure
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

        eigenvalues, eigenvectors = diagonalize_hamitonian(
            hamiltonian_func, k_points
        )
        self.status_updated.emit("Grid computation complete")

        # Update the BZ grid
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
