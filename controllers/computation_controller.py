from PySide6.QtCore import QObject
import numpy as np
from src.band_structure import interpolate_k_path, band_compute


class ComputationController(QObject):
    """
    Controller for managing physics calculations and result visualization.
    
    This controller handles band structure calculations, taking input from
    the BZ controller and unit cell models, and updating the band structure plot.
    
    Responsibilities:
    - Coordinating band structure calculations
    - Processing calculation inputs and results
    - Updating visualization components with calculation results
    """
    
    def __init__(self, unit_cells, bz_controller, band_plot):
        """
        Initialize the computation controller.
        
        Args:
            unit_cells: Dictionary mapping UUID to UnitCell objects
            bz_controller: Controller for Brillouin zone operations
            band_plot: The band structure plot UI component
        """
        super().__init__()
        
        # Store references to models and views
        self.unit_cells = unit_cells
        self.bz_controller = bz_controller
        self.band_plot = band_plot
        
        # Initialize controller state
        self.current_unit_cell_id = None
        self.bands = None
        self.k_path = None
        self.path_positions = None
    
    def set_unit_cell(self, unit_cell_id):
        """
        Set the current unit cell for calculations.
        
        Args:
            unit_cell_id: UUID of the selected unit cell
        """
        self.current_unit_cell_id = unit_cell_id
    
    def compute_bands(self):
        """
        Compute band structure along the selected BZ path.
        
        Takes the current unit cell and BZ path, computes the band structure,
        and updates the band plot with the results.
        """
        # Check if we have a valid unit cell and path
        if not self.current_unit_cell_id or self.current_unit_cell_id not in self.unit_cells:
            print("No valid unit cell selected")
            return
            
        # Get the BZ path from the controller
        path = self.bz_controller.get_path()
        if not path or len(path) < 2:
            print("Need at least two points to define a path")
            return
            
        # Get the unit cell and its Hamiltonian function
        unit_cell = self.unit_cells[self.current_unit_cell_id]
        hamiltonian = unit_cell.get_hamiltonian_function()
        
        # Get the number of points for interpolation
        n_points = self.bz_controller.bz_plot.n_points_spinbox.value()
        
        # Interpolate the path
        k_path = interpolate_k_path([np.copy(p) for p in path], n_points)
        
        # Compute the bands
        bands = band_compute(hamiltonian, k_path)
        
        # Calculate positions along the path for plotting
        step = np.linalg.norm(np.diff(k_path, axis=0), axis=1)
        pos = np.hstack((0, np.cumsum(step)))
        
        # Store results
        self.bands = bands
        self.k_path = k_path
        self.path_positions = pos
        
        # Update the band plot
        self.band_plot._plot_bands(pos, bands)
        
    def get_band_data(self):
        """
        Get the computed band structure data.
        
        Returns:
            Tuple of (path_positions, bands) or (None, None) if no data available
        """
        return (self.path_positions, self.bands) if self.bands is not None else (None, None)