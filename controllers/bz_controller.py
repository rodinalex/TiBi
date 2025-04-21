from PySide6.QtCore import QObject
import numpy as np


class BZController(QObject):
    """
    Controller for managing Brillouin Zone visualization and path construction.
    
    This controller handles interactions with the Brillouin Zone plot,
    including path creation, point selection, and coordination with band
    structure calculations.
    
    Responsibilities:
    - Managing BZ visualization state
    - Handling point selection and path construction
    - Coordinating path data with band structure calculations
    """
    
    def __init__(self, bz_plot, band_plot=None):
        """
        Initialize the BZ controller.
        
        Args:
            bz_plot: The Brillouin Zone plot UI component
            band_plot: Optional band structure plot component
        """
        super().__init__()
        
        # Store references to views
        self.bz_plot = bz_plot
        self.band_plot = band_plot
        
        # Connect UI signals to controller methods
        self.connect_signals()
        
        # Initialize controller state
        self.bz = None
        self.bz_path = []
        self.selection = {"vertex": None, "edge": None, "face": None}
        self.bz_point_lists = {"vertex": [], "edge": [], "face": []}
        self.dim = 0
        
    def connect_signals(self):
        """Connect UI signals to controller methods."""
        # Add point buttons
        self.bz_plot.add_gamma_btn.clicked.connect(lambda: self.add_point("gamma"))
        self.bz_plot.add_vertex_btn.clicked.connect(lambda: self.add_point("vertex"))
        self.bz_plot.add_edge_btn.clicked.connect(lambda: self.add_point("edge"))
        self.bz_plot.add_face_btn.clicked.connect(lambda: self.add_point("face"))
        
        # Selection buttons
        self.bz_plot.prev_vertex_btn.clicked.connect(lambda: self.select_point(-1, "vertex"))
        self.bz_plot.next_vertex_btn.clicked.connect(lambda: self.select_point(+1, "vertex"))
        self.bz_plot.prev_edge_btn.clicked.connect(lambda: self.select_point(-1, "edge"))
        self.bz_plot.next_edge_btn.clicked.connect(lambda: self.select_point(+1, "edge"))
        self.bz_plot.prev_face_btn.clicked.connect(lambda: self.select_point(-1, "face"))
        self.bz_plot.next_face_btn.clicked.connect(lambda: self.select_point(+1, "face"))
        
        # Path manipulation buttons
        self.bz_plot.remove_last_btn.clicked.connect(self.remove_last_point)
        self.bz_plot.clear_path_btn.clicked.connect(self.clear_path)
    
    def set_bz(self, bz):
        """
        Set the Brillouin zone data and update the visualization.
        
        Args:
            bz: Dictionary containing 'bz_vertices' and 'bz_faces'
        """
        self.bz = bz
        self.bz_point_lists = {"vertex": [], "edge": [], "face": []}
        self.selection = {"vertex": None, "edge": None, "face": None}
        self.bz_path = []
        
        # Determine system dimensionality
        self.dim = 0 if len(bz["bz_vertices"]) == 0 else len(bz["bz_vertices"][0])
        
        # Extract vertices and faces
        self.bz_point_lists["vertex"] = np.array(bz["bz_vertices"]) if len(bz["bz_vertices"]) > 0 else []
        
        # Process edges and faces based on dimensionality
        if self.dim == 2:
            self._process_2d_bz(bz)
        elif self.dim == 3:
            self._process_3d_bz(bz)
            
        # Update the UI
        self.bz_plot.set_BZ(bz)
        
        # Update button states
        self._update_button_states()
    
    def _process_2d_bz(self, bz):
        """Process 2D Brillouin zone points."""
        # Get the edge points (midpoints of faces in 2D)
        self.bz_point_lists["edge"] = []
        for edge in bz["bz_faces"]:
            mid_point = np.mean(edge, axis=0)
            self.bz_point_lists["edge"].append(mid_point)
        self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"]) if self.bz_point_lists["edge"] else []
    
    def _process_3d_bz(self, bz):
        """Process 3D Brillouin zone points."""
        # Get the edge and face points
        self.bz_point_lists["edge"] = []
        self.bz_point_lists["face"] = []
        
        for face in bz["bz_faces"]:
            # Extract edge midpoints
            for ii in range(len(face)):
                next_ii = (ii + 1) % len(face)
                mid_point = np.mean([face[ii], face[next_ii]], axis=0)
                self.bz_point_lists["edge"].append(mid_point)
            
            # Calculate face midpoint
            face_mid_point = np.mean(face, axis=0)
            self.bz_point_lists["face"].append(face_mid_point)
            
        self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"]) if self.bz_point_lists["edge"] else []
        self.bz_point_lists["face"] = np.array(self.bz_point_lists["face"]) if self.bz_point_lists["face"] else []
    
    def select_point(self, step, typ):
        """
        Select a point in the Brillouin zone.
        
        Args:
            step: Direction to move in point list (-1 for previous, +1 for next)
            typ: Type of point to select ("vertex", "edge", or "face")
        """
        # Guard against empty vertex list
        if len(self.bz_point_lists[typ]) == 0:
            return
            
        prev_point = self.selection[typ]
        
        if prev_point is None:
            self.selection[typ] = 0
        else:
            self.selection[typ] = (prev_point + step) % len(self.bz_point_lists[typ])
        
        # Update the UI
        self.bz_plot._select_point(step, typ)
    
    def add_point(self, point_type):
        """
        Add a point to the BZ path.
        
        Args:
            point_type: Type of point to add ("gamma", "vertex", "edge", or "face")
        """
        if point_type == "gamma":
            self.bz_path.append([0] * self.dim)
        else:
            # Check if we have a valid selection
            if (self.selection[point_type] is not None and 
                len(self.bz_point_lists[point_type]) > self.selection[point_type]):
                # Add the selected point to the path
                self.bz_path.append(self.bz_point_lists[point_type][self.selection[point_type]])
            else:
                print(f"No valid {point_type} point selected")
                return
        
        # Update the UI
        self.bz_plot._add_point(point_type)
        
        # Update button states
        self._update_button_states()
    
    def remove_last_point(self):
        """Remove the last point from the BZ path."""
        if self.bz_path:
            # Remove the last point
            self.bz_path.pop()
            
            # Update the UI
            self.bz_plot._remove_last_point()
            
            # Update button states
            self._update_button_states()
    
    def clear_path(self):
        """Clear the entire BZ path."""
        self.bz_path = []
        
        # Update the UI
        self.bz_plot._clear_path()
        
        # Update button states
        self._update_button_states()
    
    def _update_button_states(self):
        """Update the enabled state of buttons based on the path state."""
        # Enable/disable path manipulation buttons
        has_points = len(self.bz_path) > 0
        has_multiple_points = len(self.bz_path) >= 2
        
        # These button states should be managed by the controller
        # but we need to refactor BrillouinZonePlot first to expose these
        # methods instead of implementing the logic directly in the view
        pass
        
    def get_path(self):
        """Get the current BZ path."""
        return self.bz_path.copy() if self.bz_path else []
        
    def get_path_dimension(self):
        """Get the dimensionality of the current BZ."""
        return self.dim