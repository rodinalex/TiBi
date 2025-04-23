from PySide6.QtCore import QObject


class ComputationController(QObject):

    def __init__(self, bz_path):
        super().__init__()
        self.bz_path = bz_path
