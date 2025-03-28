import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QColorDialog
from PySide6.QtCore import Signal, Qt, QSize
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from src.tibitypes import UnitCell, Site, BasisVector


class UnitCellPlot(QWidget):
    """A 3D visualization panel for Unit Cells using PyQtGraph's OpenGL support."""
    
    # Signals for interacting with other components
    site_selected = Signal(object)  # Emits site ID when clicked
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(400, 400))
        
        # Initialize data
        self.unit_cell = None
        self.selected_site = None
        self.plot_items = {}  # Map to track mesh items for selection
        
        # Colors
        self.axis_colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]  # R, G, B for x, y, z
        self.cell_color = (0.8, 0.8, 0.8, 0.3)  # Light gray, semi-transparent
        self.site_color = (1, 0.8, 0, 0.8)  # Orange for sites
        self.selected_site_color = (1, 0, 0, 1)  # Red for selected site
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create 3D plot widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=8)
        self.view.setBackgroundColor('w')  # White background
        
        # Initialize grid and axes for reference
        self._setup_grid_and_axes()
        
        layout.addWidget(self.view)
    
    def _setup_grid_and_axes(self):
        """Set up the reference grid and coordinate axes."""
        # Add coordinate grid
        grid = gl.GLGridItem()
        grid.setSize(10, 10, 1)
        grid.setSpacing(1, 1, 1)
        grid.translate(0, 0, -0.5)  # Move grid slightly below origin
        self.view.addItem(grid)
        
        # Add coordinate axes
        for i, color in enumerate(self.axis_colors):
            axis = gl.GLLinePlotItem(
                pos=np.array([[0, 0, 0], [0, 0, 0]]),
                color=color,
                width=3,
                antialias=True
            )
            self.view.addItem(axis)
            # Store reference
            self.plot_items[f'axis_{i}'] = axis
    
    def set_unit_cell(self, unit_cell):
        """Set or update the unit cell to be displayed."""
        self.unit_cell = unit_cell
        # Clear previous plot items except axes and grid
        self._clear_unit_cell_items()
        
        if not unit_cell:
            return
        
        # Plot the new unit cell
        self._plot_unit_cell()
        self._plot_sites()
        
        # Update the axes to match unit cell basis vectors
        self._update_axes()
    
    def _clear_unit_cell_items(self):
        """Clear all unit cell related items from the 3D view."""
        # Keep track of keys to remove
        keys_to_remove = []
        
        for key, item in self.plot_items.items():
            # Don't remove the axes or grid
            if key.startswith('axis_'):
                continue
                
            self.view.removeItem(item)
            keys_to_remove.append(key)
        
        # Remove items from the dictionary
        for key in keys_to_remove:
            del self.plot_items[key]
    
    def _update_axes(self):
        """Update the coordinate axes to match the unit cell basis vectors."""
        if not self.unit_cell:
            return
            
        # Scale factor to make axes visible
        scale = 2.0
        
        # Update each axis to represent a basis vector
        vectors = [self.unit_cell.v1, self.unit_cell.v2, self.unit_cell.v3]
        
        for i, vector in enumerate(vectors):
            axis = self.plot_items[f'axis_{i}']
            # Create line from origin to the basis vector
            pos = np.array([
                [0, 0, 0],
                [vector.x * scale, vector.y * scale, vector.z * scale]
            ])
            axis.setData(pos=pos)
    
    def _plot_unit_cell(self):
        """Plot the unit cell parallelepiped."""
        if not self.unit_cell:
            return
            
        # Extract basis vectors
        v1 = np.array([self.unit_cell.v1.x, self.unit_cell.v1.y, self.unit_cell.v1.z])
        v2 = np.array([self.unit_cell.v2.x, self.unit_cell.v2.y, self.unit_cell.v2.z])
        v3 = np.array([self.unit_cell.v3.x, self.unit_cell.v3.y, self.unit_cell.v3.z])
        
        # Create vertices for the parallelepiped
        verts = np.array([
            [0, 0, 0],          # Origin
            v1,                 # v1
            v2,                 # v2
            v1 + v2,            # v1 + v2
            v3,                 # v3
            v1 + v3,            # v1 + v3
            v2 + v3,            # v2 + v3
            v1 + v2 + v3        # v1 + v2 + v3
        ])
        
        # Define the faces of the parallelepiped (as indices to verts)
        faces = np.array([
            [0, 1, 3, 2],  # Bottom face
            [4, 5, 7, 6],  # Top face
            [0, 4, 5, 1],  # Side face 1
            [2, 3, 7, 6],  # Side face 2
            [0, 2, 6, 4],  # Side face 3
            [1, 5, 7, 3]   # Side face 4
        ])
        
        # Create mesh item for the unit cell
        cell_mesh = gl.GLMeshItem(
            vertexes=verts, 
            faces=faces, 
            faceColors=np.tile(self.cell_color, (len(faces), 1)),
            smooth=False,
            drawEdges=True,
            edgeColor=(0, 0, 0, 1)
        )
        
        self.view.addItem(cell_mesh)
        self.plot_items['unit_cell'] = cell_mesh
    
    def _plot_sites(self):
        """Plot all sites within the unit cell."""
        if not self.unit_cell or not self.unit_cell.sites:
            return
            
        # Extract basis vectors
        v1 = np.array([self.unit_cell.v1.x, self.unit_cell.v1.y, self.unit_cell.v1.z])
        v2 = np.array([self.unit_cell.v2.x, self.unit_cell.v2.y, self.unit_cell.v2.z])
        v3 = np.array([self.unit_cell.v3.x, self.unit_cell.v3.y, self.unit_cell.v3.z])
        
        # Plot each site as a sphere
        for site_id, site in self.unit_cell.sites.items():
            # Calculate the position in Cartesian coordinates
            pos = site.c1 * v1 + site.c2 * v2 + site.c3 * v3
            
            # Create a sphere for the site
            sphere = gl.GLMeshItem(
                meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=0.1),
                smooth=True,
                color=self.site_color,
                shader='shaded'
            )
            sphere.translate(pos[0], pos[1], pos[2])
            
            # Store site ID as user data for interaction
            sphere.site_id = site_id
            
            self.view.addItem(sphere)
            self.plot_items[f'site_{site_id}'] = sphere
    
    def select_site(self, site_id):
        """Highlight a selected site."""
        # Reset previously selected site
        if self.selected_site:
            prev_sphere = self.plot_items.get(f'site_{self.selected_site}')
            if prev_sphere:
                prev_sphere.setColor(self.site_color)
        
        # Highlight new selected site
        self.selected_site = site_id
        if site_id:
            sphere = self.plot_items.get(f'site_{site_id}')
            if sphere:
                sphere.setColor(self.selected_site_color)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks to select sites."""
        # Let the view handle mouse events for 3D rotation and navigation
        # The actual picking of objects should be handled in the GLViewWidget
        super().mousePressEvent(event)
        
        # We need to implement picking through the GLViewWidget
        # For now, this is a placeholder that will be implemented in the future
        # when we can properly implement ray picking
        
        # Future implementation:
        # 1. Get mouse position in view coordinates
        # 2. Use ray casting to determine which site was clicked
        # 3. Emit site_selected signal with the site ID
        # 4. Highlight the selected site in the plot
        
        # For now, we rely on the tree selection to highlight sites
        # This is a TODO item as noted in the project roadmap