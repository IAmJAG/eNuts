# Naming Conventions

This document defines the naming conventions used throughout the eNuts project codebase.

## General Rules

All code in this project must follow these naming conventions to ensure consistency and maintainability.

---

## Specific Conventions

- **Modules**: Use dunder then lowercase for module names.
  - *Note: This is highly unconventional for standard Python modules and should be used with caution.*

  - Example: `__videocache.py`, `__framecache.py`

- **Regular Classes**: Use **PascalCase** for class names. 
  - Example: `VideoCache`, `FrameCache`, `CacheConfig`

- **Internal/Private Classes**: Use **camelCase** for class names. 
  - Example: `videoCache`, `frameCache`, `cacheConfig`

- **Functions (Public)**: Use **camelCase** for function names.
  - Example: `getFrame()`, `putFrame()`, `clearCache()`

- **Private Functions**: Starts with `_` then **camelCase** after the underscore.
  - Example: `_getFrame()`, `_putFrame()`, `_clearCache()`

- **Constants (Module/Global Level)**: Use **UPPERCASE** for constant names and should start with `C_`.
  - Example: `C_MAX_FRAMES`, `C_DEFAULT_CACHE_SIZE`

- **Local Variables (Function Scope)**: **camelCase**.
  - Example: `localVariable`, `frameData`, `cacheSize`

- **Non-Instance Variables (Module or Wider Scope)**: Start with `nl` then **TitleCase** after the second letter.
  - Example: `nlTotalFrames`, `nlFrameCount`

- **Global Variables**: Use **UPPERCASE** that starts with `G_`.
  - Example: `G_GLOBAL_CONFIG`, `G_APP_INSTANCE`

- **Class Variables (Shared by all instances)**: Use **UPPERCASE**.
  - Example: `DEFAULT_MAX_FRAMES`, `CACHE_ENABLED`

- **Class Instance Variables (Intended to be private)**: Start with `_` then **camelCase** after the underscore.
  - Example: `_cache`, `_config`, `_currentPosition`, `_maxFrames`

- **Function Arguments**: Use **camelCase** for function arguments.
  - Example: `frameId`, `cacheConfig`, `position`

- **Class Attributes (Public accessors/properties) - No inherited attribute with the same name**: Use **camelCase** 
  - Example: `maxFrames`, `enabled`, `currentPosition

- **Class Attributes (Public accessors/properties) - With inherited attribute with the same name** : Use **TitleCase**   
  - Example: `Text`, `Icon`, `CurrentPosition`

- **Class Private Attributes**: Start with `_` then **camelCase** after the underscore.
  - Example: `_frames`, `_currentPosition`

- **Enum classes**: Start with `e` then **TitleCase** after the underscore.
  - Example: `eAlignment`

---

## Exemptions

- **Testing and Validation**: Test files and validation code are exempt from these naming conventions to allow for more flexible naming in testing contexts.
- **Authorized Exceptions**: Classes starting with lowercase letters (e.g., `ENutsConfiguration`, `dataFormPage`, `logViewer`, `cardBase`, `eStyleColorProperties`, `iComponent`) are authorized as exceptions.
- **Qt Overrides**: Functions overriding Qt methods (e.g., `setupUI`, `mousePressEvent`, `paintEvent`) may use lowercase or mixed case as per Qt API.
- **Logger Functions**: Logger module functions (e.g., `debug`, `info`, `error`) use lowercase for API compatibility.
- **Entry Points**: Main functions (e.g., `def main`) use lowercase as standard Python convention.

---

## Examples


## Rationale

These conventions provide:
- **Consistency**: Uniform naming across the entire codebase
- **Readability**: Clear distinction between different types of identifiers
- **Maintainability**: Easier to understand and modify code
- **Type Indication**: Prefixes help identify variable scope and type

## Enforcement

- All new code must follow these conventions
- Code reviews will check for convention compliance
- Automated tools may be used to validate naming in the future
