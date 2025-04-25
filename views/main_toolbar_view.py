from PySide6.QtWidgets import QToolBar


class MainToolbarView(QToolBar):
    """
    Main toolbar view that contains application-wide actions.
    
    This class is a view component that provides a toolbar with common actions
    such as creating new unit cells, saving/loading projects, and accessing
    computation options.
    
    It does not create actions itself, but receives them from an action manager.
    """
    
    def __init__(self):
        """Initialize the main toolbar without actions."""
        super().__init__("Main Toolbar")
        
        # Allow the toolbar to be moved by the user
        self.setMovable(True)
        
    def set_actions(self, action_manager):
        """
        Set actions from the action manager to the toolbar.
        
        Args:
            action_manager: ActionManager instance containing all actions
        """
        # Add New Unit Cell action
        self.addAction(action_manager.file_actions["new_unit_cell"])
        
        # Add separator
        self.addSeparator()
        
        # Add Open and Save actions
        self.addAction(action_manager.file_actions["open_project"])
        self.addAction(action_manager.file_actions["save_project"])
        
        # Add separator
        self.addSeparator()
        
        # Add Export action
        self.addAction(action_manager.file_actions["export"])
        
        # Add separator
        self.addSeparator()
        
        # Add Compute Bands action
        self.addAction(action_manager.computation_actions["compute_bands"])
        
        # Add separator
        self.addSeparator()
        
        # Add Preferences action
        self.addAction(action_manager.edit_actions["preferences"])