import uuid
from PySide6.QtCore import QObject
from src.tibitypes import UnitCell
from models.data_models import DataModel
from views.bz_plot_view import BrillouinZonePlotView
import pyqtgraph.opengl as gl

import numpy as np


class BrillouinZonePlotController(QObject):

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        unit_cell_data: DataModel,
        bz_plot_view: BrillouinZonePlotView,
    ):
        super().__init__()

        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_data = unit_cell_data
        self.bz_plot_view = bz_plot_view

        # Internal controller state
        self.unit_cell = None
        self.bz_plot_items = {}  # Dictionary to store plot items
        self.bz_vertices = []
        self.bz_faces = []
        self.dim = 0
        self.bz_point_selection = {"vertex": None, "edge": None, "face": None}

        # Flag to prevent redundant redraws during cascading signal updates
        self._updating = False

        # Connect Signals
        # Signals to redraw the plot due to selections change/unit cell and site updates
        self.selection.signals.updated.connect(self._update_schedule)
        self.unit_cell_data.signals.updated.connect(self._update_schedule)

        #     self.prev_vertex_btn.clicked.connect(lambda: self._select_point(-1, "vertex"))
        #     self.next_vertex_btn.clicked.connect(lambda: self._select_point(+1, "vertex"))
        #     self.add_vertex_btn.clicked.connect(lambda: self._add_point("vertex"))
        #     self.prev_edge_btn.clicked.connect(lambda: self._select_point(-1, "edge"))
        #     self.next_edge_btn.clicked.connect(lambda: self._select_point(+1, "edge"))
        #     self.add_edge_btn.clicked.connect(lambda: self._add_point("edge"))

    #     self.prev_face_btn.clicked.connect(lambda: self._select_point(-1, "face"))
    #     self.next_face_btn.clicked.connect(lambda: self._select_point(+1, "face"))
    #     self.add_face_btn.clicked.connect(lambda: self._add_point("face"))

    # self.remove_last_btn.clicked.connect(self._remove_last_point)
    # self.clear_path_btn.clicked.connect(self._clear_path)

    def _update_schedule(self):
        if self._updating:
            return
        self._updating = True
        # Schedule the update to happen after all signals are processed
        self.set_brillouin_zone()
        self._updating = False

    def set_brillouin_zone(self):

        uc_id = self.selection.get("unit_cell")
        # Clear previous plot items except axes and grid
        for key, item in list(self.bz_plot_items.items()):
            self.bz_plot_view.view.removeItem(item)
            del self.bz_plot_items[key]

        self.unit_cell = self.unit_cells[uc_id]
        self.bz_vertices = []
        self.bz_faces = []
        self.bz_point_selection = {"vertex": None, "edge": None, "face": None}

        self.bz_plot_view.remove_last_btn.setEnabled(False)
        self.bz_plot_view.clear_path_btn.setEnabled(False)
        self.bz_plot_view.compute_bands_btn.setEnabled(False)

        if uc_id == None:
            return

        self.bz_vertices, self.bz_faces = self.unit_cell.get_BZ()

        # Determine system dimensionality
        self.dim = 0 if len(self.bz_vertices) == 0 else len(self.bz_vertices[0])

        # Activate/deactivate buttons based on dimensionality
        self.bz_plot_view.add_gamma_btn.setEnabled(self.dim > 0)
        for btn in self.bz_plot_view.vertex_btns:
            btn.setEnabled(self.dim > 0)
        for btn in self.bz_plot_view.edge_btns:
            btn.setEnabled(self.dim > 1)
        for btn in self.bz_plot_view.face_btns:
            btn.setEnabled(self.dim > 2)
        pass

        # Create the BZ wireframe by making edges (connect the vertices based on face data)

        self._create_bz_wireframe()

    #     # Extract vertices and faces from the BZ data
    #     # Note: In 2D, the faces are equivalent to edges. In 3D, the faces are polygons.
    #     self.bz_point_lists["vertex"] = np.array(bz["bz_vertices"])

    #     if self.dim == 2:
    #         # Get the edge points
    #         self.bz_point_lists["edge"] = []
    #         for edge in bz["bz_faces"]:
    #             # Midpoint of the edge
    #             mid_point = np.mean(edge, axis=0)
    #             self.bz_point_lists["edge"].append(mid_point)
    #         self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"])

    #     elif self.dim == 3:
    #         # Get the edge and face points
    #         self.bz_point_lists["edge"] = []
    #         self.bz_point_lists["face"] = []
    #         for face in bz["bz_faces"]:
    #             for ii in range(len(face)):
    #                 next_ii = (ii + 1) % len(face)
    #                 # Midpoint of the edge
    #                 mid_point = np.mean([face[ii], face[next_ii]], axis=0)
    #                 self.bz_point_lists["edge"].append(mid_point)

    #             # Midpoint of the face
    #             mid_point = np.mean(face, axis=0)
    #             self.bz_point_lists["face"].append(mid_point)
    #         self.bz_point_lists["edge"] = np.array(self.bz_point_lists["edge"])
    #         self.bz_point_lists["face"] = np.array(self.bz_point_lists["face"])

    #     # Plot the BZ vertices as points
    #     # Add Gamma point at origin
    #     sphere = self._make_point()
    #     self.view.addItem(sphere)
    #     self.plot_items["Gamma"] = sphere

    #     # Plot points for vertices, edges, and faces
    #     for typ, pt in self.bz_point_lists.items():
    #         if len(pt) > 0:
    #             pt_3d = self._pad_to_3d(pt)
    #             self.selection[typ] = 0
    #             for ii, p in enumerate(pt_3d):
    #                 sphere = self._make_point()
    #                 sphere.translate(p[0], p[1], p[2])
    #                 self.view.addItem(sphere)
    #                 self.plot_items[f"bz_{typ}_{ii}"] = sphere
    #                 # Highlight the first point
    #                 if ii == 0:
    #                     sphere.setColor(self.selected_point_color)

    def _create_bz_wireframe(self):
        if len(self.bz_faces) > 0:
            # Process faces to extract unique edges
            all_edges = []
            for face in self.bz_faces:
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


# def _clear_path(self):
#     """Remove all points from the path."""
#     self.bz_path = []
#     # Remove path from the plot if it exists
#     if "bz_path" in self.plot_items:
#         self.view.removeItem(self.plot_items["bz_path"])
#         del self.plot_items["bz_path"]

#     # Disable the control buttons since the path is empty
#     self.remove_last_btn.setEnabled(False)
#     self.clear_path_btn.setEnabled(False)
#     self.compute_bands_btn.setEnabled(False)

# def _update_path_visualization(self):
#     """
#     Update the visualization of the BZ path based on current path points.
#     """
#     # Remove existing path visualization if it exists
#     if "bz_path" in self.plot_items:
#         try:
#             self.view.removeItem(self.plot_items["bz_path"])
#             del self.plot_items["bz_path"]
#         except Exception as e:
#             print(f"Error removing path visualization: {e}")

#     # Only create visualization if we have at least 2 points
#     if not self.bz_path or len(self.bz_path) < 2:
#         return

#     # Convert path points to 3D if needed
#     path_3d = self._pad_to_3d(self.bz_path)

#     # Create line segments for the path
#     path_pos = []
#     for ii in range(len(path_3d) - 1):
#         # Add both points of each segment
#         path_pos.extend([path_3d[ii], path_3d[ii + 1]])

#     # Create the path visualization
#     path_object = gl.GLLinePlotItem(
#         pos=np.array(path_pos), color=CF_red, width=5, mode="lines"
#     )
#     self.view.addItem(path_object)
#     self.plot_items["bz_path"] = path_object

# def _select_point(self, step, typ):

#     # Guard against empty vertex list
#     if len(self.bz_point_lists[typ]) == 0:
#         return

#     prev_point = self.selection[typ]

#     if prev_point is None:
#         self.selection[typ] = 0
#     else:
#         self.selection[typ] = (prev_point + step) % len(self.bz_point_lists[typ])

#     try:
#         # Skip deselection if previous vertex wasn't valid
#         if prev_point is not None and prev_point != self.selection[typ]:
#             # Only try to deselect if the key exists
#             prev_key = f"bz_{typ}_{prev_point}"
#             if prev_key in self.plot_items:
#                 self.plot_items[prev_key].setColor(self.point_color)

#         # Only try to select if the key exists
#         new_key = f"bz_{typ}_{self.selection[typ]}"
#         if new_key in self.plot_items:
#             # Select the new vertex
#             self.plot_items[new_key].setColor(self.selected_point_color)
#     except Exception as e:
#         print(f"Error selecting {typ}: {e}")

# def _add_point(self, point):
#     """
#     Add a selected point to the Brillouin zone path.

#     Args:
#         point: The type of point to add ("gamma", "vertex", "edge", or "face")
#     """

#     if point == "gamma":
#         self.bz_path.append([0] * self.dim)
#     else:
#         if (
#             self.selection[point] is not None
#             and self.bz_point_lists[point] is not None
#         ):
#             if len(self.bz_point_lists[point]) > self.selection[point]:
#                 self.bz_path.append(
#                     self.bz_point_lists[point][self.selection[point]]
#                 )
#             else:
#                 print(f"Invalid point index: {self.selection[point]}")
#                 return
#         else:
#             print("No point selected")
#             return
#     # Enable the remove last button and clear path button now that we have points
#     self.remove_last_btn.setEnabled(True)
#     self.clear_path_btn.setEnabled(True)
#     # Enable the compute bands button if we have at least 2 points
#     if len(self.bz_path) >= 2:
#         self.compute_bands_btn.setEnabled(True)
#     else:
#         self.compute_bands_btn.setEnabled(False)

#     # Update the path visualization
#     self._update_path_visualization()

# def _remove_last_point(self):
#     """Remove the last point added to the path."""
#     if self.bz_path:
#         # Remove the last point
#         self.bz_path.pop()

#         # Update path visualization
#         self._update_path_visualization()

#         # Disable button if path is now empty
#         if not self.bz_path:
#             self.remove_last_btn.setEnabled(False)
#             self.clear_path_btn.setEnabled(False)
#         # Enable the compute bands button if we have at least 2 points
#         if len(self.bz_path) >= 2:
#             self.compute_bands_btn.setEnabled(True)
#         else:
#             self.compute_bands_btn.setEnabled(False)
