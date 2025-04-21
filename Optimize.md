# TiBi Architecture Optimization

This document provides a detailed roadmap for improving the architecture of the TiBi application, with a focus on properly implementing the Model-View-Controller (MVC) pattern to ensure maintainability as the application grows.

## Current State Analysis

The TiBi project has made progress implementing MVC with:

- **Models**: Data structures in `src/tibitypes.py` and reactive models in `models/uc_models.py`
- **Views**: UI components in the `ui/` directory
- **Controllers**: `controllers/app_controller.py` and `controllers/uc_cotroller.py`

The current implementation has several strengths:
- Reactive data binding with `DataModel` class
- Clear separation of basic UI components
- Initial controller implementation for unit cell management

However, there are areas that require improvement:
- Some views still contain business logic
- Direct model manipulation occurs in UI components
- Inconsistent data flow patterns across the application
- Missing controllers for some UI components (hopping, BZ plot)
- Computation logic embedded in UI components

## Detailed Refactoring Plan

### Phase 1: Controller Extraction and Standardization

#### 1.1. Create HoppingController

Create a dedicated controller for hopping-related operations that currently reside in the `HoppingPanel` class:

```python
# controllers/hopping_controller.py
class HoppingController(QObject):
    def __init__(self, unit_cells, hopping_panel):
        self.unit_cells = unit_cells
        self.hopping_panel = hopping_panel
        
        # Connect signals from UI to controller methods
        self.hopping_panel.matrix.button_clicked.connect(self.handle_pair_selection)
        self.hopping_panel.table.save_btn.clicked.connect(self.save_couplings)
        
    def handle_pair_selection(self, s1, s2):
        # Logic moved from HoppingPanel.handle_pair_selection
        pass
        
    def save_couplings(self):
        # Logic moved from HoppingPanel.save_couplings
        pass
```

#### 1.2. Create BZController

Extract Brillouin zone path handling logic from `BrillouinZonePlot` to a dedicated controller:

```python
# controllers/bz_controller.py
class BZController(QObject):
    def __init__(self, bz_plot, band_plot):
        self.bz_plot = bz_plot
        self.band_plot = band_plot
        
        # Connect UI signals to controller methods
        self.bz_plot.add_gamma_btn.clicked.connect(lambda: self.add_point("gamma"))
        self.bz_plot.add_vertex_btn.clicked.connect(lambda: self.add_point("vertex"))
        # ... other connections
        
    def add_point(self, point_type):
        # Logic moved from BrillouinZonePlot._add_point
        pass
```

#### 1.3. Create ComputationController

Create a controller to handle band structure computation:

```python
# controllers/computation_controller.py
class ComputationController(QObject):
    def __init__(self, unit_cells, bz_plot, band_plot):
        self.unit_cells = unit_cells
        self.bz_plot = bz_plot
        self.band_plot = band_plot
        
        self.bz_plot.compute_bands_btn.clicked.connect(self.compute_bands)
        
    def compute_bands(self):
        # Logic moved from AppController.update_bands_plot
        pass
```

### Phase 2: Refactor Existing Components

#### 2.1. Refactor HoppingPanel

Modify the `HoppingPanel` class to focus on UI presentation:

1. Remove direct model manipulation
2. Expose UI elements and signals
3. Move business logic to the new `HoppingController`

#### 2.2. Refactor BrillouinZonePlot

Modify the `BrillouinZonePlot` class to focus on visualization:

1. Change internal methods to be public, allowing controller access
2. Remove business logic related to path construction
3. Move decision-making logic to the controller
4. Keep visualization methods internal

#### 2.3. Refactor BandStructurePlot

Simplify the `BandStructurePlot` class to focus on plotting:

1. Remove any computation or data processing logic
2. Provide public methods for plot updates
3. Add proper signals for user interactions

### Phase 3: Standardize Data Flow and Interfaces

#### 3.1. Define Clear Controller Responsibilities

Each controller should have specific responsibilities:

- `AppController`: Application-level coordination between components
- `UCController`: Unit cell, site, and state CRUD operations
- `HoppingController`: Hopping parameter management
- `BZController`: BZ visualization and path construction
- `ComputationController`: Physics calculations and result handling

#### 3.2. Standardize Controller Interfaces

For consistency, all controllers should follow common patterns:

```python
class BaseController(QObject):
    """Base class for controllers providing common functionality"""
    
    def __init__(self, models, views):
        super().__init__()
        self.connect_signals()
        
    def connect_signals(self):
        """Connect UI signals to controller methods"""
        pass
```

#### 3.3. Implement Unidirectional Data Flow

For state changes, enforce a consistent pattern:
1. View emits a signal in response to user action
2. Controller method handles the signal
3. Controller updates the model
4. Model signals change event
5. Controller observes model changes
6. Controller updates view state

### Phase 4: Create Dedicated Model Classes

#### 4.1. Create a BZPathModel

Create a dedicated model to represent the BZ path:

```python
class BZPathModel(DataModel):
    """Model representing a path through the Brillouin Zone"""
    
    def __init__(self):
        super().__init__(
            points=[], 
            special_points=[]
        )
```

#### 4.2. Create a BandStructureModel

Create a model for band structure calculation results:

```python
class BandStructureModel(DataModel):
    """Model holding band structure calculation data"""
    
    def __init__(self):
        super().__init__(
            bands=None,
            k_path=None,
            path_positions=None,
            special_points=[]
        )
```

### Phase 5: Refactor MainWindow

#### 5.1. Simplify MainWindow Class

Refactor `MainWindow` to focus solely on UI layout setup:

1. Remove any logic that manipulates data models
2. Remove signal/slot connections
3. Move controller initialization to a separate method

#### 5.2. Create ApplicationController

Create a top-level controller that manages all sub-controllers:

```python
class ApplicationController(QObject):
    """Top-level controller that coordinates all sub-controllers"""
    
    def __init__(self, app_window):
        self.app_window = app_window
        
        # Initialize sub-controllers
        self.uc_controller = UCController(...)
        self.hopping_controller = HoppingController(...)
        self.bz_controller = BZController(...)
        self.computation_controller = ComputationController(...)
        
        # Connect cross-controller signals
        self.connect_controllers()
        
    def connect_controllers(self):
        """Connect signals between different controllers"""
        pass
```

## Implementation Priorities and Timeline

### Immediate Priorities (First Sprint)

1. **Create HoppingController**: Extract logic from HoppingPanel
   - Move model update logic to the controller
   - Refactor HoppingPanel to emit signals when user interacts
   - Update AppController to use the new controller

2. **Refactor BrillouinZonePlot**: Separate visualization from logic
   - Extract internal methods that modify state to controller methods
   - Keep visualization methods in the view
   - Create BZController class

### Medium-term Priorities (Second Sprint)

3. **Create ComputationController**: Separate computation from UI
   - Move band calculation logic to dedicated controller
   - Create models for computation results
   - Update UIs to observe these models

4. **Standardize Controller Interfaces**: Create consistent patterns
   - Define base controller class with common functionality
   - Refactor existing controllers to follow this pattern
   - Document controller responsibilities

### Long-term Priorities (Third Sprint)

5. **Create ApplicationController**: Top-level coordination
   - Refactor MainWindow to focus solely on UI layout
   - Create ApplicationController to manage all sub-controllers
   - Connect cross-controller communication

6. **Implement Comprehensive Testing**: 
   - Create unit tests for models
   - Create integration tests for controllers
   - Create UI tests for critical workflows

## Best Practices to Follow

### Model Design

1. **Model Independence**: Models should have no dependencies on views or controllers
2. **Rich Models**: Models should encapsulate business logic related to their data
3. **Signal-based Change Notification**: Models should emit signals when their data changes

### Controller Design

1. **Single Responsibility**: Each controller should focus on one aspect of the application
2. **Thin Controllers**: Controllers should delegate business logic to models when possible
3. **No UI Logic**: Controllers should not contain code for UI manipulation beyond updating data

### View Design

1. **No Direct Model Mutation**: Views should never directly modify model data
2. **Signal-based User Input**: Views should emit signals in response to user actions
3. **Passive Views**: Views should focus on presentation and user input handling

### Testing Strategy

1. **Model Testing**: Test models in isolation from controllers and views
2. **Controller Testing**: Test controllers with mock models and views
3. **Integration Testing**: Test critical paths through the application

## Migration Plan for Existing Features

To minimize disruption, implement these changes incrementally:

1. Create new controllers alongside existing code
2. Gradually migrate functionality from UI classes to controllers
3. Once controllers are in place, refactor UI classes to rely on controllers
4. Finally, establish the top-level ApplicationController

This approach allows you to make incremental improvements without breaking existing functionality.