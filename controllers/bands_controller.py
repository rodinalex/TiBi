from PySide6.QtCore import QObject, Signal
import uuid

from models import DataModel, UnitCell
from views.panels import BandsPanel
from core.band_structure import diagonalize_hamitonian, interpolate_k_path


class BandsController(QObject):
    """
    Controller for the hopping parameter interface.

    Attributes
    ----------
    unit_cells : dict[UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : DataModel
        Model tracking the current selection
    bands_panel : BandsPanel
        Main panel for bands and BZ grid calculations

    Methods
    -------


    Signals
    -------

    """

    bands_computed = Signal()
    status_updated = Signal(str)

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        bands_panel: BandsPanel,
    ):
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.bands_panel = bands_panel

        self.bands_panel.compute_bands_btn.clicked.connect(self._compute_bands)

    def _compute_bands(self):
        """
        Calculate the electronic band structure along a specified k-path.

        The path is defined by the special points in the Brillouin zone.
        """

        # Get the selected unit cell
        uc_id = self.selection.get("unit_cell")
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

        self.bands_panel.v1_points_spinbox.setEnabled(dim > 0)
        self.bands_panel.v2_points_spinbox.setEnabled(dim > 1)
        self.bands_panel.v3_points_spinbox.setEnabled(dim > 2)

    def set_combo(self, items: list[str]):
        """
        Set the items in the combo box.

        Parameters
        ----------
        items : list[str]
            List of items to set in the combo box.
        """
        self.bands_panel.proj_combo.refresh_combo(items)
        self.bands_panel.select_all_btn.setEnabled(len(items) > 0)
        self.bands_panel.clear_all_btn.setEnabled(len(items) > 0)
        self.bands_panel.proj_combo.select_all()
