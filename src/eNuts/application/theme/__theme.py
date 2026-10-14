# ==================================================================================
import os

# ==================================================================================
from pathlib import Path
from typing import Dict


# ==================================================================================
def loadStyles(path: str | Path) -> Dict[str, str]:
    styles: Dict[str, str] = {}
    root = Path(path)
    if not root.is_dir():
        return styles
    for entry in root.iterdir():
        if entry.is_dir():
            styles[entry.name.lower()] = loadStyle(entry)
    return styles


# ==================================================================================
def loadStyle(path: str | Path) -> str:
    palette: Dict[str, str] = _loadPalette(path)
    style: str = ""
    root = Path(path)
    for file in sorted(root.iterdir()):
        if not file.is_file() or file.suffix.lower() != ".css":
            continue
        text = file.read_text(encoding="utf-8")
        for key, value in palette.items():
            text = text.replace(f"${key}", value)
        style += text
        if not style.endswith("\n"):
            style += "\n"
    return style


# ==================================================================================
def _loadPalette(path: str | Path) -> Dict[str, str]:
    palette: Dict[str, str] = {}
    palettePath = Path(path) / "palette"
    if not palettePath.is_file():
        return palette
    with open(palettePath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            name, color = line.split(":", 1)
            palette[name.strip().lower()] = Color(color.strip()).toHex()
            
    return palette
