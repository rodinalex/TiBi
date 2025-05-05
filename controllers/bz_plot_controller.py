import uuid
from PySide6.QtCore import QObject
from src.tibitypes import UnitCell
from models.data_models import DataModel
from views.bz_plot_view import BrillouinZonePlotView
from views.computation_view import ComputationView
import pyqtgraph.opengl as gl
from resources.colors import CF_red
import numpy as np


class BrillouinZonePlotController(QObject):
    """
    Controller for the Brillouin zone plot view.

    This controller manages the 3D visualization of the Brillouin zone and
    provides functionality for selecting points within the BZ and creating paths
    for band structure calculations. It observes the unit cell data model and
    updates the visualization whenever the unit cell changes.

    The controller also handles the creation of k-paths (sequences of k-points
    in reciprocal space) that can be used for band structure calculations. When
    a path is complete, it can emit a signal requesting band structure computation.
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        bz_path,
        bz_plot_view: BrillouinZonePlotView,
        computation_view: ComputationView,
    ):
        """
        Initialize the Brillouin zone plot controller.

        Args:
            unit_cells: Dictionary mapping UUIDs to UnitCell objects
            selection: Model tracking the currently selected unit cell, site, and state
            bz_path: A list of high-symmetry points in the BZ
            bz_plot_view: The view component for displaying the Brillouin zone
            computational_view: The view component that contains controls for creating a path in the BZ.
        """
        super().__init__()

        self.unit_cells = unit_cells
        self.selection = selection
        self.bz_path = bz_path
        self.bz_plot_view = bz_plot_view
        self.computation_view = computation_view

        # Internal controller state
        self.unit_cell = None
        self.bz_plot_items = {}  # Dictionary to store plot items
        self.bz_vertices = []  # Coordinates of BZ vertices
        self.bz_faces = (
            []
        )  # A list of lists, where each inner list contains the vertices of a face
        self.dim = 0
        self.bz_point_selection = {"vertex": None, "edge": None, "face": None}
        self.bz_point_lists = {"vertex": [], "edge": [], "face": []}

        self.computation_view.bands_panel.add_gamma_btn.clicked.connect(
            lambda: self._add_point("gamma")
        )
        self.computation_view.bands_panel.prev_vertex_btn.clicked.connect(
            lambda: self._select_point(-1, "vertex")
        )
        self.computation_view.bands_panel.next_vertex_btn.clicked.connect(
            lambda: self._select_point(+1, "vertex")
        )
        self.computation_view.bands_panel.add_vertex_btn.clicked.connect(
            lambda: self._add_point("vertex")
        )
        self.computation_view.bands_panel.prev_edge_btn.clicked.connect(
            lambda: self._select_point(-1, "edge")
        )
        self.computation_view.bands_panel.next_edge_btn.clicked.connect(
            lambda: self._select_point(+1, "edge")
        )
        self.computation_view.bands_panel.add_edge_btn.clicked.connect(
            lambda: self._add_point("edge")
        )

        self.computation_view.bands_panel.prev_face_btn.clicked.connect(
            lambda: self._select_point(-1, "face")
        )
        self.computation_view.bands_panel.next_face_btn.clicked.connect(
            lambda: self._select_point(+1, "face")
        )

        self.computation_view.bands_panel.add_face_btn.clicked.connect(
            lambda: self._add_point("face")
        )

        self.computation_view.bands_panel.remove_last_btn.clicked.connect(
            self._remove_last_point
        )
        self.computation_view.bands_panel.clear_path_btn.clicked.connect(
            self._clear_path
        )

    def update_brillouin_zone(self):
        """
        Update the Brillouin zone visualization based on the current unit cell.

        This method is the core rendering function that:
        1. Clears any existing visualization
        2. Calculates the Brillouin zone vertices and faces
        3. Renders the BZ wireframe and key points (Gamma, vertices, edge midpoints, face centers)
        4. Updates UI controls based on the dimensionality of the BZ

        The method is triggered whenever the unit cell changes or a new unit cell is selected.
        """
        uc_id = self.selection.get("unit_cell")
        # Clear previous plot items except axes and grid
        for key, item in list(self.bz_plot_items.items()):
            self.bz_plot_view.view.removeItem(item)
            del self.bz_plot_items[key]
        # Reset BZ data, but not the path which is provided by the app controller
        self.bz_vertices = []
        self.bz_faces = []
        self.bz_point_selection = {"vertex": None, "edge": None, "face": None}
        self.bz_point_lists = {"vertex": [], "edge": [], "face": []}

        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.bz_path) >= 1
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.bz_path) >= 1
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.bz_path) >= 2
        )

        if uc_id == None:
            self.computation_view.bands_panel.add_gamma_btn.setEnabled(False)
            for btn in self.computation_view.bands_panel.vertex_btns:
                btn.setEnabled(False)
            for btn in self.computation_view.bands_panel.edge_btns:
                btn.setEnabled(False)
            for btn in self.computation_view.bands_panel.face_btns:
                btn.setEnabled(False)
            return
        else:
            self.unit_cell = self.unit_cells[uc_id]

        # Guard against 0-volume Brillouin zone: can occur in the process of creation of the unit cell or due to a mistake
        if self.unit_cell.volume() == 0:
            return

        self.bz_vertices, self.bz_faces = self.unit_cell.get_BZ()

        # Determine system dimensionality
        self.dim = (
            0 if len(self.bz_vertices) == 0 else len(self.bz_vertices[0])
        )

        # Draw the path
        self._update_path_visualization()

        # Activate/deactivate buttons based on dimensionality
        self.computation_view.bands_panel.add_gamma_btn.setEnabled(
            self.dim > 0
        )
        for btn in self.computation_view.bands_panel.vertex_btns:
            btn.setEnabled(self.dim > 0)
        for btn in self.computation_view.bands_panel.edge_btns:
            btn.setEnabled(self.dim > 1)
        for btn in self.computation_view.bands_panel.face_btns:
            btn.setEnabled(self.dim > 2)

        # Create the BZ wireframe by making edges (connect the vertices based on face data)
        self._create_bz_wireframe()

        # Extract vertices and faces from the BZ data
        # Note: In 2D, the faces are equivalent to edges. In 3D, the faces are polygons.
        self.bz_point_lists["vertex"] = np.array(self.bz_vertices)

        if self.dim == 2:
            # Get the edge points
            for edge in self.bz_faces:
                # Midpoint of the edge
                mid_point = np.mean(edge, axis=0)
                self.bz_point_lists["edge"].append(mid_point)
            self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"])

        elif self.dim == 3:
            unique_edges = set()
            edge_midpoints = []

            for face in self.bz_faces:
                for ii in range(len(face)):
                    next_ii = (ii + 1) % len(face)
                    v1 = tuple(face[ii])
                    v2 = tuple(face[next_ii])
                    edge = tuple(sorted((v1, v2)))
                    if edge not in unique_edges:
                        unique_edges.add(edge)
                        midpoint = 0.5 * (np.array(v1) + np.array(v2))
                        edge_midpoints.append(midpoint)

                # Face midpoint (no duplication issue here)
                face_mid = np.mean(face, axis=0)
                self.bz_point_lists["face"].append(face_mid)

            self.bz_point_lists["edge"] = np.array(edge_midpoints)
            self.bz_point_lists["face"] = np.array(self.bz_point_lists["face"])

        # Plot the BZ vertices as points
        # Add Gamma point at origin
        sphere = self._make_point()

        self.bz_plot_view.view.addItem(sphere)
        self.bz_plot_items["Gamma"] = sphere

        # Plot points for vertices, edges, and faces
        for typ, pt in self.bz_point_lists.items():
            if len(pt) > 0:
                pt_3d = self._pad_to_3d(pt)
                self.bz_point_selection[typ] = 0
                for ii, p in enumerate(pt_3d):
                    sphere = self._make_point()
                    sphere.translate(p[0], p[1], p[2])
                    self.bz_plot_view.view.addItem(sphere)
                    self.bz_plot_items[f"bz_{typ}_{ii}"] = sphere
                    # Highlight the first point
                    if ii == 0:
                        sphere.setColor(self.bz_plot_view.selected_point_color)

    def _create_bz_wireframe(self):
        """
        Create a wireframe visualization of the Brillouin zone.

        This method extracts edges from the Brillouin zone faces and creates a
        GLLinePlotItem to visualize them. The wireframe helps users understand
        the shape and boundaries of the Brillouin zone in reciprocal space.

        For 2D BZ, the wireframe is a polygon outline.
        For 3D BZ, the wireframe is the edges of the polyhedron.
        """
        if len(self.bz_faces) > 0:
            unique_edges = set()

            for face in self.bz_faces:
                for ii in range(len(face)):
                    next_ii = (ii + 1) % len(face)
                    v1 = tuple(face[ii])
                    v2 = tuple(face[next_ii])
                    edge = tuple(sorted((v1, v2)))
                    unique_edges.add(edge)

            # Convert edges to line vertices
            line_vertices = []
            for v1, v2 in unique_edges:
                line_vertices.extend([v1, v2])

            # Make sure all the line vertices are 3D
            line_vertices = self._pad_to_3d(line_vertices)

            # Create a GLLinePlotItem for all BZ edges
            bz_wireframe = gl.GLLinePlotItem(
                pos=np.array(line_vertices),
                color=(1, 1, 1, 0.8),
                width=1,
                mode="lines",
            )
            self.bz_plot_view.view.addItem(bz_wireframe)
            self.bz_plot_items["bz_wireframe"] = bz_wireframe

    def _make_point(self, vertex_size=0.20):
        """Create a sphere mesh item for a point in the BZ."""
        return gl.GLMeshItem(
            meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=vertex_size),
            smooth=True,
            color=self.bz_plot_view.point_color,
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

    def _select_point(self, step, typ):
        """
        Select a point in the Brillouin zone based on its type and step direction.

        This method implements the navigation through different types of points in the BZ
        (vertices, edge midpoints, or face centers). It updates the visual highlighting
        to show which point is currently selected, and maintains the selection state.

        Args:
            step: Direction to move in the selection (+1 for next, -1 for previous)
            typ: Type of point to select ('vertex', 'edge', or 'face')
        """
        # Guard against empty vertex list
        if len(self.bz_point_lists[typ]) == 0:
            return

        prev_point = self.bz_point_selection[typ]
        # Update the selection index
        if prev_point is None:
            self.bz_point_selection[typ] = 0
        else:
            self.bz_point_selection[typ] = (prev_point + step) % len(
                self.bz_point_lists[typ]
            )
            prev_key = f"bz_{typ}_{prev_point}"
            self.bz_plot_items[prev_key].setColor(
                self.bz_plot_view.point_color
            )

        new_key = f"bz_{typ}_{self.bz_point_selection[typ]}"
        self.bz_plot_items[new_key].setColor(
            self.bz_plot_view.selected_point_color
        )

    def _clear_path(self):
        """Remove all points from the path."""
        self.bz_path.clear()
        # Remove path from the plot if it exists
        if "bz_path" in self.bz_plot_items:
            self.bz_plot_view.view.removeItem(self.bz_plot_items["bz_path"])
            del self.bz_plot_items["bz_path"]

        # Disable the control buttons since the path is empty
        self.computation_view.bands_panel.remove_last_btn.setEnabled(False)
        self.computation_view.bands_panel.clear_path_btn.setEnabled(False)
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(False)

    def _update_path_visualization(self):
        """
        Update the visualization of the BZ path based on current path points.

        This method creates or updates the visual representation of the k-path in
        the Brillouin zone. The path is shown as a series of connected line segments
        between the selected k-points. The visualization helps users understand
        the path along which the band structure will be calculated.

        If the path has fewer than 2 points, no visualization is created.
        """
        # Remove existing path visualization if it exists
        if "bz_path" in self.bz_plot_items:
            self.bz_plot_view.view.removeItem(self.bz_plot_items["bz_path"])
            del self.bz_plot_items["bz_path"]
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
        self.bz_plot_view.view.addItem(path_object)
        self.bz_plot_items["bz_path"] = path_object

    def _add_point(self, point):
        """
        Add a selected point to the Brillouin zone path.

        This method adds the currently selected point (of the specified type) to the
        Brillouin zone path. The path is a sequence of k-points that will be used
        for band structure calculations. Points can be the origin (Gamma), vertices,
        edge midpoints, or face centers depending on the dimensionality of the BZ.

        After adding a point, the path visualization is updated and the relevant
        UI controls are enabled/disabled based on the new path state.

        Args:
            point: The type of point to add ("gamma", "vertex", "edge", or "face")
        """

        # Get the point's coordinate

        # if point == "gamma":
        #     coord = np.array([0] * self.dim)
        # else:
        #     if (
        #         self.bz_point_selection[point] is not None
        #         and self.bz_point_lists[point] is not None
        #     ):
        #          coord = self.bz_point_lists[point][self.bz_point_selection[point]]

        #     else:
        #         print("No point selected")
        #         return
        # # Add the points if it is different from the last point

        # if len(self.bz_path) == 0 or not any(self.bz_path[-1] - coord):
        #     self.bz_path.append(coord)

        if point == "gamma":
            self.bz_path.append(np.array([0] * self.dim))
        else:
            if (
                self.bz_point_selection[point] is not None
                and self.bz_point_lists[point] is not None
            ):
                self.bz_path.append(
                    self.bz_point_lists[point][self.bz_point_selection[point]]
                )
            else:
                print("No point selected")
                return
        # Enable the remove last button and clear path button now that we have points
        self.computation_view.bands_panel.remove_last_btn.setEnabled(True)
        self.computation_view.bands_panel.clear_path_btn.setEnabled(True)
        # Enable the compute bands button if we have at least 2 points
        if len(self.bz_path) >= 2:
            self.computation_view.bands_panel.compute_bands_btn.setEnabled(
                True
            )
        else:
            self.computation_view.bands_panel.compute_bands_btn.setEnabled(
                False
            )

        # Update the path visualization
        self._update_path_visualization()

    def _remove_last_point(self):
        """Remove the last point added to the path."""
        if self.bz_path:
            # Remove the last point
            self.bz_path.pop()

            # Update path visualization
            self._update_path_visualization()

            # Disable button if path is now empty
            if not self.bz_path:
                self.computation_view.bands_panel.remove_last_btn.setEnabled(
                    False
                )
                self.computation_view.bands_panel.clear_path_btn.setEnabled(
                    False
                )
            # Enable the compute bands button if we have at least 2 points
            if len(self.bz_path) >= 2:
                self.computation_view.bands_panel.compute_bands_btn.setEnabled(
                    True
                )
            else:
                self.computation_view.bands_panel.compute_bands_btn.setEnabled(
                    False
                )
