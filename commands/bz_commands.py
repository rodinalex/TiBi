from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtGui import QUndoCommand

from src.tibitypes import UnitCell
from views.computation_view import ComputationView


# Tree Commands
class AddBZPointCommand(QUndoCommand):
    """
    Add a point to the special points path in the Brillouin zone.

    Attributes
    ----------
    unit_cell : UnitCell
        `UnitCell` to which the point will be addeed
    point : NDArray
        The point to be added
    computation_view : ComputationView
        UI object containing the computation view
    signal : Signal
        Signal to be emitted to trigger a redraw of the BZ path
    """

    def __init__(
        self,
        unit_cell: UnitCell,
        point: NDArray,
        computation_view: ComputationView,
        signal: Signal,
    ):
        """
        Initialize the AddBZPointCommand.

        Parameters
        ----------
        unit_cell : UnitCell
            `UnitCell` to which the point will be addeed
        point : NDArray
            The point to be added
        computation_view : ComputationView
            UI object containing the computation view
        signal : Signal
            Signal to be emitted to trigger a redraw of the BZ path
        """
        super().__init__("Add BZ Path Point")
        self.unit_cell = unit_cell
        self.point = point
        self.computation_view = computation_view
        self.signal = signal

    def redo(self):
        self.unit_cell.bandstructure.special_points.append(self.point)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()

    def undo(self):
        self.unit_cell.bandstructure.special_points.pop(-1)
        self.computation_view.bands_panel.remove_last_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.clear_path_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 0
        )
        self.computation_view.bands_panel.compute_bands_btn.setEnabled(
            len(self.unit_cell.bandstructure.special_points) > 1
        )
        self.signal.emit()


# # Tree Commands
# class RemoveBZPointCommand(QUndoCommand):
#     """
#     Create a new unit cell with default properties and add it to the model.

#     Creates a unit cell with orthogonal basis vectors along
#     the x, y, and z axes, adds it to the unit_cells dictionary
#     and to the tree view.

#     The default unit cell has:
#     - Name: "New Unit Cell"
#     - Three orthogonal unit vectors along the x, y, and z axes
#     - No periodicity (0D system)
#     - No sites or states initially

#     Attributes
#     ----------
#     unit_cells : dict[uuid.UUID, UnitCell]
#         Dictionary mapping UUIDs to `UnitCell` objects
#     tree_view : SystemTree
#         UI object containing the tree view
#     unit_cell : UnitCell
#         Newly created `UnitCell`
#     """

#     def __init__(
#         self, unit_cells: dict[uuid.UUID, UnitCell], tree_view: SystemTree
#     ):
#         """
#         Initialize the AddUnitCellCommand.

#         Parameters
#         ----------
#         unit_cells : dict[uuid.UUID, UnitCell]
#             Dictionary mapping UUIDs to `UnitCell` objects
#         tree_view : SystemTree
#             UI object containing the tree view
#         """
#         super().__init__("Add Unit Cell")
#         self.unit_cells = unit_cells
#         self.tree_view = tree_view
#         self.unit_cell = mk_new_unit_cell()

#     # Add the newly-created unit cell to the dictionary and create a tree item
#     def redo(self):
#         self.unit_cells[self.unit_cell.id] = self.unit_cell
#         self.tree_view.add_tree_item(self.unit_cell.name, self.unit_cell.id)

#     # Remove the unit cell from the dictionary and the tree using its id
#     def undo(self):
#         del self.unit_cells[self.unit_cell.id]
#         self.tree_view.remove_tree_item(self.unit_cell.id)


# # Tree Commands
# class ClearBZPathCommand(QUndoCommand):
#     """
#     Create a new unit cell with default properties and add it to the model.

#     Creates a unit cell with orthogonal basis vectors along
#     the x, y, and z axes, adds it to the unit_cells dictionary
#     and to the tree view.

#     The default unit cell has:
#     - Name: "New Unit Cell"
#     - Three orthogonal unit vectors along the x, y, and z axes
#     - No periodicity (0D system)
#     - No sites or states initially

#     Attributes
#     ----------
#     unit_cells : dict[uuid.UUID, UnitCell]
#         Dictionary mapping UUIDs to `UnitCell` objects
#     tree_view : SystemTree
#         UI object containing the tree view
#     unit_cell : UnitCell
#         Newly created `UnitCell`
#     """

#     def __init__(
#         self, unit_cells: dict[uuid.UUID, UnitCell], tree_view: SystemTree
#     ):
#         """
#         Initialize the AddUnitCellCommand.

#         Parameters
#         ----------
#         unit_cells : dict[uuid.UUID, UnitCell]
#             Dictionary mapping UUIDs to `UnitCell` objects
#         tree_view : SystemTree
#             UI object containing the tree view
#         """
#         super().__init__("Add Unit Cell")
#         self.unit_cells = unit_cells
#         self.tree_view = tree_view
#         self.unit_cell = mk_new_unit_cell()

#     # Add the newly-created unit cell to the dictionary and create a tree item
#     def redo(self):
#         self.unit_cells[self.unit_cell.id] = self.unit_cell
#         self.tree_view.add_tree_item(self.unit_cell.name, self.unit_cell.id)

#     # Remove the unit cell from the dictionary and the tree using its id
#     def undo(self):
#         del self.unit_cells[self.unit_cell.id]
#         self.tree_view.remove_tree_item(self.unit_cell.id)
