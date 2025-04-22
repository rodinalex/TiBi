# TiBiPy Project Roadmap

## Layout

In the present version, the GUI consists of 3 columns
- The left column focuses on the system generation
  - The top panel shows a collapsable tree composed of unit cells, their child sites, and their child states.
    The nodes of the trees are highlightable. There should be a create new unit cell button somewhere (not sure where)
  - The second panel consists of the fields describing the nodes of the tree. E.g., basis vectors and the name
    for the unit cell, coordinates and the name for the site, energy and the name for the state. The type of the form
    shown in this panel changes depending which node type is selected in the tree. The panel also contains a delete button
    that asks for a confirmation before the node and its children are deleted from the tree. The tree should always
    reflect the current state of the system.
  - The last panel is reserved for something else for now, not sure what


- Middle column for visualization and (potentially) hopping parameter setting
  - The top panel shows an interactive 3D unit cell plot with selectable sites (✅ IMPLEMENTED)
  - The bottom focuses on setting up the hopping parameters. 
- Right column for computation options and input. The panels will be decided on and implemented later

## Immediate Tasks


- Implement a Hamiltonian function based on the Unit Cell datatype. Although, when adding the hoppings, the user can specify hoppings along non-periodic directions, the Hamiltonian must take the correct number of momentum coordinates. Important feature: minimize recalculation of reciprocal vectors and unnecessary calls to Unit Cell object
- Implement the calculation of the bands along the path determined from bz_plot. The user should be able to input the number of points along the path. Since different segments of the path have different lengths, the points should be allocated accordingly.
- Implement a 2D plot that will show the band structure. Preferably with some interactivity: the user should be able to pan/zoom.

## Reminders
- Hamiltonian function with momenta along the reciprocal lattice directions
- Check that the volume of the unit cell is non-zero
- Fix the redundant redrawing in app.py when a new item is selected in the tree. This leads to two model updates that also trigger the redrawing of the plot
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