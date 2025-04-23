import uuid
from PySide6.QtCore import QObject
from src.tibitypes import UnitCell
from models.data_models import DataModel
from itertools import product
from views.uc_plot_view import UnitCellPlotView
import pyqtgraph.opengl as gl

import numpy as np


class UnitCellPlotController(QObject):

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        unit_cell_data: DataModel,
        site_data: DataModel,
        uc_plot_view: UnitCellPlotView,
    ):
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.unit_cell_data = unit_cell_data
        self.site_data = site_data
        self.uc_plot_view = uc_plot_view

        # Internal controller state
        self.unit_cell = None
        self.uc_plot_items = {}  # Dictionary to store plot items

        # Flag to prevent redundant redraws during cascading signal updates
        self._updating = False

        # Connect Signals
        # Signals to redraw the plot due to selections change/unit cell and site updates
        self.selection.signals.updated.connect(self._update_schedule)
        self.unit_cell_data.signals.updated.connect(self._update_schedule)
        self.site_data.signals.updated.connect(self._update_schedule)

        # Signals to update the plot when the spinners are changed
        self.uc_plot_view.n1_spinner.valueChanged.connect(self.set_unit_cell)
        self.uc_plot_view.n2_spinner.valueChanged.connect(self.set_unit_cell)
        self.uc_plot_view.n3_spinner.valueChanged.connect(self.set_unit_cell)

    def _update_schedule(self):
        if self._updating:
            return
        self._updating = True
        # Schedule the update to happen after all signals are processed
        self.set_unit_cell()
        self._updating = False

    def set_unit_cell(self):
        """
        Set or update the unit cell to be displayed in the 3D view.

        This method handles the complete process of updating the visualization:
        1. Stores the new unit cell reference
        2. Clears existing visualization elements
        3. Creates new visualization elements for the unit cell and its sites
        4. Updates the coordinate axes to match the unit cell basis vectors

        Args:
            unit_cell: The UnitCell object to display, or None to clear the view
        """
        uc_id = self.selection.get("unit_cell")
        # Clear previous plot items except axes and grid
        for key, item in list(self.uc_plot_items.items()):
            self.uc_plot_view.view.removeItem(item)
            del self.uc_plot_items[key]

        if uc_id == None:
            return
        self.unit_cell = self.unit_cells[uc_id]
        # Check which vectors of the unit cell are periodic and activate the UC spinners if they are
        if self.unit_cell.v1.is_periodic == True:
            self.uc_plot_view.n1_spinner.setEnabled(True)
        else:
            self.uc_plot_view.n1_spinner.setEnabled(False)

        if self.unit_cell.v2.is_periodic == True:
            self.uc_plot_view.n2_spinner.setEnabled(True)
        else:
            self.uc_plot_view.n2_spinner.setEnabled(False)

        if self.unit_cell.v3.is_periodic == True:
            self.uc_plot_view.n3_spinner.setEnabled(True)
        else:
            self.uc_plot_view.n3_spinner.setEnabled(False)

        # Plot unit cell wireframe
        repeats = [
            spinner.value() if spinner.isEnabled() else 1
            for spinner in (
                self.uc_plot_view.n1_spinner,
                self.uc_plot_view.n2_spinner,
                self.uc_plot_view.n3_spinner,
            )
        ]
        self.n1, self.n2, self.n3 = repeats

        # Collect line vertices
        line_vertices = []
        for jj, kk, ll in product(range(self.n1), range(self.n2), range(self.n3)):
            line_vertices.extend(self._get_unit_cell_edges(jj, kk, ll))
            self._plot_sites(jj, kk, ll)

        # Create the wireframe using GLLinePlotItem
        unit_cell_edges = gl.GLLinePlotItem(
            pos=line_vertices, color="w", width=1, mode="lines"  # White color
        )

        # Shift the unit cells so that they are centered aroudn the origin
        shift = (
            -(
                self.n1 * self.unit_cell.v1.as_array()
                + self.n2 * self.unit_cell.v2.as_array()
                + self.n3 * self.unit_cell.v3.as_array()
            )
            / 2
        )
        unit_cell_edges.translate(shift[0], shift[1], shift[2])
        self.uc_plot_view.view.addItem(unit_cell_edges)
        self.uc_plot_items["unit_cell_edges"] = unit_cell_edges

    def _plot_sites(self, a1, a2, a3):
        """
        Plot all sites (atoms) within the unit cell as spheres.

        Each site is represented as a colored sphere positioned according to
        its fractional coordinates within the unit cell. Sites can be selected
        and will change color when highlighted. Each sphere stores a reference
        to its corresponding site ID for interaction.
        """
        if not self.unit_cell or not self.unit_cell.sites:
            return

        # Extract basis vectors
        v1 = self.unit_cell.v1.as_array()
        v2 = self.unit_cell.v2.as_array()
        v3 = self.unit_cell.v3.as_array()

        # Plot each site as a sphere
        for site_id, site in self.unit_cell.sites.items():
            # Calculate the position in Cartesian coordinates
            pos = (a1 + site.c1) * v1 + (a2 + site.c2) * v2 + (a3 + site.c3) * v3
            sphere_color = (
                self.uc_plot_view.selected_site_color
                if site_id == self.selection["site"]
                else self.uc_plot_view.site_color
            )
            # Create a sphere for the site
            sphere = gl.GLMeshItem(
                meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=0.1),
                smooth=True,
                color=sphere_color,
                shader="shaded",
            )

            shift = -(self.n1 * v1 + self.n2 * v2 + self.n3 * v3) / 2 + pos
            sphere.translate(shift[0], shift[1], shift[2])

            # Store site ID as user data for interaction
            sphere.site_id = site_id

            self.uc_plot_view.view.addItem(sphere)
            self.uc_plot_items[f"site_{site_id}_{a1}_{a2}_{a3}"] = sphere

    def _get_unit_cell_edges(self, a1, a2, a3):
        """
        Plot the unit cell as a wireframe parallelepiped.

        Creates a 3D wireframe representation of the unit cell using the three
        basis vectors to define the shape. The parallelepiped is drawn as a set
        of 12 lines connecting 8 vertices in 3D space.
        """
        if not self.unit_cell:
            return

        # Extract basis vectors
        v1 = self.unit_cell.v1.as_array()
        v2 = self.unit_cell.v2.as_array()
        v3 = self.unit_cell.v3.as_array()

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
        verts = [v + (a1 * v1 + a2 * v2 + a3 * v3) for v in verts]
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

        return line_vertices

    def _on_spinner_changed(self):
        self.set_unit_cell()
