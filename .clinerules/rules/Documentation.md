# Code Documentation Instructions & Guidelines

## 1. Directory Structure & Path Mirroring
- **Documentation Root:** All documentation must be placed under the `.docs/` directory located at the project root.
- **Path Mirroring:** The documentation file structure must mirror the source code directory, dropping root or source prefixes (e.g., source file `<root>/src/eNuts/__shell.py` maps to documentation path `<root>/.docs/eNuts/shell.md`).
- **Core Files:** Every documentation directory and project environment will include:
  - `<filename>.md` (mirroring the respective code file name).
  - `requirement.md` (project requirements and design decisions).
  - `implementation.md` (low-level implementation details and workflows).

see the file format from <root>/.kilocode/templates/documentTemplates.md

