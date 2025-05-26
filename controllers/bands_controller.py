from PySide6.QtCore import QObject, Signal

from views.panels import BandsPanel
from core.band_structure import diagonalize_hamitonian, interpolate_k_path


class BandsController(QObject):
    """
    Controller for the hopping parameter interface.

    This controller manages the creation and editing of hopping parameters
    (tight-binding matrix elements) between quantum states. It handles:

    1. The interactive matrix grid where each button represents a possible
       hopping between two states
    2. The detailed parameter table for editing specific hopping values
    3. The right-click context menu for performing operations like creating
       Hermitian partners

    The controller maintains the connection between the visual representation
    and the underlying data model, ensuring that changes in the UI are properly
    reflected in the unit cell's hopping parameters.

    Attributes
    ----------
    unit_cells : dict[UUID, UnitCell]
        Dictionary mapping UUIDs to UnitCell objects
    selection : DataModel
        Model tracking the current selection
    hopping_view : HoppingPanel
        The main view component
    undo_stack : QUndoStack
        `QUndoStack` to hold "undo-able" commands
    state_info : list[tuple]
        List of tuples containing state information \
            (site_name, site_id, state_name, state_id)\
            for each `State` in the `UnitCell`
    pair_selection : list[tuple]
        2-element list of tuples containing the selected state pair
    hoppings : dict[Tuple[uuid, uuid],\
            list[Tuple[int, int, int], np.complex128]]
        Dictionary containing the hopping parameters for the `UnitCell`

    Methods
    -------
    update_unit_cell()
        Updates the hopping data model with the `UnitCell`'s hoppings

    Signals
    -------
    btn_clicked
        Emitted when a button is clicked, carrying the source \
            and destination state info
    hoppings_changed
        Emitted by the command when couplings are modified
    hopping_segments_requested
        Emitted when the coupling table is updated, triggering an\
            update of hopping segments. The signal carries the\
            information about the selection.
    selection_requested
        Emitted when the selection change in the tree is required,\
            carrying the unit cell, site, and state IDs
    """

    bands_computed = Signal()

    def __init__(
        self,
        bands_panel: BandsPanel,
    ):
        super().__init__()
        self.bands_panel = bands_panel

        self.bands_panel.compute_bands_btn.clicked.connect(self._compute_bands)

    def _compute_bands(self):
        """
        Calculate the electronic band structure along a specified k-path.

        The path is defined by the special points in the Brillouin zone.
        """

        # Get the selected unit cell
        uc_id = self.models["selection"]["unit_cell"]
        unit_cell = self.unit_cells[uc_id]

        # Check if the coupling is Hermitian and only then calculate
        if not unit_cell.is_hermitian():
            self.status_updated.emit(
                "Computation halted: the system is non-Hermitian"
            )
            return

        num_points = self.computation_view.bands_panel.n_points_spinbox.value()

        # Get Hamiltonian function
        hamiltonian_func = unit_cell.get_hamiltonian_function()

        # Perform calculation
        k_path = interpolate_k_path(
            unit_cell.bandstructure.special_points, num_points
        )
        self.status_updated.emit("Computing the bands")

        eigenvalues, eigenvectors = diagonalize_hamitonian(
            hamiltonian_func, k_path
        )
        self.status_updated.emit("Bands computation complete")

        # Update the band structure
        unit_cell.bandstructure.eigenvalues = eigenvalues
        unit_cell.bandstructure.eigenvectors = eigenvectors
        unit_cell.bandstructure.path = k_path
        self.band_computation_completed.emit()
