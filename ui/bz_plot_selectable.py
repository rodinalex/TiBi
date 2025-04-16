import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import QSize, Qt, Signal
import pyqtgraph.opengl as gl


class SelectableBrillouinZonePlot(QWidget):
    """
    An enhanced Brillouin Zone visualization that supports point selection.
    
    This is an extension of the original BrillouinZonePlot that adds:
    1. Point selection capabilities via mouse click
    2. A signal to notify when a vertex is selected
    3. Visual highlighting of the selected vertex
    """
    
    # Signal emitted when a vertex is selected with its coordinates
    vertex_selected = Signal(object)  # Emits the coordinates of the selected vertex
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(300, 200))
        
        # Initialize data
        self.bz = None
        self.plot_items = {}  # Map to track mesh items
        self.selected_vertex = None
        self.selected_idx = -1  # Index of the selected vertex
        self.vertex_points = []  # Store vertex coordinates for selection
        
        # Colors
        self.axis_colors = [
            (213 / 255, 94 / 255, 0, 1),
            (0, 158 / 255, 115 / 255, 1),
            (0, 114 / 255, 178 / 255, 1),
        ]  # R, G, B for x, y, z
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create 3D plot widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=8)
        self.view.setBackgroundColor("k")  # Black background
        
        # Enable mouse click events handling
        self.view.mousePressBool = False
        self.view.mousePressEvent = self._handle_mouse_press
        
        # Enable keyboard events for this widget
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Axes
        axis_limit = 10
        axes = [
            np.array([[-axis_limit, 0, 0], [axis_limit, 0, 0]]),
            np.array([[0, -axis_limit, 0], [0, axis_limit, 0]]),
            np.array([[0, 0, -axis_limit], [0, 0, axis_limit]]),
        ]
        for ii, color in enumerate(self.axis_colors):
            self.view.addItem(
                gl.GLLinePlotItem(pos=axes[ii], color=color, width=5, antialias=True)
            )
        
        # Information label below the plot
        self.info_label = QLabel("Use N key to cycle through BZ vertices")
        self.info_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.view, stretch=9)
        layout.addWidget(self.info_label, stretch=1)
    
    def set_BZ(self, bz):
        """
        Set or update the Brillouin zone to be displayed in the 3D view.
        """
        self.bz = bz
        # Clear previous plot items except axes and grid
        for key, item in list(self.plot_items.items()):
            self.view.removeItem(item)
            del self.plot_items[key]
        
        # Reset vertex data
        self.vertex_points = []
        self.selected_vertex = None
        self.selected_idx = -1
        self.info_label.setText("Use N key to cycle through BZ vertices")
        
        if not bz or "bz_vertices" not in bz or "bz_faces" not in bz:
            return
        
        bz_vertices = bz["bz_vertices"]
        bz_faces = bz["bz_faces"]
        
        # Check if we have any vertices to plot
        if len(bz_vertices) == 0:
            # No periodic directions, nothing to visualize
            return
        
        # Plot the BZ vertices as points
        if len(bz_vertices) > 0:
            vertex_size = 0.05  # Size of vertex points
            
            # Ensure all vertices have 3D coordinates
            vertices_3d = []
            for vertex in bz_vertices:
                # Pad with zeros if needed to ensure 3D coordinates
                if len(vertex) == 1:  # 1D case
                    vertices_3d.append([vertex[0], 0, 0])
                elif len(vertex) == 2:  # 2D case
                    vertices_3d.append([vertex[0], vertex[1], 0])
                else:  # 3D case
                    vertices_3d.append(vertex)
            
            # Store vertices for selection
            self.vertex_points = vertices_3d
            
            # Create individual spheres for each vertex (like in the original plot)
            for i, vertex in enumerate(vertices_3d):
                # Create a sphere for the vertex
                try:
                    sphere = gl.GLMeshItem(
                        meshdata=gl.MeshData.sphere(
                            rows=10, cols=10, radius=vertex_size
                        ),
                        smooth=True,
                        color=(1, 1, 1, 0.8),  # White, semi-transparent
                        shader="shaded",
                    )
                    sphere.translate(vertex[0], vertex[1], vertex[2])
                    self.view.addItem(sphere)
                    self.plot_items[f"bz_vertex_{i}"] = sphere
                except Exception as e:
                    print(f"Error creating BZ vertex {i}: {e}")
        
        # Create edges - connect the vertices based on face data
        if len(bz_faces) > 0:
            # Process faces to extract unique edges
            all_edges = []
            for face in bz_faces:
                # Ensure all face vertices have 3D coordinates
                face_vertices = []
                for vertex in face:
                    if len(vertex) == 1:  # 1D case
                        face_vertices.append([vertex[0], 0, 0])
                    elif len(vertex) == 2:  # 2D case
                        face_vertices.append([vertex[0], vertex[1], 0])
                    else:  # 3D case
                        face_vertices.append(vertex)
                
                # Extract edges from each face (connecting consecutive vertices)
                for i in range(len(face_vertices)):
                    next_i = (i + 1) % len(face_vertices)  # Loop back to first vertex
                    all_edges.append([face_vertices[i], face_vertices[next_i]])
            
            # Create a single line item for all BZ edges
            if all_edges:
                # Flatten the list of edges to a list of vertices for GLLinePlotItem
                line_vertices = []
                for edge in all_edges:
                    line_vertices.extend(edge)
                
                # Create a GLLinePlotItem for all BZ edges
                try:
                    bz_edges = gl.GLLinePlotItem(
                        pos=np.array(line_vertices),
                        color=(1, 1, 1, 0.8),  # White, semi-transparent
                        width=2,
                        mode="lines",
                    )
                    self.view.addItem(bz_edges)
                    self.plot_items["bz_edges"] = bz_edges
                except Exception as e:
                    print(f"Error creating BZ edges: {e}")
    
    def _handle_mouse_press(self, event):
        """Handle mouse press events for picking vertices"""
        # Get the mouse position
        pos = event.pos()
        
        # Make sure we have vertices to pick
        if not self.vertex_points:
            # Call the parent class method to handle navigation
            super(gl.GLViewWidget, self.view).mousePressEvent(event)
            return
        
        # Check if right-click or control-click (for selection)
        if event.button() == Qt.RightButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            try:
                # Simplified method - just select a vertex from the available vertices
                # We'll select the first vertex as a test
                if len(self.vertex_points) > 0:
                    # Choose vertex 0 for now (the simplest approach for testing)
                    vertex = self.vertex_points[0]
                    self._select_vertex(vertex, 0)
                    print(f"Selected vertex 0 (testing)")
                    
                    # In a future improvement, we would:
                    # 1. Get the view and projection matrices
                    # 2. Project each 3D vertex to 2D screen position
                    # 3. Find closest to click position
                    # But this requires more complex OpenGL calculations
                    
            except Exception as e:
                print(f"Error in vertex picking: {e}")
            
        # Call the parent class method to handle navigation
        super(gl.GLViewWidget, self.view).mousePressEvent(event)
    
    def _select_vertex(self, vertex, idx):
        """Highlight the selected vertex and emit signal"""
        # Remove previous highlight if any
        if "selected_vertex" in self.plot_items:
            self.view.removeItem(self.plot_items["selected_vertex"])
        
        # Highlight selected vertex with a sphere
        try:
            # Create a sphere for the selected vertex
            sphere = gl.GLMeshItem(
                meshdata=gl.MeshData.sphere(
                    rows=10, cols=10, radius=0.08  # Slightly larger than regular vertices
                ),
                smooth=True,
                color=(1, 0.9, 0, 1),  # Yellow
                shader="shaded",
            )
            sphere.translate(vertex[0], vertex[1], vertex[2])
            self.view.addItem(sphere)
            self.plot_items["selected_vertex"] = sphere
        except Exception as e:
            print(f"Error creating highlight sphere: {e}")
            # Fallback to scatter plot if mesh fails
            highlight = gl.GLScatterPlotItem(
                pos=np.array([vertex]),
                color=(1, 0.9, 0, 1),  # Yellow
                size=10,
                pxMode=True,
            )
            self.view.addItem(highlight)
            self.plot_items["selected_vertex"] = highlight
        
        # Update selected vertex and its index
        self.selected_vertex = vertex
        self.selected_idx = idx
        
        # Emit signal
        self.vertex_selected.emit(vertex)
        
        # Update info label with vertex index and coordinates
        label_text = f"Vertex {idx}: "
        if len(vertex) == 3:
            label_text += f"({vertex[0]:.2f}, {vertex[1]:.2f}, {vertex[2]:.2f})"
        elif len(vertex) == 2:
            label_text += f"({vertex[0]:.2f}, {vertex[1]:.2f})"
        else:
            label_text += f"({vertex[0]:.2f})"
            
        # Additional instruction for new users
        label_text += " - Press N/P to cycle"
        self.info_label.setText(label_text)
    
    def get_selected_vertex(self):
        """Return the currently selected vertex coordinates or None"""
        return self.selected_vertex
        
    def keyPressEvent(self, event):
        """Handle keyboard events for vertex cycling"""
        if event.key() == Qt.Key_N:  # N key to cycle to next vertex
            # Cycle to the next vertex if we have vertices
            if len(self.vertex_points) > 0:
                # Increment index and wrap around to 0 if needed
                next_idx = (self.selected_idx + 1) % len(self.vertex_points)
                next_vertex = self.vertex_points[next_idx]
                
                # Select this vertex
                self._select_vertex(next_vertex, next_idx)
                print(f"Selected vertex {next_idx} (via keyboard)")
        elif event.key() == Qt.Key_P:  # P key to cycle to previous vertex
            # Cycle to the previous vertex if we have vertices
            if len(self.vertex_points) > 0:
                # Decrement index and wrap around to the end if needed
                prev_idx = (self.selected_idx - 1) % len(self.vertex_points) if self.selected_idx > 0 else len(self.vertex_points) - 1
                prev_vertex = self.vertex_points[prev_idx]
                
                # Select this vertex
                self._select_vertex(prev_vertex, prev_idx)
                print(f"Selected vertex {prev_idx} (via keyboard)")
        else:
            # Pass event to parent class for default handling
            super().keyPressEvent(event)