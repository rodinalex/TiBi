import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpinBox,
    QLabel,
)
from PySide6.QtCore import Signal, Qt, QSize
import pyqtgraph.opengl as gl
from ui.placeholder import PlaceholderWidget
from itertools import product


class BrillouinZonePlot(QWidget):
    """
    A 3D visualization panel for Unit Cells using PyQtGraph's OpenGL support.

    Displays a unit cell as a wireframe parallelepiped with sites (atoms) as spheres.
    The visualization supports rotation, zooming, and site selection. The coordinate
    system shows the unit cell basis vectors and a reference grid.
    """

    # Signals for interacting with other components
    site_selected = Signal(object)  # Emits site ID when a site is selected

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

        # Settings panel
        self.control_panel = QHBoxLayout()
        # View adjusting panel
        self.lattice_view_control = QVBoxLayout()
        self.lattice_view_control_label = QLabel("Number of unit cells to show")
        self.lattice_view_control_label.setAlignment(Qt.AlignCenter)
        self.lattice_view_control_spinners = QHBoxLayout()

        # Unit cell view number
        self.n1_spinner = QSpinBox()
        self.n2_spinner = QSpinBox()
        self.n3_spinner = QSpinBox()

        self.n1_spinner.valueChanged.connect(self._on_spinner_changed)
        self.n2_spinner.valueChanged.connect(self._on_spinner_changed)
        self.n3_spinner.valueChanged.connect(self._on_spinner_changed)

        for x in [self.n1_spinner, self.n2_spinner, self.n3_spinner]:
            x.setFixedWidth(40)
            x.setRange(1, 10)
            x.setEnabled(False)

        # Create row layouts with labels on the left and spin boxes on the right
        spinner1 = QHBoxLayout()
        spinner1.addWidget(QLabel("n<sub>1</sub>:"))
        spinner1.addWidget(self.n1_spinner)

        spinner2 = QHBoxLayout()
        spinner2.addWidget(QLabel("n<sub>2</sub>:"))
        spinner2.addWidget(self.n2_spinner)

        spinner3 = QHBoxLayout()
        spinner3.addWidget(QLabel("n<sub>3</sub>:"))
        spinner3.addWidget(self.n3_spinner)

        # Add spinners to the main form layout
        self.lattice_view_control_spinners.addLayout(spinner1)
        self.lattice_view_control_spinners.addLayout(spinner2)
        self.lattice_view_control_spinners.addLayout(spinner3)

        self.lattice_view_control.addWidget(self.lattice_view_control_label)
        self.lattice_view_control.addLayout(self.lattice_view_control_spinners)

        self.control_panel.addLayout(self.lattice_view_control, stretch=1)
        self.control_panel.addWidget(PlaceholderWidget("TEST"), stretch=3)

        layout.addWidget(self.view, stretch=5)
        layout.addLayout(self.control_panel, stretch=1)

    def set_unit_cell(self, unit_cell):
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
        self.unit_cell = unit_cell
        # Clear previous plot items except axes and grid
        for key, item in list(self.plot_items.items()):
            self.view.removeItem(item)
            del self.plot_items[key]

        if not unit_cell:
            return

        # Check which vectors of the unit cell are periodic and activate the UC spinners if they are
        if self.unit_cell.v1.is_periodic == True:
            self.n1_spinner.setEnabled(True)
        else:
            self.n1_spinner.setEnabled(False)

        if self.unit_cell.v2.is_periodic == True:
            self.n2_spinner.setEnabled(True)
        else:
            self.n2_spinner.setEnabled(False)

        if self.unit_cell.v3.is_periodic == True:
            self.n3_spinner.setEnabled(True)
        else:
            self.n3_spinner.setEnabled(False)

        # Plot unit cell wireframe
        repeats = [
            spinner.value() if spinner.isEnabled() else 1
            for spinner in (self.n1_spinner, self.n2_spinner, self.n3_spinner)
        ]
        n1, n2, n3 = repeats

        # Collect line vertices
        line_vertices = []
        for jj, kk, ll in product(range(n1), range(n2), range(n3)):
            line_vertices.extend(self._get_unit_cell_edges(jj, kk, ll))
            self._plot_sites(jj, kk, ll)

        # Create the wireframe using GLLinePlotItem
        unit_cell_edges = gl.GLLinePlotItem(
            pos=line_vertices, color="w", width=2, mode="lines"  # White color
        )
        self.view.addItem(unit_cell_edges)
        self.plot_items["unit_cell_edges"] = unit_cell_edges

        # Plot the new unit cell
        # self._plot_sites(0, 0, 0)

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
        v1 = np.array([self.unit_cell.v1.x, self.unit_cell.v1.y, self.unit_cell.v1.z])
        v2 = np.array([self.unit_cell.v2.x, self.unit_cell.v2.y, self.unit_cell.v2.z])
        v3 = np.array([self.unit_cell.v3.x, self.unit_cell.v3.y, self.unit_cell.v3.z])

        # Plot each site as a sphere
        for site_id, site in self.unit_cell.sites.items():
            # Calculate the position in Cartesian coordinates
            pos = (a1 + site.c1) * v1 + (a2 + site.c2) * v2 + (a3 + site.c3) * v3

            # Create a sphere for the site
            sphere = gl.GLMeshItem(
                meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=0.1),
                smooth=True,
                color=self.site_color,
                shader="shaded",
            )
            sphere.translate(pos[0], pos[1], pos[2])

            # Store site ID as user data for interaction
            sphere.site_id = site_id

            self.view.addItem(sphere)
            self.plot_items[f"site_{site_id}_{a1}_{a2}_{a3}"] = sphere

    def select_site(self, site_id):
        """
        Highlight a selected site by changing its color.

        This method is called when a site is selected, either from clicking on it
        in the 3D view or from selecting it in the tree view. It changes the color
        of the selected site to make it stand out and resets any previously selected
        site back to the default color.

        Args:
            site_id: The UUID of the site to highlight, or None to deselect all sites
        """
        # Reset previously selected site to default color
        if self.selected_site:
            prev_sphere = self.plot_items.get(f"site_{self.selected_site}")
            if prev_sphere:
                prev_sphere.setColor(self.site_color)

        # Highlight new selected site with the highlight color
        self.selected_site = site_id
        if site_id:
            sphere = self.plot_items.get(f"site_{site_id}")
            if sphere:
                sphere.setColor(self.selected_site_color)

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

        self.set_unit_cell(self.unit_cell)

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
