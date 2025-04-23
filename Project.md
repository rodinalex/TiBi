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

