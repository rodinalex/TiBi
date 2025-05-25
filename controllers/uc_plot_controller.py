from itertools import product
import numpy as np
from PySide6.QtCore import QObject
import pyqtgraph.opengl as gl
from typing import Tuple
import uuid

from models import DataModel, UnitCell
from ui.constants import CF_yellow, default_site_scaling
from views.uc_plot_view import UnitCellPlotView


class UnitCellPlotController(QObject):
    """
    Controller for the unit cell 3D visualization.

    This controller manages the 3D visualization of unit cells, handling the
    rendering of unit cell wireframes, site positions, and periodic
    repetitions. It observes changes to the selected unit cell and its
    properties, updating the visualization in response to any modifications.

    The controller provides functionality for:
    1. Visualizing the unit cell as a wireframe parallelepiped
    2. Displaying sites (atoms) as colored spheres
    3. Showing multiple periodic repetitions of the unit cell
    4. Highlighting selected sites

    The visualization updates reactively when the unit cell data changes
    or when the user adjusts the number of periodic repetitions via spinners.

    Attributes
    ----------
    unit_cells : dict[uuid.UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : DataModel
        Model tracking the currently selected unit cell, site, and state
    uc_plot_view : UnitCellPlotView
        The view component for the 3D visualization
    unit_cell : UnitCell
        The unit cell currently being visualized
    uc_plot_items : dict
        Dictionary to store plot items
    """

    def __init__(
        self,
        unit_cells: dict[uuid.UUID, UnitCell],
        selection: DataModel,
        uc_plot_view: UnitCellPlotView,
    ):
        """
        Initialize the unit cell plot controller.

        Parameters
        ----------
        unit_cells: dict[uuid.UUID, UnitCell]
            Dictionary mapping UUIDs to UnitCell objects
        selection: DataModel
            Model tracking the currently selected unit cell, site, and state
        uc_plot_view: UnitCellPlotView
            The view component for the 3D visualization
        """
        super().__init__()
        self.unit_cells = unit_cells
        self.selection = selection
        self.uc_plot_view = uc_plot_view

        # Internal controller state
        self.unit_cell = None  # Unit cell being plotted
        self.uc_plot_items = {}  # Dictionary to store plot items

    def update_unit_cell(self, wireframe_shown, n1, n2, n3):
        """
        Set or update the unit cell to be displayed in the 3D view.

        This method handles the complete process of updating the visualization:
        1. Stores the new unit cell reference
        2. Clears existing visualization elements
        3. Creates new visualization elements for the unit cell and its sites
        4. Updates the coordinate axes to match the unit cell basis vectors

        Parameters
        ----------
        wireframe_shown: bool
            Denotes whether the primitive vector wireframe is drawn
        n1, n2, n3: int
            Number of repetitions along the corresponding basis vector
        """
        uc_id = self.selection.get("unit_cell")
        # Clear previous plot items except axes
        for key, item in list(self.uc_plot_items.items()):
            self.uc_plot_view.view.removeItem(item)
            del self.uc_plot_items[key]

        if uc_id is None:
            return

        self.unit_cell = self.unit_cells[uc_id]
        self.n1, self.n2, self.n3 = n1, n2, n3

        # Collect line vertices
        unique_edges = (
            set()
        )  # Unique edges to avoid duplication from neighboring unit cells
        # Loop over the unit cell indices
        for jj, kk, ll in product(
            range(self.n1), range(self.n2), range(self.n3)
        ):
            # List of tuples with vertices defining edges
            edges = self._get_unit_cell_edges(jj, kk, ll)
            for edge in edges:
                unique_edges.add(edge)  # Keep only unique edges
            self._plot_sites(jj, kk, ll)

        # Convert edges to line vertices
        line_vertices = []
        for v1, v2 in unique_edges:
            line_vertices.extend([v1, v2])
        # Create the wireframe using GLLinePlotItem
        unit_cell_edges = gl.GLLinePlotItem(
            pos=line_vertices, color="w", width=1, mode="lines"  # White color
        )

        # Shift the unit cells so that they are centered around the origin
        shift = (
            -(
                self.n1 * self.unit_cell.v1.as_array()
                + self.n2 * self.unit_cell.v2.as_array()
                + self.n3 * self.unit_cell.v3.as_array()
            )
            / 2
        )

        unit_cell_edges.translate(shift[0], shift[1], shift[2])

        # Plot the wireframe if requested
        if wireframe_shown:
            self.uc_plot_view.view.addItem(unit_cell_edges)
            self.uc_plot_items["unit_cell_edges"] = unit_cell_edges

    def _plot_sites(self, a1, a2, a3):
        """
        Plot all `Site`s within the `UnitCell` at a1*v1 + a2*v2 + a3*v3.

        Each site is represented as a colored sphere positioned according to
        its fractional coordinates within the unit cell. Sites can be selected
        and change size when highlighted. Spheres also store the site id
        to draw the coupling links when pairs of states are selected from
        the hopping panel.

        Parameters
        ----------
        a1, a2, a3 : int
            Integer multiples of the unit cell basis vectors v1, v2, and v3.
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
            pos = (
                (a1 + site.c1) * v1 + (a2 + site.c2) * v2 + (a3 + site.c3) * v3
            )
            sphere_color = self.unit_cell.sites[site_id].color

            sphere_radius = (
                self.unit_cell.sites[site_id].R * default_site_scaling
                if site_id == self.selection.get("site")
                else self.unit_cell.sites[site_id].R
            )
            # Create a sphere for the site.
            sphere = gl.GLMeshItem(
                meshdata=gl.MeshData.sphere(
                    rows=10, cols=10, radius=sphere_radius
                ),
                smooth=True,
                color=(
                    sphere_color[0],
                    sphere_color[1],
                    sphere_color[2],
                    sphere_color[3],
                ),
                shader="shaded",
                glOptions="translucent",
            )
            # Shift the objects so that the illustration is centered
            # at the origin
            shift = -(self.n1 * v1 + self.n2 * v2 + self.n3 * v3) / 2 + pos
            sphere.translate(shift[0], shift[1], shift[2])

            # Store site ID as user data for interaction
            sphere.site_id = site_id

            self.uc_plot_view.view.addItem(sphere)
            self.uc_plot_items[f"site_{site_id}_{a1}_{a2}_{a3}"] = sphere

    def _get_unit_cell_edges(
        self, a1, a2, a3
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Get the edges of the unit cell parallelepiped.

        Parameters
        ----------
        a1, a2, a3 : int
            Integer multiples of the unit cell basis vectors v1, v2, and v3.

        Returns
        -------
        list[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]
            A list of edges in the unit cell parallelepiped.
            Each edge is represented as a tuple of two vertices.
            Each vertex is a tuple of three floats (x, y, z).
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
        vertex_tuples = []
        for edge in edges:
            V1 = tuple(verts[edge[0]])
            V2 = tuple(verts[edge[1]])
            vertex_tuples.append(tuple(sorted((V1, V2))))

        return vertex_tuples

    def update_hopping_segments(self, pair_selection):
        """
        Draw segments to indicate hopping connections.

        When a pair is selected from the hopping matrix, this function
        draws lines starting from the site hosting the source state
        inside the unit cell around (0,0,0) to all the sites hosting
        the target sites.

        Parameters
        ----------
        pair_selection : tuple
            A tuple of (site_name, site_id, state_name, state_id)
            representing the selected pair of states.
            The first element is the source state and the second
            element is the target state.
        """

        # Clear previous hopping segments
        hopping_segments = self.uc_plot_items.get("hopping_segments")
        if hopping_segments is not None:
            self.uc_plot_view.view.removeItem(hopping_segments)
            del self.uc_plot_items["hopping_segments"]

        # s1 and s2 are tuples (site_name, site_id, state_name, state_id)
        s1, s2 = pair_selection
        hoppings = self.unit_cell.hoppings.get((s1[3], s2[3]))
        if hoppings is None:
            return

        v1 = self.unit_cell.v1.as_array()
        v2 = self.unit_cell.v2.as_array()
        v3 = self.unit_cell.v3.as_array()

        # Get the location of the source site
        source = self.unit_cell.sites[s2[1]]
        source_pos = source.c1 * v1 + source.c2 * v2 + source.c3 * v3

        # Get the location of the target sites in the (0,0,0) unit cell
        target = self.unit_cell.sites[s1[1]]
        target_pos = target.c1 * v1 + target.c2 * v2 + target.c3 * v3

        segments = []
        for (d1, d2, d3), _ in hoppings:
            target = target_pos + d1 * v1 + d2 * v2 + d3 * v3
            segments.append(source_pos)
            segments.append(target)

        hopping_segments = gl.GLLinePlotItem(
            pos=segments,
            color=CF_yellow,
            width=5,
            mode="lines",
        )

        shift = (
            (self.n1 % 2) * v1 + (self.n2 % 2) * v2 + (self.n3 % 2) * v3
        ) / 2

        hopping_segments.translate(-shift[0], -shift[1], -shift[2])

        # Add to the view
        self.uc_plot_view.view.addItem(hopping_segments)
        # Store it so we can remove it later
        self.uc_plot_items["hopping_segments"] = hopping_segments
