# Theme System Architecture & Specification

**Repository:** `IAmJAG/eNuts`  
**Branch:** `development`  
**Related Modules:**  
- `eNuts/src/eNuts/application/theme`  
- `eNuts/src/eNuts/application/__eNutsApplications.py`  

---

## 1. Directory Structure

Shared QSS lives under `qss/`. Each theme is a **palette file** at the themes root whose **file name** is the theme identifier.

```text
<root>/
└── config/
    └── themes/
        ├── qss/
        │   ├── main.css
        │   ├── sideBar.css
        │   └── [additional].css | .qss
        ├── dark                 # palette file (theme id = file name)
        ├── dracula
        ├── ironman
        ├── light
        ├── material
        └── options/
            └── <theme_name>/
                └── <OptionName>.json
```

---

## 2. Palette File Specification

* **Location:** `config/themes/<theme_name>` (no file extension).
* **Format:** `keyword: color_value` (one per line).
* **Supported Color Formats:**
  * Named colors (e.g., `red`, `dodgerblue`)
  * Hexadecimal color codes (e.g., `#1e1e1e`, `#ffffff`)

### Example (`config/themes/ironman`)

```text
bg: #0e1014
surface: #161a20
text: #f5f7fa
accent: #e31b23
```

---

## 3. CSS / QSS Specification & Keyword Substitution

Stylesheets under `config/themes/qss/` use `$keyword` tokens. The loader:

1. Discovers each palette file in `config/themes/` (skips directories such as `qss/` and `options/`).
2. Reads all `*.css` / `*.qss` in `qss/` (sorted by file name).
3. Replaces `$keyword` with values from that theme’s palette (longest key first).
4. Concatenates fragments into one stylesheet string keyed by theme name (lowercased).

### Example

```css
QWidget#W_SIDEBAR {
    background: $surface;
    border-right: 1px solid $border;
}
```

---

## 4. Application wiring

```text
eNutsApplication.asyncSetStyeSheet(cfg.theme)
  → loadStyles(config/themes)
  → setStyleSheet(themeName)   # looks up styles[themeName.lower()]
```

`appconfig.json` field `"theme"` must match a palette file name (e.g. `"ironman"`).

---

## 5. Options (non-QSS)

Widget option JSON is stored at:

```text
config/themes/options/<theme_name>/<OptionName>.json
```

Resolved by `jAGQt.options.OptionsBase.resolvePath(themeName)`.
