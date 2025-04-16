import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
)
from PySide6.QtCore import QSize, Qt
import pyqtgraph.opengl as gl
from resources.colors import CF_red, CF_vermillion, CF_yellow, CF_green, CF_sky, CF_blue


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
        self.bz_vertex_points = None
        self.bz_edge_points = None
        self.bz_face_points = None
        self.plot_items = {}  # Map to track mesh items
        self.selected_vertex = None
        self.selected_edge = None
        self.selected_face = None
        self.bz_path = []
        # Colors
        self.axis_colors = [
            CF_vermillion,
            CF_green,
            CF_blue,
        ]  # R, G, B for x, y, z
        self.point_color = CF_sky
        self.selected_point_color = CF_yellow

        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create 3D plot widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=20)
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

        # Selection panel
        self.selection_panel = QVBoxLayout()
        self.selection_panel_label = QLabel("Create a BZ Path")
        self.selection_panel_label.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(2)

        gamma_pick_layout = QHBoxLayout()
        self.add_gamma_btn = QPushButton("+")
        gamma_pick_layout.addWidget(self.add_gamma_btn)
        self.add_gamma_btn.clicked.connect(lambda: self._add_point("Gamma"))

        vertex_pick_layout = QHBoxLayout()
        self.prev_vertex_btn = QPushButton("←")
        self.next_vertex_btn = QPushButton("→")
        self.add_vertex_btn = QPushButton("+")
        vertex_pick_layout.addWidget(self.prev_vertex_btn)
        vertex_pick_layout.addWidget(self.next_vertex_btn)
        vertex_pick_layout.addWidget(self.add_vertex_btn)
        self.prev_vertex_btn.clicked.connect(lambda: self._select_vertex(-1))
        self.next_vertex_btn.clicked.connect(lambda: self._select_vertex(+1))
        self.add_vertex_btn.clicked.connect(lambda: self._add_point("Vertex"))

        edge_pick_layout = QHBoxLayout()
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("+")
        edge_pick_layout.addWidget(self.prev_edge_btn)
        edge_pick_layout.addWidget(self.next_edge_btn)
        edge_pick_layout.addWidget(self.add_edge_btn)
        self.prev_edge_btn.clicked.connect(lambda: self._select_edge(-1))
        self.next_edge_btn.clicked.connect(lambda: self._select_edge(+1))
        self.add_edge_btn.clicked.connect(lambda: self._add_point("Edge"))

        face_pick_layout = QHBoxLayout()
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("+")
        face_pick_layout.addWidget(self.prev_face_btn)
        face_pick_layout.addWidget(self.next_face_btn)
        face_pick_layout.addWidget(self.add_face_btn)
        self.prev_face_btn.clicked.connect(lambda: self._select_face(-1))
        self.next_face_btn.clicked.connect(lambda: self._select_face(+1))
        self.add_face_btn.clicked.connect(lambda: self._add_point("Face"))

        self.clear_path_btn = QPushButton("Clear")
        self.clear_path_btn.clicked.connect(lambda: self._clear_path())

        btns = [
            self.add_gamma_btn,
            self.prev_vertex_btn,
            self.next_vertex_btn,
            self.add_vertex_btn,
            self.prev_edge_btn,
            self.next_edge_btn,
            self.add_edge_btn,
            self.prev_face_btn,
            self.next_face_btn,
            self.add_face_btn,
        ]
        for btn in btns:
            btn.setEnabled(False)

        self.vertex_btns = [
            self.prev_vertex_btn,
            self.next_vertex_btn,
            self.add_vertex_btn,
        ]
        self.edge_btns = [self.prev_edge_btn, self.next_edge_btn, self.add_edge_btn]
        self.face_btns = [self.prev_face_btn, self.next_face_btn, self.add_face_btn]

        form_layout.addRow("Γ:", gamma_pick_layout)
        form_layout.addRow("Vertex:", vertex_pick_layout)
        form_layout.addRow("Edge:", edge_pick_layout)
        form_layout.addRow("Face:", face_pick_layout)

        self.selection_panel.addWidget(self.selection_panel_label)
        self.selection_panel.addLayout(form_layout)
        self.selection_panel.addWidget(self.clear_path_btn)

        layout.addWidget(self.view, stretch=1)
        layout.addLayout(self.selection_panel, stretch=1)

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
        self.bz_vertex_points = []  # Points for vertices
        self.bz_edge_points = []  # Points in the middle of each edge
        self.bz_face_points = []  # Points in the middle of each face
        self.selected_vertex = None
        self.selectedEdge = None
        self.selectedFace = None
        self.bz_path = []

        # Clear previous plot items except axes and grid
        for key, item in list(self.plot_items.items()):
            self.view.removeItem(item)
            del self.plot_items[key]

        if not bz or "bz_vertices" not in bz or "bz_faces" not in bz:
            return
        # Extract vertices and faces from the BZ data. Note that in 2D, the faces are equivalent to edges.
        # In 3D, the faces are polygons.
        self.bz_vertex_points = bz["bz_vertices"]
        # System dimensionality
        if len(self.bz_vertex_points) == 0:
            self.dim = 0
        else:
            self.dim = len(bz["bz_vertices"][0])

        # Activate/deactivate buttons based on dimensionality
        self.add_gamma_btn.setEnabled(self.dim > 0)
        for btn in self.vertex_btns:
            btn.setEnabled(self.dim > 0)
        for btn in self.edge_btns:
            btn.setEnabled(self.dim > 1)
        for btn in self.face_btns:
            btn.setEnabled(self.dim > 2)

        if self.dim == 2:
            # Get the edge points
            self.bz_edge_points = []
            for edge in bz["bz_faces"]:
                # Midpoint of the edge
                mid_point = np.mean(edge, axis=0)
                self.bz_edge_points.append(mid_point)
            self.bz_edge_points = np.array(self.bz_edge_points)

        elif self.dim == 3:
            # Get the edge and face points
            self.bz_edge_points = []
            self.bz_face_points = []
            for face in bz["bz_faces"]:
                for ii in range(len(face)):
                    next_ii = (ii + 1) % len(face)
                    # Midpoint of the edge
                    mid_point = np.mean([face[ii], face[next_ii]], axis=0)
                    self.bz_edge_points.append(mid_point)

                # Midpoint of the face
                mid_point = np.mean(face, axis=0)
                self.bz_face_points.append(mid_point)
            self.bz_edge_points = np.array(self.bz_edge_points)
            self.bz_face_points = np.array(self.bz_face_points)

        # Create edges - connect the vertices based on face data
        if len(bz["bz_faces"]) > 0:
            # Process faces to extract unique edges
            all_edges = []
            for face in bz["bz_faces"]:
                # Extract edges from each face (connecting consecutive vertices)
                for ii in range(len(face)):
                    next_ii = (ii + 1) % len(face)  # Loop back to first vertex
                    all_edges.append([face[ii], face[next_ii]])

            # Create a single line item for all BZ edges
            if all_edges:
                # Flatten the list of edges to a list of vertices for GLLinePlotItem
                line_vertices = []
                for edge in all_edges:
                    line_vertices.extend(edge)
            # Make sure all the line vertices are 3D
            pad_width = 3 - self.dim
            if pad_width > 0:
                line_vertices = np.pad(
                    line_vertices, ((0, 0), (0, pad_width)), mode="constant"
                )
            else:
                line_vertices = line_vertices

            # Create a GLLinePlotItem for all BZ edges
            try:
                bz_edges = gl.GLLinePlotItem(
                    pos=np.array(line_vertices),
                    color=(1, 1, 1, 0.8),  # White, semi-transparent
                    width=1,
                    mode="lines",
                )
                self.view.addItem(bz_edges)
                self.plot_items["bz_edges"] = bz_edges
            except Exception as e:
                print(f"Error creating BZ edges: {e}")

        # Plot the BZ vertices as points
        if len(self.bz_vertex_points) > 0:

            pad_width = 3 - self.dim
            if pad_width > 0:
                vertices_3d = np.pad(
                    self.bz_vertex_points, ((0, 0), (0, pad_width)), mode="constant"
                )
            else:
                vertices_3d = self.bz_vertex_points

            # Create a sphere for each vertex
            for ii, vertex in enumerate(vertices_3d):
                try:
                    sphere = self._make_point()
                    sphere.translate(vertex[0], vertex[1], vertex[2])
                    self.view.addItem(sphere)
                    self.plot_items[f"bz_vertex_{ii}"] = sphere
                except Exception as e:
                    print(f"Error creating BZ vertex {ii}: {e}")
            # Add Gamma point
            sphere = self._make_point()
            self.view.addItem(sphere)
            self.plot_items[f"Gamma"] = sphere
        else:
            return

        if len(self.bz_edge_points) > 0:

            pad_width = 3 - self.dim
            if pad_width > 0:
                edges_3d = np.pad(
                    self.bz_edge_points, ((0, 0), (0, pad_width)), mode="constant"
                )
            else:
                edges_3d = self.bz_edge_points

            # Create a sphere for each vertex
            for ii, edge in enumerate(edges_3d):
                try:
                    sphere = self._make_point()
                    sphere.translate(edge[0], edge[1], edge[2])
                    self.view.addItem(sphere)
                    self.plot_items[f"bz_edge_{ii}"] = sphere
                except Exception as e:
                    print(f"Error creating BZ edge {ii}: {e}")
        else:
            return

        if len(self.bz_face_points) > 0:

            pad_width = 3 - self.dim
            if pad_width > 0:
                faces_3d = np.pad(
                    self.bz_face_points, ((0, 0), (0, pad_width)), mode="constant"
                )
            else:
                faces_3d = self.bz_face_points

            # Create a sphere for each vertex
            for ii, face in enumerate(faces_3d):
                try:
                    sphere = self._make_point()
                    sphere.translate(face[0], face[1], face[2])
                    self.view.addItem(sphere)
                    self.plot_items[f"bz_face_{ii}"] = sphere
                except Exception as e:
                    print(f"Error creating BZ face {ii}: {e}")

    def _select_vertex(self, step):
        """
        Move to the next vertex in the BZ visualization.
        """
        if self.selected_vertex is None:
            self.selected_vertex = 0
            prev_vertex = None
        else:
            prev_vertex = self.selected_vertex
            self.selected_vertex = (self.selected_vertex + step) % len(
                self.bz_vertex_points
            )
        if prev_vertex is not None:
            # Deselect the previous vertex
            self.plot_items[f"bz_vertex_{prev_vertex}"].setColor(self.point_color)
        # Select the new vertex
        self.plot_items[f"bz_vertex_{self.selected_vertex}"].setColor(
            self.selected_point_color
        )

    def _select_edge(self, step):
        """
        Move to the next edge in the BZ visualization.
        """
        if self.selected_edge is None:
            self.selected_edge = 0
            prev_edge = None
        else:
            prev_edge = self.selected_edge
            self.selected_edge = (self.selected_edge + step) % len(self.bz_edge_points)
        if prev_edge is not None:
            # Deselect the previous edge
            self.plot_items[f"bz_edge_{prev_edge}"].setColor(self.point_color)
        # Select the new edge
        self.plot_items[f"bz_edge_{self.selected_edge}"].setColor(
            self.selected_point_color
        )

    def _select_face(self, step):
        """
        Move to the next face in the BZ visualization.
        """
        if self.selected_face is None:
            self.selected_face = 0
            prev_face = None
        else:
            prev_face = self.selected_face
            self.selected_face = (self.selected_face + step) % len(self.bz_face_points)
        if prev_face is not None:
            # Deselect the previous edge
            self.plot_items[f"bz_face_{prev_face}"].setColor(self.point_color)
        # Select the new edge
        self.plot_items[f"bz_face_{self.selected_face}"].setColor(
            self.selected_point_color
        )

    def _make_point(self, vertex_size=0.20):
        return gl.GLMeshItem(
            meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=vertex_size),
            smooth=True,
            color=self.point_color,
            shader="shaded",
        )

    def _clear_path(self):
        self.bz_path = []
        # Remove path from the plot
        self.view.removeItem(self.plot_items["bz_path"])
        del self.plot_items["bz_path"]

    def _add_point(self, point):
        if point == "Gamma":
            self.bz_path.append([0] * self.dim)
        elif point == "Vertex":
            self.bz_path.append(self.bz_vertex_points[self.selected_vertex])
        elif point == "Edge":
            self.bz_path.append(self.bz_edge_points[self.selected_edge])
        elif point == "Face":
            self.bz_path.append(self.bz_face_points[self.selected_face])

        print(self.bz_path)

        if len(self.bz_path) > 1:
            pad_width = 3 - self.dim
            if pad_width > 0:
                path_3d = np.pad(
                    self.bz_path, ((0, 0), (0, pad_width)), mode="constant"
                )
            else:
                path_3d = self.bz_face_points

            path_segments = []

            for ii in range(len(self.bz_path) - 1):
                path_segments.append([self.bz_path[ii], self.bz_path[ii + 1]])
            path_object = gl.GLLinePlotItem(
                pos=np.array(path_segments), color=CF_red, width=2, mode="lines"
            )
            self.view.addItem(path_object)

            self.plot_items["bz_path"] = path_object
