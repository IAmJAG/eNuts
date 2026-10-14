# ==================================================================================
import os

# ==================================================================================
from pathlib import Path
from typing import Dict


# ==================================================================================
def loadStyles(path: str | Path) -> Dict[str, str]:
    styles: Dict[str, str] = dict[str, str]()
    for file in Path(path).iterdir():
        if file.is_dir():
            styles[file.name.lower()] = loadStyle(file)

    return styles


# ==================================================================================
def loadStyle(path: str | Path) -> str:
    palette: dict[str, Color] = _loadPalette(path)
    style: str = ""
    for file in Path(path).iterdir():
        if file.is_file():
            if file.suffix != ".css":
                continue
            text = file.read_text()

            for key, value in palette.items():
                text = text.replace(f"${key}", key, str(value))

            style += text

    return style


# ==================================================================================
def _loadPalette(path: str | Path) -> dict[str, Color]:
    palette: Dict[str, Color] = dict[str, Color]()
    palettePath: Path = os.path.join(path, "palette")
    if not os.path.exists(palettePath):
        return palette

    with open(palettePath, "r") as f:
        for line in f:
            name, color = line.split(":")
            palette[name.strip().lower()] = Color(color.strip())

    return palette
