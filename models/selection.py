from PySide6.QtCore import QObject, Signal


class Selection(QObject):
    """
    Currently selected item.

    The item is characterized by a series of uuid.UUID's.

    Attributes
    ----------
    unit_cell : uuid.UUID | None
        ID of the selected `UnitCell`
    site : uuid.UUID | None
        ID of the selected `Site`
    state : uuid.UUID | None
        ID of the selected `State`

    Methods
    -------
    set_selection(uc_id : uuid.UUID | None, site_id : uuid.UUID | None,\
          state_id : uuid.UUID | None)
       Update the selection and emit an appropriate signal.

    Signals
    -------
    unit_cell_updated
        Emitted when a new `UnitCell` is selected.
    site_updated
        Emitted when a new `Site` is selected.
    state_updated
        Emitted when a new `State` is selected.
    selection_changed
        Emitted when the selection changes, in addition
        to the specific signal.
    """

    unit_cell_updated = Signal()
    site_updated = Signal()
    state_updated = Signal()
    selection_changed = Signal()

    def __init__(self):
        """Initialize the Selection object."""
        super().__init__()

        self.unit_cell = None
        self.site = None
        self.state = None

    def set_selection(self, uc_id, site_id, state_id):
        """
        Update the selection and emit an appropriate signal.

        Parameters
        ----------
        uc_id : uuid.UUID | None
            New `UnitCell` id.
        site_id : uuid.UUID | None
            New `Site` id.
        state_id : uuid.UUID | None
            New `State` id.
        """
        current_uc = self.unit_cell
        current_site = self.site
        current_state = self.state

        self.unit_cell = uc_id
        self.site = site_id
        self.state = state_id

        if current_uc != uc_id:
            self.unit_cell_updated.emit()
            self.selection_changed.emit()
        elif current_site != site_id:
            self.site_updated.emit()
            self.selection_changed.emit()
        elif current_state != state_id:
            self.state_updated.emit()
            self.selection_changed.emit()
