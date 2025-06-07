from PySide6.QtWidgets import QStatusBar, QLabel


class StatusBarView(QStatusBar):
    """
    Status bar view that displays application status information.

    This class is a view component that shows messages to the user.
    """

    def __init__(self):
        """Initialize the status bar with default components."""
        super().__init__()

        # Create a permanent status label
        self.status_label = QLabel("Ready")
        self.addPermanentWidget(self.status_label)

    def update_status(self, text):
        """
        Update the status label.

        Args:
            text: New status text to display
        """
        self.status_label.setText(text)
