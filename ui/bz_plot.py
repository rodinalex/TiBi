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
        self.plot_items = {}  # Map to track mesh items
        self.bz_point_lists = {"vertex": [], "edge": [], "face": []}
        self.selection = {"vertex": None, "edge": None, "face": None}
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
        self.prev_vertex_btn.clicked.connect(lambda: self._select_point(-1, "vertex"))
        self.next_vertex_btn.clicked.connect(lambda: self._select_point(+1, "vertex"))
        # self.prev_vertex_btn.clicked.connect(lambda: self._select_vertex(-1))
        # self.next_vertex_btn.clicked.connect(lambda: self._select_vertex(+1))
        self.add_vertex_btn.clicked.connect(lambda: self._add_point("Vertex"))

        edge_pick_layout = QHBoxLayout()
        self.prev_edge_btn = QPushButton("←")
        self.next_edge_btn = QPushButton("→")
        self.add_edge_btn = QPushButton("+")
        edge_pick_layout.addWidget(self.prev_edge_btn)
        edge_pick_layout.addWidget(self.next_edge_btn)
        edge_pick_layout.addWidget(self.add_edge_btn)
        self.prev_edge_btn.clicked.connect(lambda: self._select_point(-1, "edge"))
        self.next_edge_btn.clicked.connect(lambda: self._select_point(+1, "edge"))
        # self.prev_edge_btn.clicked.connect(lambda: self._select_edge(-1))
        # self.next_edge_btn.clicked.connect(lambda: self._select_edge(+1))
        self.add_edge_btn.clicked.connect(lambda: self._add_point("Edge"))

        face_pick_layout = QHBoxLayout()
        self.prev_face_btn = QPushButton("←")
        self.next_face_btn = QPushButton("→")
        self.add_face_btn = QPushButton("+")
        face_pick_layout.addWidget(self.prev_face_btn)
        face_pick_layout.addWidget(self.next_face_btn)
        face_pick_layout.addWidget(self.add_face_btn)
        self.prev_face_btn.clicked.connect(lambda: self._select_point(-1, "face"))
        self.next_face_btn.clicked.connect(lambda: self._select_point(+1, "face"))
        # self.prev_face_btn.clicked.connect(lambda: self._select_face(-1))
        # self.next_face_btn.clicked.connect(lambda: self._select_face(+1))
        self.add_face_btn.clicked.connect(lambda: self._add_point("Face"))

        # Path control buttons
        path_controls_layout = QHBoxLayout()

        self.remove_last_btn = QPushButton("Remove Last")
        self.remove_last_btn.clicked.connect(self._remove_last_point)
        self.remove_last_btn.setEnabled(False)  # Disabled until path has points

        self.clear_path_btn = QPushButton("Clear")
        self.clear_path_btn.clicked.connect(self._clear_path)

        path_controls_layout.addWidget(self.remove_last_btn)
        path_controls_layout.addWidget(self.clear_path_btn)

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
        self.selection_panel.addLayout(path_controls_layout)

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
        self.bz_point_lists = {"vertex": [], "edge": [], "face": []}
        self.selection = {"vertex": None, "edge": None, "face": None}
        self.bz_path = []

        # Clear previous plot items except axes and grid
        for key, item in list(self.plot_items.items()):
            self.view.removeItem(item)
            del self.plot_items[key]

        # Determine system dimensionality
        self.dim = 0 if len(bz["bz_vertices"]) == 0 else len(bz["bz_vertices"][0])

        # Activate/deactivate buttons based on dimensionality
        self.add_gamma_btn.setEnabled(self.dim > 0)
        for btn in self.vertex_btns:
            btn.setEnabled(self.dim > 0)
        for btn in self.edge_btns:
            btn.setEnabled(self.dim > 1)
        for btn in self.face_btns:
            btn.setEnabled(self.dim > 2)

        # Create the BZ wireframe by making edges (connect the vertices based on face data)
        self._create_bz_wireframe(bz)

        # Extract vertices and faces from the BZ data
        # Note: In 2D, the faces are equivalent to edges. In 3D, the faces are polygons.
        self.bz_point_lists["vertex"] = np.array(bz["bz_vertices"])

        if self.dim == 2:
            # Get the edge points
            self.bz_point_lists["edge"] = []
            for edge in bz["bz_faces"]:
                # Midpoint of the edge
                mid_point = np.mean(edge, axis=0)
                self.bz_point_lists["edge"].append(mid_point)
            self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"])

        elif self.dim == 3:
            # Get the edge and face points
            self.bz_point_lists["edge"] = []
            self.bz_point_lists["face"] = []
            for face in bz["bz_faces"]:
                for ii in range(len(face)):
                    next_ii = (ii + 1) % len(face)
                    # Midpoint of the edge
                    mid_point = np.mean([face[ii], face[next_ii]], axis=0)
                    self.bz_point_lists["edge"].append(mid_point)

                # Midpoint of the face
                mid_point = np.mean(face, axis=0)
                self.bz_point_lists["face"].append(mid_point)
            self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"])
            self.bz_point_lists["face"] = np.array(self.bz_point_lists["face"])

        # Plot the BZ vertices as points
        # Add Gamma point at origin
        sphere = self._make_point()
        self.view.addItem(sphere)
        self.plot_items["Gamma"] = sphere

        # Plot points for vertices, edges, and faces
        pts = [
            self.bz_point_lists["vertex"],
            self.bz_point_lists["edge"],
            self.bz_point_lists["face"],
        ]
        types = ["vertex", "edge", "face"]
        for pt, typ in zip(pts, types):
            if len(pt) > 0:
                pt_3d = self._pad_to_3d(pt)
                self.selection[typ] = 0
                for ii, p in enumerate(pt_3d):
                    sphere = self._make_point()
                    sphere.translate(p[0], p[1], p[2])
                    self.view.addItem(sphere)
                    self.plot_items[f"bz_{typ}_{ii}"] = sphere
                    # Highlight the first point
                    if ii == 0:
                        sphere.setColor(self.selected_point_color)

    def _create_bz_wireframe(self, bz):
        if len(bz["bz_faces"]) > 0:
            # Process faces to extract unique edges
            all_edges = []
            for face in bz["bz_faces"]:
                # Extract edges from each face (connecting consecutive vertices)
                for ii in range(len(face)):
                    next_ii = (ii + 1) % len(face)  # Loop back to first vertex
                    all_edges.append([face[ii], face[next_ii]])

            # Create a single line item for all BZ edges
            # Flatten the list of edges to a list of vertices for GLLinePlotItem
            line_vertices = []
            for edge in all_edges:
                line_vertices.extend(edge)

            # Make sure all the line vertices are 3D
            line_vertices = self._pad_to_3d(line_vertices)

            # Create a GLLinePlotItem for all BZ edges
            bz_wireframe = gl.GLLinePlotItem(
                pos=np.array(line_vertices),
                color=(1, 1, 1, 0.8),
                width=1,
                mode="lines",
            )
            self.view.addItem(bz_wireframe)
            self.plot_items["bz_wireframe"] = bz_wireframe

    def _select_point(self, step, typ):

        # Guard against empty vertex list
        if len(self.bz_point_lists[typ]) == 0:
            return

        prev_vertex = self.selection[typ]

        if self.selection[typ] is None:
            self.selection[typ] = 0
        else:
            self.selection[typ] = (self.selection[typ] + step) % len(
                self.bz_point_lists[typ]
            )

        try:
            # Skip deselection if previous vertex wasn't valid
            if prev_vertex is not None and prev_vertex != self.selection[typ]:
                # Only try to deselect if the key exists
                prev_key = f"bz_{typ}_{prev_vertex}"
                if prev_key in self.plot_items:
                    self.plot_items[prev_key].setColor(self.point_color)

            # Only try to select if the key exists
            new_key = f"bz_{typ}_{self.selection[typ]}"
            if new_key in self.plot_items:
                # Select the new vertex
                self.plot_items[new_key].setColor(self.selected_point_color)
        except Exception as e:
            print(f"Error selecting {typ}: {e}")

    def _select_vertex(self, step):
        """
        Move to the next vertex in the BZ visualization.

        Args:
            step: Direction to move (typically +1 or -1)
        """
        # Guard against empty vertex list
        if len(self.bz_point_lists["vertex"]) == 0:
            return

        prev_vertex = self.selection["vertex"]
        # prev_vertex = self.selected_vertex

        if self.selection["vertex"] is None:
            self.selection["vertex"] = 0
        else:
            self.selection["vertex"] = (self.selection["vertex"] + step) % len(
                self.bz_point_lists["vertex"]
            )

        try:
            # Skip deselection if previous vertex wasn't valid
            if prev_vertex is not None and prev_vertex != self.selection["vertex"]:
                # Only try to deselect if the key exists
                prev_key = f"bz_vertex_{prev_vertex}"
                if prev_key in self.plot_items:
                    self.plot_items[prev_key].setColor(self.point_color)

            # Only try to select if the key exists
            new_key = f"bz_vertex_{self.selection["vertex"]}"
            if new_key in self.plot_items:
                # Select the new vertex
                self.plot_items[new_key].setColor(self.selected_point_color)
        except Exception as e:
            print(f"Error selecting vertex: {e}")

    def _select_edge(self, step):
        """
        Move to the next edge in the BZ visualization.

        Args:
            step: Direction to move (typically +1 or -1)
        """
        # Guard against empty edge list
        if len(self.bz_point_lists["edge"]) == 0:
            return

        prev_edge = self.selection["edge"]

        if self.selection["edge"] is None:
            self.selection["edge"] = 0
        else:
            self.selection["edge"] = (self.selection["edge"] + step) % len(
                self.bz_point_lists["edge"]
            )

        try:
            # Skip deselection if previous edge wasn't valid
            if prev_edge is not None and prev_edge != self.selection["edge"]:
                # Only try to deselect if the key exists
                prev_key = f"bz_edge_{prev_edge}"
                if prev_key in self.plot_items:
                    self.plot_items[prev_key].setColor(self.point_color)

            # Only try to select if the key exists
            new_key = f"bz_edge_{self.selection["edge"]}"
            if new_key in self.plot_items:
                # Select the new edge
                self.plot_items[new_key].setColor(self.selected_point_color)
        except Exception as e:
            print(f"Error selecting edge: {e}")

    def _select_face(self, step):
        """
        Move to the next face in the BZ visualization.

        Args:
            step: Direction to move (typically +1 or -1)
        """
        # Guard against empty face list
        if len(self.bz_point_lists["face"]) == 0:
            return

        prev_face = self.selection["face"]

        if self.selection["face"] is None:
            self.selection["face"] = 0
        else:
            self.selection["face"] = (self.selection["face"] + step) % len(
                self.bz_point_lists["face"]
            )

        try:
            # Skip deselection if previous face wasn't valid
            if prev_face is not None and prev_face != self.selection["face"]:
                # Only try to deselect if the key exists
                prev_key = f"bz_face_{prev_face}"
                if prev_key in self.plot_items:
                    self.plot_items[prev_key].setColor(self.point_color)

            # Only try to select if the key exists
            new_key = f"bz_face_{self.selection["face"]}"
            if new_key in self.plot_items:
                # Select the new face
                self.plot_items[new_key].setColor(self.selected_point_color)
        except Exception as e:
            print(f"Error selecting face: {e}")

    def _make_point(self, vertex_size=0.20):
        """Create a sphere mesh item for a point in the BZ."""
        return gl.GLMeshItem(
            meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=vertex_size),
            smooth=True,
            color=self.point_color,
            shader="shaded",
        )

    def _pad_to_3d(self, points):
        """
        Ensure points have 3D coordinates by padding with zeros if needed.

        Args:
            points: Array of points with coordinates

        Returns:
            Array of points with 3D coordinates
        """
        pad_width = 3 - self.dim
        if pad_width > 0:
            return np.pad(points, ((0, 0), (0, pad_width)), mode="constant")
        return np.array(points)

    def _clear_path(self):
        """Remove all points from the path."""
        self.bz_path = []
        # Remove path from the plot if it exists
        if "bz_path" in self.plot_items:
            self.view.removeItem(self.plot_items["bz_path"])
            del self.plot_items["bz_path"]

        # Disable the remove last button since path is empty
        self.remove_last_btn.setEnabled(False)

    def _remove_last_point(self):
        """Remove the last point added to the path."""
        if self.bz_path:
            # Remove the last point
            self.bz_path.pop()

            # Update path visualization
            self._update_path_visualization()

            # Disable button if path is now empty
            if not self.bz_path:
                self.remove_last_btn.setEnabled(False)

    def _update_path_visualization(self):
        """
        Update the visualization of the BZ path based on current path points.
        """
        # Remove existing path visualization if it exists
        if "bz_path" in self.plot_items:
            try:
                self.view.removeItem(self.plot_items["bz_path"])
                del self.plot_items["bz_path"]
            except Exception as e:
                print(f"Error removing path visualization: {e}")

        # Only create visualization if we have at least 2 points
        if not self.bz_path or len(self.bz_path) < 2:
            return

        # Convert path points to 3D if needed
        path_3d = self._pad_to_3d(self.bz_path)

        # Create line segments for the path
        path_pos = []
        for ii in range(len(path_3d) - 1):
            # Add both points of each segment
            path_pos.extend([path_3d[ii], path_3d[ii + 1]])

        # Create the path visualization
        path_object = gl.GLLinePlotItem(
            pos=np.array(path_pos), color=CF_red, width=5, mode="lines"
        )
        self.view.addItem(path_object)
        self.plot_items["bz_path"] = path_object

    def _add_point(self, point):
        """
        Add a selected point to the Brillouin zone path.

        Args:
            point: The type of point to add ("Gamma", "Vertex", "Edge", or "Face")
        """
        try:
            # Add the selected point to the path
            if point == "Gamma":
                if hasattr(self, "dim") and self.dim > 0:
                    self.bz_path.append([0] * self.dim)
                else:
                    print("Cannot add Gamma point: dimension not set")
                    return

            elif point == "Vertex":
                if (
                    self.selection["vertex"] is not None
                    and self.bz_point_lists["vertex"] is not None
                ):
                    if len(self.bz_point_lists["vertex"]) > self.selection["vertex"]:
                        self.bz_path.append(
                            self.bz_point_lists["vertex"][self.selection["vertex"]]
                        )
                    else:
                        print(f"Invalid vertex index: {self.selection["vertex"]}")
                        return
                else:
                    print("No vertex selected")
                    return

            elif point == "Edge":
                if (
                    self.selection["edge"] is not None
                    and self.bz_point_lists["edge"] is not None
                ):
                    if len(self.bz_point_lists["edge"]) > self.selection["edge"]:
                        self.bz_path.append(
                            self.bz_point_lists["edge"][self.selection["edge"]]
                        )
                    else:
                        print(f"Invalid edge index: {self.selection["edge"]}")
                        return
                else:
                    print("No edge selected")
                    return

            elif point == "Face":
                if (
                    self.selection["face"] is not None
                    and self.bz_point_lists["face"] is not None
                ):
                    if len(self.bz_point_lists["face"]) > self.selection["face"]:
                        self.bz_path.append(
                            self.bz_point_lists["face"][self.selection["face"]]
                        )
                    else:
                        print(f"Invalid face index: {self.selection["face"]}")
                        return
                else:
                    print("No face selected")
                    return

            # Enable the remove last button now that we have points
            self.remove_last_btn.setEnabled(True)

            # Update the path visualization
            self._update_path_visualization()
        except Exception as e:
            print(f"Error adding point: {e}")
