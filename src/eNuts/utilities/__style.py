# ==================================================================================================
import os

# ==================================================================================================
from typing import List

# ==================================================================================================
from PySide6.QtWidgets import QApplication, QWidget

# ==================================================================================================
BASE_THEME_PATH: str = "_style"
BASE_THEME_EXT: str = ".css"
# ==================================================================================================


# ==================================================================================================
def applyStyleSheet(wid: QApplication | QWidget, styleSheet: str | List[str]) -> None:
    if isinstance(styleSheet, str): styleSheet = [styleSheet]
    wid.setStyleSheet("\n\n".join(styleSheet))

def loadStyleSheet(themePath: str, styleSheet: str) -> List[str] | str:
    basePath: str = os.path.join(themePath, f"{BASE_THEME_PATH}{BASE_THEME_EXT}")
    styleSheetPath = os.path.join(themePath, f"{styleSheet}{BASE_THEME_EXT}")

    base: str = ""
    style: str = ""

    with open(styleSheetPath, "r") as f:
        style = f.read()

    with open(basePath, "r") as f:
        base = f.read()

    return [base, style]

    
