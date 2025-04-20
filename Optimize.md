# TiBi Architecture Optimization

This document outlines recommendations for improving the architecture of the TiBi application, with a focus on strengthening the Model-View-Controller (MVC) pattern implementation.

## Current MVC Implementation

The TiBi project currently follows the MVC pattern with:

- **Models**: Data structures in `src/tibitypes.py` and reactive models in `models/uc_models.py`
- **Views**: UI components in the `ui/` directory
- **Controllers**: Coordination logic in `controllers/uc_cotroller.py` and partially in `app.py`

## Recommendations for Improvement

### 1. Strengthen Separation of Concerns

#### MainWindow Refactoring
- Extract controller logic from `MainWindow` in `app.py` into a dedicated `ApplicationController` class
- Limit `MainWindow` to UI setup and layout management
- Use the controller to connect signals between components

#### View Component Cleanup
- Remove direct model manipulation from view components
- Create controller methods for all data operations
- Views should emit signals when user actions occur, but controllers should handle the logic

### 2. Consistent Data Flow Patterns

#### Implement Unidirectional Data Flow
- Models should never directly update views
- Controllers should observe models and update views accordingly
- Views should never directly call model methods that modify state

#### Controller Responsibilities
- Controllers should be the only components that update models based on view events
- Controllers should update views in response to model changes
- Controllers should mediate all interactions between models and views

### 3. Specific Component Improvements

#### BrillouinZonePlot and BandStructurePlot
- Move computation logic to a dedicated `ComputationController`
- Views should only handle visualization and user interaction
- Use signals to notify controllers of user actions

#### TreeViewPanel
- Remove model update logic from tree view
- Emit signals for selection changes and item edits
- Let controllers handle model updates

#### UnitCellPlot
- Extract selection logic to a controller
- Focus on visualization only

### 4. Architectural Patterns to Adopt

#### Observer Pattern
- Use consistent signal/slot connections for model changes
- Apply observer pattern more rigorously throughout the application

#### Command Pattern
- Implement user actions as command objects
- Enables features like undo/redo functionality
- Centralizes business logic in a consistent way

#### Factory Pattern
- Use factories to create complex model objects
- Ensures consistent object creation and initialization

### 5. Code Organization

#### Package Structure
- Create a clearer package hierarchy that reflects architectural concerns
- Separate high-level application controllers from component-specific controllers

#### Naming Conventions
- Use consistent naming that reflects architectural roles
- Add clear interfaces/base classes for models, views, and controllers

### 6. Testing Strategy

- Create unit tests for models that are independent of views
- Implement controller tests that use mock views and models
- Add integration tests for complete features

## Implementation Priority

1. Extract controller logic from MainWindow
2. Remove direct model access from views
3. Implement consistent data flow patterns
4. Refactor computation-heavy views
5. Enhance the test suite

By addressing these recommendations, the TiBi application will have a more maintainable architecture that strictly adheres to MVC principles, making it easier to extend with new features and capabilities.