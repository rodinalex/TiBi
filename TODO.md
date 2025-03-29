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
  - The bottom could be a table for hopping elements. To be implemented later
- Right column for computation options and input. The panels will be decided on and implemented later

## Immediate Tasks

- ✅ Add the interactive plot that would take the selected unit cell and plot it in 3D. The plot should 
include the unit cell as a parallelepiped, as well as any of the sites found inside of it
- Add the ability to select sites from the plot and reflect the selection in the tree (partially implemented - highlighting sites works when selected in tree)
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