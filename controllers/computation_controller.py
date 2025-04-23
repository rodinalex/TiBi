from PySide6.QtCore import QObject
from src.tibitypes import UnitCell
from src.band_structure import band_compute, interpolate_k_path
from models.data_models import AlwaysNotifyDataModel


class ComputationController(QObject):

    def __init__(self, band_structure: AlwaysNotifyDataModel):
        super().__init__()
        self.band_structure = band_structure

    def compute_bands(self, unit_cell: UnitCell, path, num_points):
        # Get Hamiltonian function
        hamiltonian_func = unit_cell.get_hamiltonian_function()

        # Perform calculation
        k_path = interpolate_k_path(path, num_points)
        bands = band_compute(hamiltonian_func, k_path)

        # Update model
        self.band_structure.update(
            {"k_path": k_path, "bands": bands, "special_points": path}
        )
