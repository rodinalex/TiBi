# TiBiPy Project Roadmap


## Immediate Tasks


## Reminders
- Hamiltonian function with momenta along the reciprocal lattice directions
- Check that the volume of the unit cell is non-zero
- MAYBE: add point group information
- Figure out how to help the user distinguish between different sites: for now they all look the same
- Make BZ path selection context-based (that a BZ exists in the first place)
- Refactor the styling:
* Buttons
* Colors
- Add bandstructure plot
- When creating a UC, we occasionally have problematic vectors DURING THE CREATION leading to runtime warnings (parallel vectors, zero volume, etc).
## Daily Plan
- Add path-construction option using the selection

## Tree structure
- update_tree_item, remove_tree_item, select_item, and find_item_by_id have some redundancy: can make more streamlined

## Function calls 
- Fix the redundant redrawing of the unit cell when a new item is selected in the tree (see the signals connected in uc_plot_controller). This leads to two model updates that also trigger the redrawing of the plot


## Bugs
<!-- - Check that the displacements are unique in coupling table
- Add button coloring
- Add "Hermitian Check" -->
<!-- 
## Core Functionality

- Add proper data persistence:
  - Implement save/load functionality for unit cells
  - Support common file formats (CIF, POSCAR, etc.)
  - Add auto-save functionality

- Improve UnitCell visualization:
  - Add 3D visualization of unit cells using OpenGL or similar
  - Enable interactive rotation and zoom
  - Display sites within the unit cell

- Implement site and state management:
  - Enable adding multiple sites to a unit cell
  - Allow managing quantum states for each site
  - Calculate and display site properties

## Advanced Features

- Add symmetry operations:
  - Implement space group detection
  - Enable symmetry-based operations on unit cells
  - Provide symmetry visualization

- Physics calculations:
  - Add basic energy calculations
  - Implement Hamiltonian construction for states
  - Enable simple simulations

- Batch operations:
  - Support for working with multiple unit cells
  - Comparative analysis tools
  - Batch export/import functionality

## UI Improvements

- Add context menus to tree view
- Implement drag-and-drop for reorganizing elements
- Add undo/redo functionality
- Improve application styling and themes
- Add keyboard shortcuts

## Documentation and Testing

- Add proper docstrings to all classes and methods
- Create user documentation with usage examples
- Implement unit tests for core functionality
- Add integration tests for UI components -->