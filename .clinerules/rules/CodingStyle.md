# Coding Style Rules

This document defines the coding style rules used throughout the eNuts project codebase.

## General Rules

All code in this project must follow these coding style rules to ensure consistency, readability, and maintainability.

---

## Specific Conventions

### Imports
- Group imports with section separators: `# ==================================================================================`
- Order: Standard library imports first, then third-party (e.g., PySide6), then local imports.
- Separate groups with the separator comment.
- Import grouping with separators is enforced in most files; ensure all new code follows this pattern.

### Code Structure
- Use object-oriented design with inheritance, decorators, and design patterns.
- Use properties for encapsulation of class attributes.
- Implement contracts (e.g., `iConfiguration`, `iProvider`) for modularity.
- Most class should have correspodning contracts/protocol. Specially if a circlular references is most likely to happen

### Type Hints
- Use type hints extensively for function parameters, return types, and variables 
- Ensure type annotations are accurate and up-to-date.

### Error Handling
- Use try-except blocks with specific exception types.
- Log errors using the custom logger (warning, error, critical, fatal).
- Log important code milestone with debug and verbose
- Handle platform-specific code appropriately (e.g., Windows-specific calls).

### Indentation and Spacing
- Use 4 spaces for indentation.
- Maintain consistent spacing around operators and after commas.

### Comments and Docstrings
- Use minimal comments; 
- Include docstrings for decorators and key functions where necessary.
- Use section separators for logical code blocks.
- Do not include the LOGS directory in project documentation structures.

### Constants and Variables
- Avoid global variables; use dependency injection instead.

### GUI and Framework Usage
- Use PySide6 (Qt) for UI components with custom jAGQt wrappers.
- Implement layouts, events, and icons consistently.
- Process QSS (Qt Style Sheets) with regex for variables and placeholders.

### Patterns and Best Practices
- Use lifecycle management for dependencies (Singleton, Transient, Factory).
- Ensure cross-platform compatibility where applicable.

---

## Enforcement

- All new code must follow these style rules.
- Code reviews will check for style compliance.
- Automated tools may be used to validate style in the future.

## Rationale

These rules promote:
- **Consistency**: Uniform style across the codebase.
- **Readability**: Clear, maintainable code structure.
- **Maintainability**: Easier to understand, modify, and extend.
- **Quality**: Robust error handling and type safety.
