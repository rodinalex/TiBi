from PySide6.QtCore import Signal, QObject


class Worker(QObject):
    """
    General worker class for performing background tasks.
    """

    progress_updated = Signal(int)
    task_finished = Signal()
    task_aborted = Signal()

    def __init__(self):
        super().__init__()
        self._abort = False

    def do_work(self):
        raise NotImplementedError("Subclasses must implement do_work()")

    def request_abort(self):
        self._abort = True
