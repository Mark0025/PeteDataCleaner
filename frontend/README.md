# Pete Frontend Architecture

## Overview

The frontend is designed with a modular, component-based architecture to improve maintainability, readability, and extensibility.

## Directory Structure

```
frontend/
├── components/      # Reusable UI components
├── dialogs/         # Specialized dialog windows
├── utils/           # Utility functions and helpers
├── constants.py     # Shared constants and configuration
└── main_window.py   # Main application entry point
```

## Key Components

### Base Component

`components/base_component.py` provides a base class with:

- Common layout management
- Logo handling
- Navigation button support
- Consistent initialization pattern

### Utilities

- `utils/logo_utils.py`: Logo generation
- Consistent styling and branding

### Dialogs

Specialized dialogs for:

- Settings configuration
- Mapping rules
- Column manipulation

## Design Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Reusability**: Components designed to be easily reused
3. **Extensibility**: Easy to add new features without modifying existing code
4. **Consistent UI**: Shared utilities ensure uniform look and feel

## Getting Started

1. Understand the base component structure
2. Use base classes for new components
3. Follow existing patterns for new features

## Contributing

- Keep components small and focused
- Use type hints
- Write docstrings
- Follow PEP 8 style guidelines

## Performance Considerations

- Lazy loading of components
- Minimal widget creation
- Efficient layout management

## Future Improvements

- Add more utility functions
- Create more generic base components
- Implement dependency injection
- Add comprehensive logging
