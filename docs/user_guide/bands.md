# Band Structrure and Density of States

This page describes how to set up the band structure and density of states computation. This functionality can be found under the **Bands** tab of the central panel.

---

## Bands

Bands can only be computed if the system's dimensionality is greater than zero. The user defines a path through the Brillouin zone using its high-symmetry points as anchors, chooses the number of points in the path, and launches the calculation. Upon its completion, the bands are plotted.

!!! warning
    Changing the system properties erases the computed bands to avoid stale data. Undoing the change does not reinstate the bands as storing this data in the undo stack could consume a lot of memory.

Depending on the system dimensionality, the path can include the Γ point, vertices, edges, or faces of the Brillouin zone. Vertices, edges, and faces each have their own selection controls which are activated in accordance with the dimensionality. By clicking the up and down buttons, the user can change the selection of the particular type of high-symmetry points. By clicking the button **Γ**, **V**, **E**, or **F**, the corresponding point is added to the path along which the bands will be calculated.
As the path is constructed, it is updated in the Brillouin zone plot.

The number of points in the path is set using the **Points** field. Clicking **Compute** launches the calculation and plots the bands upon its completion.

!!! note
    The points are distributed along the path in a manner that guarantees the inclusion of the high-symmetry points while also respecting the distances between the points. Consequently, occasionally the number of points in the calculated path will differ from the value entered in the **Points** field.

!!! info
    The approximate output size is estimated using the number of states in the system and the number of points in the path. In particular, because of the double precision and the complex eigenstates, the output for each point along the path takes $(16\times \mathrm{states}^2+8\times\mathrm{states})$ bytes. The total binary output size is obtained by multiplying this value by the number of points in the path. Finally, because the data is save in the JSON format, there is an additional factor of about 10 of overhead.

---

## Density of States

To obtain the density of states, the reciprocal space primitive cell is discretized by choosing the number of points along each reciprocal vector. The type of the grid (Γ-centered or Monkhorst-Pack) is selected using the radio buttons. Clicking **Compute** launches the calculation and plots the density of states upon its completion.

!!! warning
    Changing the system properties erases the computed grid to avoid stale data. Undoing the change does not reinstate the bands as storing this data in the undo stack could consume a lot of memory.

The user can choose to visualize the density of states as a histogram or as a collection of Lorentzians. For the histogram option, one can choose the number of bins. For Lorentzians, the bin number functions as number of energies at which the density of states is computed, positioned equally between the minimum and maximum eigenvalues. Additionally, the broadening parameter controls the smoothing of the Lorentzian curves.

---

## Projection

There is an option to project the results onto the system states. The states to be included in the projection can be selected from the dropdown menu. For the band plots, the weight of the projection is indicated by the radius of the scatterplot symbols plotted on top of the band lines. For the density of states histogram, the weight of each eigenstate is given by its projection onto the selected states. Finally, for the Lorentzian plot, each Lorentzian is scaled by the weight of the state's projection onto the selected states.

---