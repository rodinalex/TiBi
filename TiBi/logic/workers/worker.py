from PySide6.QtCore import Signal, QObject


class Worker(QObject):
    """
    General worker class for performing background tasks.

    Attributes
    ----------
    _abort : bool
        Flag indicating whether the worker should abourt its task.
    progress_updated : Signal
        Emitted to update the progress of the task.
    task_finished : Signal
        Emitted when the task is completed successfully.
    task_aborted : Signal
        Emitted when the task is aborted by the user.

    Methods
    -------
    do_work() -> None
        Abstract method implemented by subclasses to perform the actual work.
    request_abort() -> None
        Set the abort flag to True, signaling the worker to stop its task.
    """

    progress_updated = Signal(int)
    task_finished = Signal(object)
    task_aborted = Signal()

    def __init__(self):
        super().__init__()
        self._abort = False

    def do_work(self):
        raise NotImplementedError("Subclasses must implement do_work()")

    def request_abort(self):
        """
        Set the abort flag to True, signaling the worker to stop its task.
        """
        self._abort = True
