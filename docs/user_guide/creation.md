# Project Structure

This page describes the structure of a TiBi **project** and explains how to create, modify, and interpret its core components — **systems**, **unit cells**, **sites**, and **states**.

In TiBi, a single **project** can contain multiple **systems**. A **system** consists of a **unit cell** with **sites** (atoms). Each **site** can have an arbitrary number of **states** (orbitals).

!!! example
    <div class="grid cards" markdown>

    - Graphene (unit cell)
        - A (site, sublattice A)  
            - pz (state, orbital) 
        - B (site, sublattice B)  
            - pz (state, orbital) 

    - BN (unit cell)
        - B (site, boron)  
            - pz (state, orbital) 
        - N (site, nitrogen)  
            - pz (state, orbital) 
    </div>


The orbitals couple to each other via **hopping terms**. Having multiple systems makes it easy to compare their properties, such as the band structures of two graphene bilayers with different transverse electric fields.

---

## Creating a System

To create a system, you’ll define basis vectors, add sites to the unit cell, and attach states to each site. To start, click the **+ Add Unit Cell** button in the **project layout** view. Once a new unit cell has been added, it is possible to rename it by double clicking on it in the project layout view. Press Enter to confirm the new name.

### Basis Vectors

By default, unit cells start as cubic with no periodicity (i.e., 0D). This means that the unit cell is not repeated along any of its basis vectors. The dimensionality can be set between 0 and 3 by clicking the appropriate radio button. The system’s dimensionality determines how the unit cell is repeated and how the Brillouin zone is computed. For *n*-dimensional systems, the unit cell is repeated along the first *n* basis vectors. You can edit each basis vector using the input fields next to it. Press Enter to apply changes. 

For notational consistency, there are certain restrictions on the basis vectors depending on the system dimensionality:

* 0D: Basis vectors are orthogonal, with the first one pointing in the *x* direction, second in the *y* direction, and the third in the *z* direction.
* 1D: Vector 1 is periodic. Basis vectors are orthogonal, with the first one pointing in the *x* direction, second in the *y* direction, and the third in the *z* direction. 
* 2D: Vectors 1 and 2 are periodic. The periodic vectors lie in the *x-y* plane; the third vector points along the *z* direction.
* 3D: Vectors 1, 2, and 3 are periodic. There is no restriction on their directions or magnitudes.

To visualize the lattice even in the absence of any sites, click the **Toggle wireframe** button from the toolbar. Depending on the dimensionality, it is also possible to change the number of unit cells to be shown along each periodic vector.

As the basis vectors and the dimensionality are modified, the Brillouin zone is updated. The Brillouin zone plot shows the edges and the high-symmetry points of the zone that are used for the band calculation:

* 0D: the Brillouin zone contains a single Γ point
* 1D: the Brillouin zone contains three points (Γ and two points at either end of the zone)
* 2D: the high-symmetry points are the Γ point, vertices, and edge midpoints
* 3D: the high-symmetry points are the Γ point, vertices, edge midpoints, and face centers

!!! tip

    After defining a new unit cell, click the **Reduce Unit Cell** button. This step ensures that the basis is "most orthogonal", making sure that the algorithm for determining the Brillouin zone functions correctly. For example, if one were to pick **v**~1~ = (1,0,0) and **v**~2~ = (1,1,0), the reduction would set **v**~2~ = (0,1,0).

    If the volume of the unit cell is zero, the Brillouin zone is not shown.

### Sites

Sites can be added to a selected unit cell by clicking the "+" icon next to its name in the project layout view. The sites can be renamed the same was as the unit cells. In addition to changing a site's name, it is also possible to modify its radius and color. These two properties are entirely cosmetic and their effect can be seen in the system view.

The position of each site inside the unit cell is given by the fractional coordinates **c**~1~, **c**~2~, and **c**~3~, ranging from 0 to 1. As with the color and radius, the position is, strictly speaking, also a cosmetic feature since the coupling between different orbitals is determined by hopping elements, not the physical distance.

### States

States are added to sites by clicking the "+" icon next to the selected site's name. The states can also be renamed, just as unit cells and sites.

!!! note
    States don’t have an explicit energy parameter. Instead, the diagonal elements of the Hamiltonian (i.e., state energies) are defined as hopping terms from a state to itself. Therefore, the state energies are added when constructing the hopping matrix.

!!! tip
    States, Sites, and Unit Cells can be deleted by either clicking the trash bin icon when the item or selected, or by pressing Backspace/Del keys.

---

## Hoppings

### Hopping Matrix

### Hopping Table

---
<!-- ## Summary

- A project can contain multiple systems.
- Each system contains a unit cell with sites and states.
- Basis vectors define the geometry and periodicity.
- Brillouin zone generation depends on dimensionality.
- Use wireframe view to visualize lattice structure even before adding sites. -->