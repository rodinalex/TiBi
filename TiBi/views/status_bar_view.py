from PySide6.QtWidgets import QStatusBar, QLabel


class StatusBarView(QStatusBar):
    """
    Status bar view that displays application status information.

    This class is a view component that shows messages to the user.

    Methods
    -------
    update_status(text: str)
        Update the status label.
    """

    def __init__(self):
        super().__init__()

        # Create a permanent status label
        self.status_label = QLabel("Ready")
        self.addPermanentWidget(self.status_label)

    def update_status(self, text: str):
        """
        Update the status label.

        Parameters
        ----------
        text : str
            New status text to display
        """
        self.status_label.setText(text)
