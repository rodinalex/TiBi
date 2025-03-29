import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QColorDialog
from PySide6.QtCore import Signal, Qt, QSize
import pyqtgraph as pg
import pyqtgraph.opengl as gl


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
        self.axis_colors = [
            (213 / 255, 94 / 255, 0, 1),
            (0, 158 / 255, 115 / 255, 1),
            (0, 114 / 255, 178 / 255, 1),
        ]  # R, G, B for x, y, z
        self.cell_color = (0.8, 0.8, 0.8, 0.3)  # Light gray, semi-transparent
        self.site_color = (86 / 255, 180 / 255, 233 / 255, 0.8)
        self.selected_site_color = (
            240 / 255,
            228 / 255,
            66 / 255,
            1,
        )

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create 3D plot widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=8)
        self.view.setBackgroundColor("k")  # Black background

        # Initialize grid and axes for reference
        grid = gl.GLGridItem()
        grid.setSize(10, 10, 1)
        grid.setSpacing(1, 1, 1)
        self.view.addItem(grid)

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

    def set_unit_cell(self, unit_cell):
        """Set or update the unit cell to be displayed."""
        self.unit_cell = unit_cell
        # Clear previous plot items except axes and grid
        for key, item in list(self.plot_items.items()):
            self.view.removeItem(item)
            del self.plot_items[key]

        if not unit_cell:
            return

        # Plot the new unit cell
        self._plot_unit_cell()
        self._plot_sites()

        # Update the axes to match unit cell basis vectors
        self._update_axes()

    def _update_axes(self):
        """Update the coordinate axes to match the unit cell basis vectors."""
        if not self.unit_cell:
            return

        # Scale factor to make axes visible
        scale = 2.0

        # Update each axis to represent a basis vector
        vectors = [self.unit_cell.v1, self.unit_cell.v2, self.unit_cell.v3]

        for ii, vector in enumerate(vectors):

            axis_pos = np.array(
                [[0, 0, 0], [vector.x * scale, vector.y * scale, vector.z * scale]]
            )
            axis = gl.GLLinePlotItem(
                pos=axis_pos, color=(0.8, 0.8, 0.8, 0.3), width=3, antialias=True
            )

            self.view.addItem(axis)
            self.plot_items[f"axis_{ii}"] = axis

    def _plot_unit_cell(self):
        """Plot the unit cell parallelepiped."""
        if not self.unit_cell:
            return

        # Extract basis vectors
        v1 = np.array([self.unit_cell.v1.x, self.unit_cell.v1.y, self.unit_cell.v1.z])
        v2 = np.array([self.unit_cell.v2.x, self.unit_cell.v2.y, self.unit_cell.v2.z])
        v3 = np.array([self.unit_cell.v3.x, self.unit_cell.v3.y, self.unit_cell.v3.z])

        # Define the 8 corners of the parallelepiped
        verts = np.array(
            [
                [0, 0, 0],
                v1,
                v2,
                v1 + v2,  # Bottom 4 vertices
                v3,
                v1 + v3,
                v2 + v3,
                v1 + v2 + v3,  # Top 4 vertices
            ]
        )

        # Define the 12 edges of the parallelepiped
        edges = np.array(
            [
                [0, 1],
                [0, 2],
                [1, 3],
                [2, 3],  # Bottom square
                [4, 5],
                [4, 6],
                [5, 7],
                [6, 7],  # Top square
                [0, 4],
                [1, 5],
                [2, 6],
                [3, 7],  # Vertical edges
            ]
        )
        # Convert edges into line segments
        line_vertices = []
        for edge in edges:
            line_vertices.append(verts[edge[0]])
            line_vertices.append(verts[edge[1]])

        # Convert to NumPy array
        line_vertices = np.array(line_vertices)

        # Create the wireframe using GLLinePlotItem
        unit_cell_edges = gl.GLLinePlotItem(
            pos=line_vertices, color="w", width=2, mode="lines"  # White color
        )
        self.view.addItem(unit_cell_edges)
        self.plot_items["unit_cell_edges"] = unit_cell_edges

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
                meshdata=gl.MeshData.sphere(rows=40, cols=40, radius=0.1),
                smooth=True,
                color=self.site_color,
                shader="shaded",
            )
            sphere.translate(pos[0], pos[1], pos[2])

            # Store site ID as user data for interaction
            sphere.site_id = site_id

            self.view.addItem(sphere)
            self.plot_items[f"site_{site_id}"] = sphere

    def select_site(self, site_id):
        """Highlight a selected site."""
        # Reset previously selected site
        if self.selected_site:
            prev_sphere = self.plot_items.get(f"site_{self.selected_site}")
            if prev_sphere:
                prev_sphere.setColor(self.site_color)

        # Highlight new selected site
        self.selected_site = site_id
        if site_id:
            sphere = self.plot_items.get(f"site_{site_id}")
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
