# Theme System Architecture & Specification

**Repository:** `IAmJAG/eNuts`  
**Branch:** `development`  
**Related Modules:**  
- `eNuts/src/eNuts/application/theme`  
- `eNuts/src/eNuts/application/__application.py`  

---

## 1. Directory Structure

Themes are stored in the root configuration directory. Each theme must reside in its own isolated subdirectory whose name matches the theme's identifier.

```text
<root>/
└── config/
    └── themes/
        └── <theme_name>/
            ├── palette
            ├── main.css
            └── [additional_css_files...].css
```

---

## 2. Palette File Specification

The `palette` file defines key-value mappings for colors used across the theme's stylesheets.

* **File Name:** `palette` (no file extension).
* **Format:** `keyword: color_value`
* **Supported Color Formats:**
  * Named colors (e.g., `red`, `dodgerblue`)
  * Hexadecimal color codes (e.g., `#1e1e1e`, `#ffffff`)

### Example `palette`

```text
primary: #1e1e1e
text: #ffffff
accent: dodgerblue
```

---

## 3. CSS / QSS Specification & Keyword Substitution

Stylesheets contain standard Qt Style Sheet (QSS) rules utilizing replaceable color keywords defined in the `palette` file.

* **Keyword Syntax:** `$keyword` (must match a key defined in `palette`).
* **Processing:** The theme engine replaces all `$keyword` occurrences in `.css` files with their corresponding color values prior to applying the styles to the application.

### Example Stylesheet (`.css`)

```css
QLabel {
    background-color: $primary;
    color: $text;
}

QPushButton {
    border: 1px solid $accent;
}
```