# ==================================================================================
# src/eNuts/UI/widgets/pages/settings/__settingsPage.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ==================================================================================
from jAGQt.widgets import Page

# ==================================================================================
from .....configuration import eNutsConfiguration

# ==================================================================================
C_THEME_NAMES: List[str] = ["dark", "light", "dracula", "ironman", "material"]

# Dark themes need an explicit light WindowText palette or Qt still paints black.
C_DARK_THEMES = frozenset({"dark", "dracula", "ironman", "material"})


# ==================================================================================
def _applyThemePalette(app: QApplication, theme: str) -> None:
    """Override system palette so text is never black-on-dark (or white-on-light)."""
    lPal = QPalette(app.palette())
    if theme in C_DARK_THEMES:
        lFg = QColor("#f5f7fa")
        lBg = QColor("#0e1014")
        lBase = QColor("#1e242c")
        lAlt = QColor("#161a20")
        lDisabled = QColor("#6b7280")
        lHighlight = QColor("#e31b23")
        lHighlightedText = QColor("#ffffff")
    else:
        lFg = QColor("#1a1a1a")
        lBg = QColor("#f5f5f5")
        lBase = QColor("#ffffff")
        lAlt = QColor("#eeeeee")
        lDisabled = QColor("#9e9e9e")
        lHighlight = QColor("#1976d2")
        lHighlightedText = QColor("#ffffff")

    for lRole in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.BrightText,
        QPalette.ColorRole.ToolTipText,
        QPalette.ColorRole.PlaceholderText,
    ):
        lPal.setColor(QPalette.ColorGroup.Active, lRole, lFg)
        lPal.setColor(QPalette.ColorGroup.Inactive, lRole, lFg)
        lPal.setColor(QPalette.ColorGroup.Disabled, lRole, lDisabled)

    for lRole, lColor in (
        (QPalette.ColorRole.Window, lBg),
        (QPalette.ColorRole.Base, lBase),
        (QPalette.ColorRole.AlternateBase, lAlt),
        (QPalette.ColorRole.Button, lBase),
        (QPalette.ColorRole.ToolTipBase, lBase),
        (QPalette.ColorRole.Highlight, lHighlight),
        (QPalette.ColorRole.HighlightedText, lHighlightedText),
    ):
        lPal.setColor(QPalette.ColorGroup.Active, lRole, lColor)
        lPal.setColor(QPalette.ColorGroup.Inactive, lRole, lColor)
        lPal.setColor(QPalette.ColorGroup.Disabled, lRole, lColor)

    app.setPalette(lPal)


# ==================================================================================
class SettingsPage(Page):
    """Application settings page. Page already owns Header / Content / CommandBar."""

    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Settings",
            description="Application configuration",
            parent=parent,
        )
        self.setObjectName("SettingsPage")

        self._buildUI()
        self._loadCurrentTheme()

    # ==================================================================================
    def _buildUI(self) -> None:
        lRoot = QWidget()
        lRoot.setObjectName("SettingsRoot")
        lOuter = QVBoxLayout(lRoot)
        lOuter.setContentsMargins(0, 0, 0, 0)
        lOuter.setSpacing(0)

        lPanel = QGroupBox("Appearance", lRoot)
        lPanel.setObjectName("SettingsAppearancePanel")
        lPanelLayout = QVBoxLayout(lPanel)
        lPanelLayout.setContentsMargins(12, 16, 12, 12)
        lPanelLayout.setSpacing(12)

        lForm = QFormLayout()
        lForm.setObjectName("SettingsAppearanceForm")
        lForm.setSpacing(10)
        lForm.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._themeCombo = QComboBox(lPanel)
        self._themeCombo.setObjectName("ThemeCombo")
        self._themeCombo.setMinimumWidth(220)
        for lName in C_THEME_NAMES:
            self._themeCombo.addItem(lName.capitalize(), lName)

        lForm.addRow("Theme", self._themeCombo)
        lPanelLayout.addLayout(lForm)

        lBtnRow = QHBoxLayout()
        lBtnRow.setSpacing(8)
        lBtnRow.addStretch(1)

        self._applyBtn = QPushButton("Apply Theme", lPanel)
        self._applyBtn.setObjectName("ApplyThemeBtn")
        self._applyBtn.clicked.connect(self._onApplyTheme)
        lBtnRow.addWidget(self._applyBtn)
        lPanelLayout.addLayout(lBtnRow)

        lOuter.addWidget(lPanel, 0, Qt.AlignmentFlag.AlignTop)
        lOuter.addStretch(1)

        self.Content = lRoot

    # ==================================================================================
    def _loadCurrentTheme(self) -> None:
        lCfg = eNutsConfiguration()
        lStyle = getattr(lCfg, "style", None) or "ironman"
        lStyle = str(lStyle).strip().lower()
        for lIdx in range(self._themeCombo.count()):
            if self._themeCombo.itemData(lIdx) == lStyle:
                self._themeCombo.setCurrentIndex(lIdx)
                return
        for lIdx in range(self._themeCombo.count()):
            if self._themeCombo.itemData(lIdx) == "ironman":
                self._themeCombo.setCurrentIndex(lIdx)
                break

    def _onApplyTheme(self) -> None:
        lTheme: str = self._themeCombo.currentData()
        if not lTheme:
            return
        lCfg = eNutsConfiguration()
        lCfg.style = lTheme
        lCfg.save()
        lApp = QApplication.instance()
        if lApp is not None:
            _applyThemePalette(lApp, lTheme)
            lApp.setStyleSheet(lCfg.styleSheet)
