# TiBi Project Scope

## General Information

The purpose of this project is to use PySide to provide a GUI for tight-binding calculations aimed at theorists and experimentalists. 
This GUI will perform relatively fast calculations (like band structure), as well as slower ones (like integrating over
the entire Brollouin zone to compute Berry curvature, polarization function, for example).

## Features

The user will be able to create unit cells by providing their 3 basis vectors. Each unit cell will then contain sites (one
can think of them as atoms) defined by their positions along the three basis vectors. Each site will contain possibly
multiple quantum states (like orbitals) defined by their energies. The unit cell, along with the sites will be shown
in a interactive plot, allowing the user to rotate the cell and highlight the sites.

The user than will be able to take the Unit Cells and turn them into periodic systems along any or multiple of the basis
vectors. They will also be able to add hoppings between the states (both within and across unit cells of the crystal).
With the system assempled, the user will get information about the shape of the Brillouin zone and be able to choose
how to calculate the band structure: either following a path across the Brollouin zone or for a grid. The results
will then be visualized.

The user will also be able to turn the unit cells into supercells with all the hoppings preserved correctly. By creating
a very large supercell, the user will be able to create defects by modifying local sites/states/hoppings.

The types of calculations that the user will be able to perform will be expanded as the project progresses.


<!-- # CF_red = colorant"rgba(204, 121, 167, 1.0)"
# CF_vermillion = colorant"rgba(213, 94, 0, 1.0)"
# CF_orange = colorant"rgba(230, 159, 0, 1.0)"
# CF_yellow = colorant"rgba(240, 228, 66, 1.0)"
# CF_green = colorant"rgba(0, 158, 115, 1.0)"
# CF_sky = colorant"rgba(86, 180, 233, 1.0)"
# CF_blue = colorant"rgba(0, 114, 178, 1.0)"
# CF_black = colorant"rgba(100, 100, 100, 1.0)" -->
