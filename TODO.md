# TiBiPy Project Roadmap

## Features
- Export the system to a file
- Import a system from a file
- Add hints for the status bar
- Selectively hide sites for clarity
- Fix the band plotting layout
- Figure out dragging of hoppings between different site pairs
- Undo possibility
- Progress bar for calculations
- Maybe a 3D plot with a grid of points in the momentum space that we can make light up/switch off by adjusting energy range/state composition

## Functionality
- Threads/workers

## Tasks
- Dedicate the right panel to calculations:
  - Move BZ panel to the right
  - Put a placeholder instead of its current panel (to be used for other system creation options, maybe supercell)
- Add a progress bar at the bottom of the right panel
- Investigate threading
- Add DOS panel (with projection) to the right panel
- Add band visualization options to the right panel (?) maybe to show the projected bands to the states in the system?
- Berry curvature/connection/phase panel on the right. Figure out how to visualize it

## Bugs

- Make sure that we cannot add the same BZ point multiple times


🔧 Core Functionalities You Already Have (and are spot-on):
Band structure with high-symmetry path + projections (like orbital or atomic character).
DOS and projected DOS, computed over a grid.
k-space visualization with filtering by energy window (very useful for visualizing Fermi surfaces, for instance).
Berry phase/curvature/connection, with reciprocal space overlays (very helpful in topological systems).
🧭 Suggested Additional Features
5. Fermi Surface Visualization (especially for 2D/3D)

Let the user select an energy (e.g. the Fermi level), and plot the surface (or contour) in reciprocal space where the band crosses that energy.
Even in 2D, plotting energy contours helps reveal nesting, van Hove singularities, etc.
6. Wannier Charge Centers / Wilson Loops

A great companion to Berry phase: computing the evolution of hybrid Wannier centers (in 1D BZ slices) gives access to Z2 invariants in 2D or 3D, Chern number, and other topological diagnostics.
This can be integrated into the reciprocal space plot.
7. Topological Invariants

Integrate Chern number, Z2 invariant computation (where appropriate).
You can summarize them for the whole system and annotate Berry curvature plots.
8. Real-Space Local Density of States (LDOS)

For supercells or finite systems, allow LDOS maps (especially useful for edge states, impurities, interfaces).
Could show these either as spatial maps or layer-resolved plots.
9. Edge States / Ribbon Band Structure

From bulk TB input, create a ribbon geometry along a given direction.
Show edge vs bulk states, possibly with real-space projections.
Add a “ribbon generator” tool: select a direction and number of layers → auto-generate finite strip.
10. User-Defined Operators

Allow users to define and compute expectation values of operators in eigenstates. E.g., spin expectation ⟨ψ|σᵢ|ψ⟩, current operators, or orbital moments.
Especially useful for models with internal degrees of freedom (spin, orbital, etc.).
11. Time-Reversal and Symmetry Analysis

Provide automated symmetry checks: does the system have inversion, TRS, mirror symmetry, etc.?
Highlight their implications: “You can expect degenerate Kramers pairs” or “Berry curvature must vanish globally.”
12. Real-space Hamiltonian Viewer / Editor

A visual tool to inspect and edit the Hamiltonian: show the lattice, couplings, hopping terms, etc.
Useful both for learning and debugging.
13. k·p Model Extraction (Optional)

Near high-symmetry points (like K, Γ), fit a low-energy k·p model from the TB data.
Could show users an approximate analytic form or matrix.
🧠 Optional Advanced Stuff (For Down the Line)
Green’s Function Tools: For surface Green’s functions, spectral functions, etc.
Floquet Band Structures: For periodically driven systems (time-dependent hoppings/phases).
Disorder: Show how small randomness in on-site or hopping terms affects DOS or localization.

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