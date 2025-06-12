import numpy as np
from PySide6.QtCore import Signal
from .worker import Worker


class DiagonalizationWorker(Worker):

    task_finished = Signal(list, list)

    def __init__(self, hamiltonian_func, k_points):
        super().__init__()
        self.hamiltonian_func = hamiltonian_func
        self.k_points = k_points

    def do_work(self):

        emit_interval = max(len(self.k_points) // 100, 1)

        eigenvalues = []
        eigenvectors = []
        n_pts = len(self.k_points)
        self.progress_updated.emit(0)

        for ii, k in enumerate(self.k_points):
            if self._abort:
                self.task_aborted.emit()
                return

            H = self.hamiltonian_func(k)
            solution = np.linalg.eigh(H)
            eigenvalues.append(solution[0])
            eigenvectors.append(solution[1])
            self.progress_updated.emit(int((ii + 1) / n_pts * 100))

            if ii % emit_interval == 0 or ii == len(self.k_points) - 1:
                self.progress_updated.emit(
                    int((ii + 1) / len(self.k_points) * 100)
                )

        self.task_finished.emit(eigenvalues, eigenvectors)
