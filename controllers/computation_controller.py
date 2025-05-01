from PySide6.QtCore import QObject
from src.tibitypes import UnitCell
from src.band_structure import band_compute, interpolate_k_path
from models.data_models import AlwaysNotifyDataModel
from views.computation_view import ComputationView


class ComputationController(QObject):
    """
    Controller responsible for physics calculations within the application.

    This controller handles the computational aspects of the application, such as
    band structure calculations, and updates the corresponding data models with the results.
    It isolates the calculation logic from both the UI and the data storage, following
    the MVC pattern.
    """

    def __init__(
        self, computation_view: ComputationView, band_structure: AlwaysNotifyDataModel
    ):
        """
        Initialize the computation controller.

        Args:
            band_structure: Data model that will store calculation results
        """
        super().__init__()
        self.computation_view = computation_view
        self.band_structure = band_structure

        # Connect the signales

    def compute_bands(self, unit_cell: UnitCell, path, num_points):
        """
        Calculate the electronic band structure along a specified k-path.

        This method performs a tight-binding calculation of electronic bands
        by diagonalizing the Hamiltonian at each k-point along the path. The
        results are stored in the band_structure model.

        Args:
            unit_cell: The unit cell containing the tight-binding model
            path: List of k-points defining special points along the path
            num_points: Total number of points to calculate along the path
                        (distributed according to segment lengths)
        """
        # Get Hamiltonian function
        hamiltonian_func = unit_cell.get_hamiltonian_function()

        # Perform calculation
        k_path = interpolate_k_path(path, num_points)
        bands = band_compute(hamiltonian_func, k_path)

        # Update model
        self.band_structure.update(
            {"k_path": k_path, "bands": bands, "special_points": path}
        )
