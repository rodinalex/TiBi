import numpy as np
from .worker import Worker


class DiagonalizationWorker(Worker):
    """
    Worker for diagonalizing a Hamiltonian at multiple k-points.

    Attributes
    ----------
    hamiltonian_func : callable
        Function that takes a k-point and returns the Hamiltonian matrix.
    k_points : list
        List of k-points at which to diagonalize the Hamiltonian.
    """

    def __init__(self, hamiltonian_func, k_points):
        """
        Initialize the DiagonalizationWorker.

        Parameters
        ----------
        hamiltonian_func : callable
            Function that takes a k-point and returns the Hamiltonian matrix.

        k_points : list
            List of k-points at which to diagonalize the Hamiltonian.
        """
        super().__init__()
        self.hamiltonian_func = hamiltonian_func
        self.k_points = k_points

    def do_work(self):
        """
        Diagonalize the Hamiltonian at the specified k-points.

        At the end of the computation, emit a signal with the results.
        """

        emit_interval = max(len(self.k_points) // 100, 1)

        eigenvalues = []
        eigenvectors = []
        self.progress_updated.emit(0)

        for ii, k in enumerate(self.k_points):
            if self._abort:
                self.task_aborted.emit()
                return

            H = self.hamiltonian_func(k)
            solution = np.linalg.eigh(H)
            eigenvalues.append(solution[0])
            eigenvectors.append(solution[1])

            if ii % emit_interval == 0 or ii == len(self.k_points) - 1:
                self.progress_updated.emit(
                    int((ii + 1) / len(self.k_points) * 100)
                )

        self.task_finished.emit((eigenvalues, eigenvectors, self.k_points))
