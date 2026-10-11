# ==================================================================================================
from __future__ import annotations

# ==================================================================================================
import os
from typing import List

# ==================================================================================================
from PySide6.QtWidgets import QApplication, QWidget

# ==================================================================================================
C_BASE_DIR: str = "_base"
C_QSS_EXTS: tuple[str, ...] = (".qss", ".css")
# ==================================================================================================


# ==================================================================================================
def ApplyStyleSheet(wid: QApplication | QWidget, styleSheet: str | List[str]) -> None:
    if isinstance(styleSheet, str):
        styleSheet = [styleSheet]
    wid.setStyleSheet("\n\n".join(styleSheet))


def LoadStyleSheet(themePath: str, styleName: str) -> List[str]:
    """Load QSS fragments for a theme.

    Order:
      1. config/.../_base/*.qss   (structural, shared)
      2. config/.../<styleName>/*.qss  (theme colors per component)

    Fallback (legacy):
      If the theme folder is missing, load <themePath>/<styleName>.css
      and optional <themePath>/_style.css as before.
    """
    lParts: List[str] = []
    lThemePath = os.path.normpath(themePath)
    lStyleName = (styleName or "").strip()

    lBaseDir = os.path.join(lThemePath, C_BASE_DIR)
    lThemeDir = os.path.join(lThemePath, lStyleName) if lStyleName else ""

    if os.path.isdir(lBaseDir):
        lParts.extend(_readQssDir(lBaseDir))

    if lThemeDir and os.path.isdir(lThemeDir):
        lParts.extend(_readQssDir(lThemeDir))
        return lParts

    # Legacy flat-file path: _style.css + <style>.css
    lLegacyBase = os.path.join(lThemePath, f"_style{C_QSS_EXTS[1]}")
    lLegacyTheme = os.path.join(lThemePath, f"{lStyleName}{C_QSS_EXTS[1]}")
    for lPath in (lLegacyBase, lLegacyTheme):
        if os.path.isfile(lPath):
            lText = _readFile(lPath)
            if lText:
                lParts.append(lText)
    return lParts


def _readQssDir(dirPath: str) -> List[str]:
    """Read all .qss/.css files in dirPath, sorted by filename."""
    lOut: List[str] = []
    try:
        lNames = sorted(
            lName
            for lName in os.listdir(dirPath)
            if lName.lower().endswith(C_QSS_EXTS) and not lName.startswith(".")
        )
    except OSError:
        return lOut

    for lName in lNames:
        lPath = os.path.join(dirPath, lName)
        if not os.path.isfile(lPath):
            continue
        lText = _readFile(lPath)
        if lText:
            lOut.append(lText)
    return lOut


def _readFile(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as lFile:
            return lFile.read().strip()
    except OSError:
        return ""


# Back-compat aliases (call sites may still use camelCase)
applyStyleSheet = ApplyStyleSheet
loadStyleSheet = LoadStyleSheet
