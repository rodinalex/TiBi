from PySide6.QtCore import QObject, Signal
import uuid

from core.band_structure import diagonalize_hamitonian, interpolate_k_path
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
    set_dimensionality(int)
        Set systen dimensionality to activate/deactivate ui components.
    set_combo(list[str])
        Populate the projection dropdown menu with state labels.
    get_projection_indices()
        Get the states selected for projection from the dropdown menu.

    Signals
    -------
    bands_computed
        Once the bands are computed, the signal is used to trigger plotting.
    projection_selection_changed
        Change in projection triggers band replotting
    status_updated
        Update the status bar information.
    """

    bands_computed = Signal()
    projection_selection_changed = Signal(object)
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
        self.bands_panel.proj_combo.selection_changed.connect(
            self.projection_selection_changed.emit
        )

    def _compute_bands(self):
        """
        Calculate the electronic band structure along a specified k-path.

        The path is defined by the special points in the Brillouin zone.
        """

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
        self.bands_computed.emit()

    def set_dimensionality(self, dim: int):
        """
        Set the system dimensionality.

        The panel components are activated/deactivated based on
        the dimensionality.
        """
        # BZ path selection buttons
        # Activate/deactivate buttons based on dimensionality
        self.bands_panel.add_gamma_btn.setEnabled(dim > 0)
        for btn in self.bands_panel.vertex_btns:
            btn.setEnabled(dim > 0)
        for btn in self.bands_panel.edge_btns:
            btn.setEnabled(dim > 1)
        for btn in self.bands_panel.face_btns:
            btn.setEnabled(dim > 2)

        # BZ grid spinboxes
        self.bands_panel.v1_points_spinbox.setEnabled(dim > 0)
        self.bands_panel.v2_points_spinbox.setEnabled(dim > 1)
        self.bands_panel.v3_points_spinbox.setEnabled(dim > 2)

    def set_combo(self, items: list[str]):
        """
        Update the states in the combo box.

        Once the items are updated, the selection buttons are activated
        if the number of items is not zero. Additionally, all the items
        are selected programatically.

        Parameters
        ----------
        items : list[str]
            List of items to set in the combo box.
        """
        self.bands_panel.proj_combo.refresh_combo(items)
        self.bands_panel.select_all_btn.setEnabled(len(items) > 0)
        self.bands_panel.clear_all_btn.setEnabled(len(items) > 0)
        self.bands_panel.proj_combo.select_all()

    def get_projection_indices(self):
        """
        Get the indices of the selected states from the projection menu.
        """
        return self.bands_panel.proj_combo.checked_items()
