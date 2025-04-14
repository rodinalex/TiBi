import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import QSize
import pyqtgraph.opengl as gl


class BrillouinZonePlot(QWidget):
    """
    A 3D visualization panel for Brillouin Zone using PyQtGraph's OpenGL support.

    Displays a Brillouin zone as a wireframe with vertices shown as small spheres.
    The visualization supports rotation and zooming. The coordinate system shows 
    the reciprocal space axes.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(300, 200))

        # Initialize data
        self.bz = None
        self.plot_items = {}  # Map to track mesh items
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

        layout.addWidget(self.view)

    def set_BZ(self, bz):
        """
        Set or update the Brillouin zone to be displayed in the 3D view.

        This method handles the complete process of updating the BZ visualization:
        1. Stores the BZ data (vertices and faces)
        2. Clears existing visualization elements
        3. Creates new visualization elements for the BZ vertices and edges
        
        Args:
            bz: Dictionary containing 'bz_vertices' and 'bz_faces' or None to clear the view
        """
        self.bz = bz
        # Clear previous plot items except axes and grid
        for key, item in list(self.plot_items.items()):
            self.view.removeItem(item)
            del self.plot_items[key]

        if not bz or 'bz_vertices' not in bz or 'bz_faces' not in bz:
            return

        bz_vertices = bz['bz_vertices']
        bz_faces = bz['bz_faces']
        
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
            
            # Create a sphere for each vertex
            for i, vertex in enumerate(vertices_3d):
                try:
                    sphere = gl.GLMeshItem(
                        meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=vertex_size),
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
                        mode="lines"
                    )
                    self.view.addItem(bz_edges)
                    self.plot_items["bz_edges"] = bz_edges
                except Exception as e:
                    print(f"Error creating BZ edges: {e}")

    def mousePressEvent(self, event):
        """Handle mouse events for 3D rotation and navigation."""
        super().mousePressEvent(event)
