# ==================================================================================================
from __future__ import annotations

# ==================================================================================================
import os

# ==================================================================================================
from ctypes import byref, c_int, sizeof, windll
from sys import platform

# ==================================================================================================
from typing import List

# ==================================================================================================
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget

# ==================================================================================================
C_BASE_DIR: str = "_base"
C_QSS_EXTS: tuple[str, ...] = (".qss", ".css")
# ==================================================================================================

# ==================================================================================================
def applyDarkBootstrapPalette(app: QApplication) -> None:
    lBg = QColor("#1e1e1e")
    lFg = QColor("#e0e0e0")
    lPal = QPalette()
    lPal.setColor(QPalette.ColorRole.Window, lBg)
    lPal.setColor(QPalette.ColorRole.WindowText, lFg)
    lPal.setColor(QPalette.ColorRole.Base, lBg)
    lPal.setColor(QPalette.ColorRole.Text, lFg)
    lPal.setColor(QPalette.ColorRole.Button, lBg)
    lPal.setColor(QPalette.ColorRole.ButtonText, lFg)
    app.setPalette(lPal)
    app.setStyle("Fusion")


# ==================================================================================================
def enableWinDarkTitleBar(hwnd: int) -> None:
    if platform != "win32" or not hwnd:
        return

    try:
        lAttr = c_int(20)
        lValue = c_int(1)
        windll.dwmapi.DwmSetWindowAttribute(hwnd, lAttr, byref(lValue), sizeof(lValue))

    except Exception:
        try:
            lAttr = c_int(19)
            lValue = c_int(1)
            windll.dwmapi.DwmSetWindowAttribute(hwnd, lAttr, byref(lValue), sizeof(lValue))

        except Exception:
            pass

# ==================================================================================================
def ApplyStyleSheet(wid: QApplication | QWidget, styleSheet: str | List[str]) -> None:
    if isinstance(styleSheet, str): styleSheet = [styleSheet]
    wid.setStyleSheet("\n\n".join(styleSheet))


def LoadStyleSheet(themePath: str, styleName: str) -> List[str]:
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
        if not os.path.isfile(lPath): continue
        lText = _readFile(lPath)
        if lText: lOut.append(lText)
    return lOut


def _readFile(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as lFile:
            return lFile.read().strip()
    except OSError:
        return ""

applyStyleSheet = ApplyStyleSheet
loadStyleSheet = LoadStyleSheet
