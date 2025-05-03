from PySide6.QtWidgets import QMenuBar, QMenu


class MenuBarView(QMenuBar):
    """
    Menu bar view that provides access to application features.

    This class is a view component that organizes application actions
    into menus, providing a standard way to access all functionality.

    It does not create actions itself, but receives them from an action manager.
    """

    def __init__(self):
        """Initialize the menu bar with empty menus."""
        super().__init__()

        # Create empty menus
        self.file_menu = QMenu("&File", self)
        self.edit_menu = QMenu("&Edit", self)
        self.view_menu = QMenu("&View", self)
        self.computation_menu = QMenu("&Computation", self)
        self.help_menu = QMenu("&Help", self)

        # Add menus to the menu bar
        self.addMenu(self.file_menu)
        # self.addMenu(self.edit_menu)
        # self.addMenu(self.view_menu)
        # self.addMenu(self.computation_menu)
        # self.addMenu(self.help_menu)

    def set_actions(self, action_manager):
        pass

        """
        Set actions from the action manager to the appropriate menus.

        Args:
            action_manager: ActionManager instance containing all actions
        """
        # Populate File menu
        self.file_menu.addAction(action_manager.file_actions["new_project"])
        self.file_menu.addAction(action_manager.file_actions["open_project"])
        self.file_menu.addAction(action_manager.file_actions["import_project"])

        self.file_menu.addSeparator()
        self.file_menu.addAction(action_manager.file_actions["save_project"])
        self.file_menu.addAction(action_manager.file_actions["save_project_as"])

    #     self.file_menu.addSeparator()
    #     self.file_menu.addAction(action_manager.file_actions["export"])
    #     self.file_menu.addSeparator()
    #     self.file_menu.addAction(action_manager.file_actions["quit"])

    #     # Populate Edit menu
    #     self.edit_menu.addAction(action_manager.edit_actions["cut"])
    #     self.edit_menu.addAction(action_manager.edit_actions["copy"])
    #     self.edit_menu.addAction(action_manager.edit_actions["paste"])
    #     self.edit_menu.addSeparator()
    #     self.edit_menu.addAction(action_manager.edit_actions["preferences"])

    #     # Populate View menu
    #     self.view_menu.addAction(action_manager.view_actions["show_toolbar"])
    #     self.view_menu.addAction(action_manager.view_actions["show_statusbar"])

    #     # Populate Computation menu
    #     self.computation_menu.addAction(action_manager.computation_actions["compute_bands"])
    #     self.computation_menu.addAction(action_manager.computation_actions["compute_dos"])

    #     # Populate Help menu
    #     self.help_menu.addAction(action_manager.help_actions["about"])
    #     self.help_menu.addAction(action_manager.help_actions["help"])
