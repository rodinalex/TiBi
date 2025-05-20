from PySide6.QtCore import QObject, Signal
import uuid

from src.band_structure import diagonalize_hamitonian, interpolate_k_path
from src.tibitypes import UnitCell
from views.computation_view import ComputationView


class ComputationController(QObject):
    """
    Controller responsible for physics calculations within the application.

    Attributes
    ----------
    models : dict
        Dictionary containing the system models
    computation_view : ComputationView
        UI object containing the computation view


    Signals
    -------
    status_updated
        Signal emitted to update the status of the computation
    band_computation_completed
        Signal notifying that the data can be plotted
    """

    status_updated = Signal(str)
    band_computation_completed = Signal()

    def __init__(self, models, computation_view: ComputationView):
        """
        Initialize the computation controller.

        Parameters
        ----------
        models : dict
            Dictionary containing the system models
        computation_view : ComputationView
            UI object containing the computation view
        """
        super().__init__()
        self.models = models
        self.computation_view = computation_view

        self.unit_cells: dict[uuid.UUID, UnitCell] = models["unit_cells"]
        # Connect the signals
        self.computation_view.bands_panel.compute_bands_btn.clicked.connect(
            self._compute_bands
        )

    def _compute_bands(self):
        """
        Calculate the electronic band structure along a specified k-path.

        The path is defined by the special points in the Brillouin zone.
        """

        # Get the selected unit cell
        uc_id = self.models["selection"]["unit_cell"]
        unit_cell = self.unit_cells[uc_id]

        # Check if the coupling is Hermitian and only then calculate
        if not unit_cell.is_hermitian():
            self.status_updated.emit(
                "Computation halted: the system is non-Hermitian"
            )
            return

        num_points = self.computation_view.bands_panel.n_points_spinbox.value()

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
        self.band_computation_completed.emit()
