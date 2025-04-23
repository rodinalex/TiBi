from PySide6.QtCore import QObject


class BandStructurePlotController(QObject):

    def __init__(self):
        super().__init__()

    # def _plot_bands(self, pos, bands):
    #     """
    #     Plot the calculated bands.

    #     """
    #     # Clear previous plot
    #     self.ax.clear()

    #     # Plot each band

    #     for band_idx in range(bands.shape[1]):
    #         self.ax.plot(pos, bands[:, band_idx], "b-")

    #     # # Add vertical lines at special points
    #     # special_distances = [distances[0]]  # First point

    #     # # Add intermediate points where path changes direction
    #     # for i in range(1, len(special_points)):
    #     #     idx = i * (self.num_points // (len(special_points) - 1))
    #     #     if idx < len(distances):
    #     #         special_distances.append(distances[idx])

    #     # # Add vertical lines at special points
    #     # for dist in special_distances:
    #     #     self.ax.axvline(x=dist, color="k", linestyle="--", alpha=0.5)

    #     # # Set x-ticks at special points with labels
    #     # self.ax.set_xticks(special_distances)
    #     # if len(self.special_point_labels) >= len(special_distances):
    #     #     self.ax.set_xticklabels(self.special_point_labels[: len(special_distances)])

    #     # # Set labels and grid
    #     # self.ax.set_xlabel("k-vector")
    #     # self.ax.set_ylabel("Energy")
    #     self.ax.grid(True)

    #     # Draw the canvas
    #     self.canvas.draw()
