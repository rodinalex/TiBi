from PySide6.QtCore import QObject, Signal
from src.band_structure import band_compute, interpolate_k_path
from views.computation_view import ComputationView
from src.tibitypes import BandStructure
import numpy as np
import copy


class ComputationController(QObject):
    """
    Controller responsible for physics calculations within the application.

    This controller handles the computational aspects of the application, such as
    band structure calculations, and updates the corresponding data models with the results.
    It isolates the calculation logic from both the UI and the data storage, following
    the MVC pattern.
    """

    status_updated = Signal(str)

    def __init__(self, models, computation_view: ComputationView):
        """
        Initialize the computation controller.

        Args:
            models: System models. All are provided for computational convenience
            band_structure: Data model that will store calculation results
        """
        super().__init__()
        self.models = models
        self.computation_view = computation_view

        # Connect the signales
        self.computation_view.bands_panel.compute_bands_btn.clicked.connect(
            self._compute_bands
        )

    def _compute_bands(self):
        """
        Calculate the electronic band structure along a specified k-path.

        This method performs a tight-binding calculation of electronic bands
        by diagonalizing the Hamiltonian at each k-point along the path. The
        results are stored in the band_structure model.
        """

        special_points = self.models["bz_path"]
        num_points = self.computation_view.bands_panel.n_points_spinbox.value()

        # Get the selected unit cell
        uc_id = self.models["selection"]["unit_cell"]
        unit_cell = self.models["unit_cells"][uc_id]

        # Check if the coupling is Hermitian and only then proceed to calculation
        if not unit_cell.is_hermitian():
            self.status_updated.emit("Computation halted: the system is non-Hermitian")
            return

        # Get Hamiltonian function
        hamiltonian_func = unit_cell.get_hamiltonian_function()

        # Perform calculation
        k_path = interpolate_k_path(special_points, num_points)
        self.status_updated.emit("Computing the bands")

        eigenvalues, eigenvectors = band_compute(hamiltonian_func, k_path)
        self.status_updated.emit("Bands computation complete")

        band_structure = BandStructure(
            path=k_path,
            special_points=special_points,
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
        )
        self.models["band_structures"][uc_id] = band_structure

        # Update model
        self.models["active_band_structure"].update(
            {
                "k_path": copy.deepcopy(k_path),
                "bands": copy.deepcopy(np.array(eigenvalues)),
                "special_points": copy.deepcopy(special_points),
            }
        )
