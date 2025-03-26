import uuid
from src.tibitypes import UnitCell, Site, State, BasisVector


class UCController:
    def __init__(self, model: dict[uuid.UUID, UnitCell]):
        self.model = model

        def add_unit_cell():
            v1 = BasisVector(1, 0, 0)
            v2 = BasisVector(0, 1, 0)
            v3 = BasisVector(0, 0, 1)
            new_cell = UnitCell("New Unit Cell", v1, v2, v3, {}, uuid.uuid4())
            model[new_cell.id] = new_cell

        def edit_unit_cell():
            pass

        def delete_unit_cell(id: uuid.UUID):
            pass

        def add_site():
            new_site = Site("New Site", 0, 0, 0, {}, uuid.uuid4())

        def edit_site():
            pass

        def delete_site():
            pass

        def add_state():
            new_state = State("New State", 0, uuid.uuid4())

        def edit_state():
            pass

        def delete_state():
            pass


# class UnitCellController:
#     """Controller to manage UnitCells, Sites, and their interaction with the tree."""

#     def __init__(self, model, tree_view):
#         self.model = model  # List of UnitCells
#         self.tree_view = tree_view  # QTreeView displaying them

#     def add_unit_cell(self, unit_cell: UnitCell):
#         """Adds a UnitCell to the data and updates the tree."""
#         self.model.append(unit_cell)  # Update data
#         self.tree_view.add_unit_cell(unit_cell)  # Update view

#     def remove_unit_cell(self, unit_cell_name: str):
#         """Removes a UnitCell from the data and updates the tree."""
#         self.model[:] = [c for c in self.model if c.name != unit_cell_name]  # Update data
#         self.tree_view.remove_unit_cell(unit_cell_name)  # Update view

#     def add_site(self, unit_cell_name: str, site: Site):
#         """Adds a Site to a UnitCell and updates the tree."""
#         for cell in self.model:
#             if cell.name == unit_cell_name:
#                 cell.sites.append(site)  # Update data
#                 self.tree_view.add_site(unit_cell_name, site)  # Update view
#                 break

#     def remove_site(self, unit_cell_name: str, site_name: str):
#         """Removes a Site from a UnitCell and updates the tree."""
#         for cell in self.model:
#             if cell.name == unit_cell_name:
#                 cell.sites = [s for s in cell.sites if s.name != site_name]  # Update data
#                 self.tree_view.remove_site(unit_cell_name, site_name)  # Update view
#                 break
