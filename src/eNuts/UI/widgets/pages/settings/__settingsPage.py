# ==================================================================================
# src/eNuts/UI/widgets/pages/settings/__settingsPage.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from PySide6.QtCore import Qt
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
from jAGQt.widgets import CommandBar, Page

# ==================================================================================
from ....configuration import eNutsConfiguration

# ==================================================================================
C_THEME_NAMES: List[str] = ["dark", "light", "dracula", "ironman", "material"]


# ==================================================================================
class SettingsPage(Page):
    """Application settings page.

    Follows the Page contract:

        Page
        ├── Header (Title / Description / CommandBar)
        └── Content
            └── Settings panels (Appearance / …)
    """

    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Settings",
            description="Application configuration",
            parent=parent,
        )
        self.setObjectName("SettingsPage")

        lBar = CommandBar(parent=self)
        self.CommandBar = lBar

        self._buildUI()
        self._loadCurrentTheme()

    # ==================================================================================
    def _contentHost(self) -> QWidget:
        lContent = getattr(self, "Content", None)
        if isinstance(lContent, QWidget):
            return lContent
        return self

    def _attachToContent(self, widget: QWidget) -> None:
        lHost = self._contentHost()
        lContentLayout = getattr(self, "ContentLayout", None)
        if lContentLayout is not None:
            lContentLayout.addWidget(widget, 1)
            return
        if lHost is not self:
            lLayout = lHost.layout()
            if lLayout is None:
                lLayout = QVBoxLayout(lHost)
                lLayout.setContentsMargins(0, 0, 0, 0)
                lLayout.setSpacing(0)
            lLayout.addWidget(widget, 1)
            return
        lPageLayout = self.layout()
        if lPageLayout is not None:
            lPageLayout.addWidget(widget, 1)
            return
        lEmergency = QVBoxLayout(self)
        lEmergency.setContentsMargins(0, 0, 0, 0)
        lEmergency.addWidget(widget, 1)

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
        self._attachToContent(lRoot)

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
            lApp.setStyleSheet(lCfg.styleSheet)
