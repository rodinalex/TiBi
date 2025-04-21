from PySide6.QtCore import QObject
import numpy as np


class HoppingController(QObject):
    """
    Controller for managing hopping parameter operations.
    
    This controller handles the interactions between the hopping UI components
    and the underlying data models. It processes user actions from the hopping
    matrix and table, and updates the data models accordingly.
    
    Responsibilities:
    - Handling state selection in the hopping matrix
    - Processing changes to hopping parameters from the table
    - Updating the unit cell model with new hopping data
    - Maintaining consistency between the UI and data model
    """
    
    def __init__(self, unit_cells, hopping_panel):
        """
        Initialize the hopping controller.
        
        Args:
            unit_cells: Dictionary mapping UUID to UnitCell objects
            hopping_panel: The hopping panel UI component
        """
        super().__init__()
        
        # Store references to models and views
        self.unit_cells = unit_cells
        self.hopping_panel = hopping_panel
        
        # Connect UI signals to controller methods
        self.hopping_panel.matrix.button_clicked.connect(self.handle_pair_selection)
        self.hopping_panel.matrix.hoppings_changed.connect(self.handle_matrix_interaction)
        self.hopping_panel.table.save_btn.clicked.connect(self.save_couplings)
        
        # Initialize controller state
        self.current_uc_id = None
        self.selected_state1 = None
        self.selected_state2 = None
    
    def set_unit_cell(self, uc_id):
        """
        Set the current unit cell for hopping operations.
        
        Args:
            uc_id: UUID of the selected unit cell, or None if no unit cell is selected
        """
        self.current_uc_id = uc_id
        self.selected_state1 = None
        self.selected_state2 = None
        
        # If no unit cell selected, hide the panels
        if uc_id is None:
            self.hopping_panel.panel_stack.setCurrentWidget(self.hopping_panel.info_label)
            self.hopping_panel.table.set_state_coupling([])
            self.hopping_panel.table.table_title.setText("")
            return
        
        # Get the unit cell and check if it has any states
        uc = self.unit_cells[uc_id]
        new_states, new_info = uc.get_states()
        
        # Set up the matrix view with the states
        self.hopping_panel.matrix.set_states(new_info)
        self.hopping_panel.hopping_data = self.hopping_panel.hopping_data.__class__(uc.hoppings)
        self.hopping_panel.matrix.set_hopping_data(self.hopping_panel.hopping_data)
        
        # Hide the panel if there are no states in the unit cell
        if not new_states:
            self.hopping_panel.panel_stack.setCurrentWidget(self.hopping_panel.info_label)
        else:
            self.hopping_panel.panel_stack.setCurrentWidget(self.hopping_panel.panel)
            
        # Reset the table selection
        self.hopping_panel.table_stack.setCurrentWidget(self.hopping_panel.table_info_label)
    
    def handle_pair_selection(self, s1, s2):
        """
        Handle selection of a state pair in the hopping matrix.
        
        Args:
            s1: Tuple of (site_name, state_name, state_id) for the destination state (row)
            s2: Tuple of (site_name, state_name, state_id) for the source state (column)
        """
        # Store the UUIDs of the selected states
        self.selected_state1 = s1[2]  # Destination state UUID
        self.selected_state2 = s2[2]  # Source state UUID
        
        # Show the table with the hopping data for this state pair
        self.hopping_panel.table_stack.setCurrentWidget(self.hopping_panel.table)
        
        # Retrieve existing hopping terms between these states
        state_coupling = self.hopping_panel.hopping_data.get(
            (self.selected_state1, self.selected_state2), []
        )
        
        # Update the table with the retrieved hopping terms
        self.hopping_panel.table.set_state_coupling(state_coupling)
        
        # Update the table title to show the selected states (source → destination)
        self.hopping_panel.table.table_title.setText(f"{s2[0]}.{s2[1]} → {s1[0]}.{s1[1]}")
    
    def handle_matrix_interaction(self):
        """
        Handle changes to the hopping matrix from context menu interactions.
        
        Updates the table to reflect changes in the matrix (like setting transpose elements
        or clearing hoppings).
        """
        self.hopping_panel.matrix.refresh_button_colors()
        
        # If we have a selected state pair, update the table
        if self.selected_state1 and self.selected_state2:
            updated_couplings = self.hopping_panel.hopping_data.get(
                (self.selected_state1, self.selected_state2), []
            )
            self.hopping_panel.table.set_state_coupling(updated_couplings)
    
    def save_couplings(self):
        """
        Save changes from the hopping table to the model.
        
        Extracts data from the table, processes it to merge duplicate displacements,
        and updates the unit cell model with the new hopping data.
        """
        if not self.current_uc_id or not self.selected_state1 or not self.selected_state2:
            return
            
        new_couplings = {}
        
        # Extract values from each row in the table
        for row in range(self.hopping_panel.table.hopping_table.rowCount()):
            # Get displacement vector components (integers)
            d1 = self.hopping_panel.table.hopping_table.cellWidget(row, 0).value()
            d2 = self.hopping_panel.table.hopping_table.cellWidget(row, 1).value()
            d3 = self.hopping_panel.table.hopping_table.cellWidget(row, 2).value()
            
            # Get complex amplitude components (floats)
            re = self.hopping_panel.table.hopping_table.cellWidget(row, 3).value()
            im = self.hopping_panel.table.hopping_table.cellWidget(row, 4).value()
            
            # Create the complex amplitude
            amplitude = np.complex128(re + im * 1j)
            
            # Create a tuple for the displacement vector (d₁, d₂, d₃)
            triplet = (d1, d2, d3)
            
            # If the triplet already exists, merge amplitudes by adding the new amplitude
            if triplet in new_couplings:
                new_couplings[triplet] += amplitude
            else:
                new_couplings[triplet] = amplitude
        
        # Convert the dictionary to the expected format of the list of tuples
        merged_couplings = [
            ((d1, d2, d3), amplitude)
            for (d1, d2, d3), amplitude in new_couplings.items()
        ]
        
        # Update the data model with the new couplings
        self.hopping_panel.hopping_data[(self.selected_state1, self.selected_state2)] = merged_couplings
        self.unit_cells[self.current_uc_id].hoppings = self.hopping_panel.hopping_data
        
        # Refresh the table with the new data
        self.hopping_panel.table.set_state_coupling(merged_couplings)
        
        # Update the matrix to show the new coupling state
        self.hopping_panel.matrix.refresh_matrix()