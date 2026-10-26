# ==================================================================================
from pathlib import Path
from typing import Dict


# ==================================================================================
C_QSS_DIR: str = "qss"
C_QSS_EXTS: tuple[str, ...] = (".css", ".qss")
# ==================================================================================


# ==================================================================================
def loadStyles(path: str | Path) -> Dict[str, str]:
    """Load all themes under ``path``.

    Layout::

        path/
          qss/*.css          — shared stylesheets
          <themeName>        — palette file (theme id = file name)
          options/…          — ignored here
    """
    styles: Dict[str, str] = {}
    root = Path(path)
    if not root.is_dir():
        return styles

    qssDir = root / C_QSS_DIR
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        styles[entry.name.lower()] = loadStyle(entry, qssDir)
    return styles


# ==================================================================================
def _loadPalette(palettePath: str | Path) -> Dict[str, str]:
    palette: Dict[str, str] = {}
    path = Path(palettePath)
    if not path.is_file():
        return palette
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            name, color = line.split(":", 1)
            # KEEP original case — do NOT lower()
            palette[name.strip()] = Color(color.strip()).toHex()
    return palette


# ==================================================================================
def loadStyle(palettePath: str | Path, qssDir: str | Path | None = None) -> str:
    """Build one stylesheet from a palette file and shared ``qss/`` fragments.

    ``qssDir`` defaults to ``<palette parent>/qss`` when omitted (back-compat).
    """
    palettePath = Path(palettePath)
    palette: Dict[str, str] = _loadPalette(palettePath)
    style: str = ""

    if qssDir is None:
        qssDir = palettePath.parent / C_QSS_DIR
    root = Path(qssDir)
    if not root.is_dir():
        return style

    for file in sorted(root.iterdir()):
        if not file.is_file():
            continue
        if file.suffix.lower() not in C_QSS_EXTS:
            continue
        text = file.read_text(encoding="utf-8")
        for key in sorted(palette.keys(), key=len, reverse=True):
            text = text.replace(f"${key}", palette[key])
        style += text
        if not style.endswith("\n"):
            style += "\n"
    return style
