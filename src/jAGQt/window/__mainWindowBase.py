# ==================================================================================
# src/jAGQt/window/__mainWindowBase.py
# ==================================================================================
from __future__ import annotations

from enum import Enum
from typing import Optional

# ==================================================================================
from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSettings,
    QSize,
)
from PySide6.QtGui import QGuiApplication

# ==================================================================================
from jAGFx.workflow import workflow

# ==================================================================================
from .windowBase import WindowBase


# ==================================================================================
class ShowAnimation(str, Enum):
    """Available window show animations."""

    Popup = "popup"
    SlideRight = "slideRight"
    SlideLeft = "slideLeft"
    SlideTop = "slideTop"
    SlideDown = "slideDown"


# ==================================================================================
@workflow("InitializeUI", "InitializeSettings", "RestoreWindowsState")
class MainWindowBase(WindowBase):
    """Richer foundation for application main-window and dashboard classes."""

    def __init__(
        self,
        name: str = None,
        frameless: bool = False,
        *args,
        showAnimation: ShowAnimation | str = ShowAnimation.Popup,
        showAnimationDurationMs: int = 280,
        **kwargs,
    ) -> None:
        super().__init__(name, frameless, *args, **kwargs)
        self._showAnimation: ShowAnimation = self._coerceShowAnimation(showAnimation)
        self._showAnimationDurationMs: int = max(0, int(showAnimationDurationMs))
        self._showAnimationRunning: bool = False
        self._showAnimGroup: Optional[QParallelAnimationGroup] = None

    # ------------------------------------------------------------------ workflow hooks
    def _wInitializeSettings(self) -> None:
        company = self.Company if hasattr(self, "Company") else "jAGQt"
        applicationId = (
            self.ApplicationId if hasattr(self, "ApplicationId") else "jAGQt::ModernWindow"
        )
        self._qsettings = QSettings(company, applicationId)

    def _wRestoreWindowsState(self) -> None:
        self.restoreWindowsState()

    # ------------------------------------------------------------------ public API
    def saveWindowState(self) -> None:
        self.Settings.setValue("geometry", self.geometry())
        self.Settings.setValue("windowState", self.windowState())

    def restoreWindowsState(self) -> None:
        if self.Settings.contains("geometry"):
            self.setGeometry(self.Settings.value("geometry"))

        if self.Settings.contains("windowState"):
            self.setWindowState(self.Settings.value("windowState"))

    def Show(
        self,
        animation: Optional[ShowAnimation | str] = None,
        durationMs: Optional[int] = None,
    ) -> None:
        """Show the window with the configured (or override) animation."""
        if animation is not None:
            self._showAnimation = self._coerceShowAnimation(animation)
        if durationMs is not None:
            self._showAnimationDurationMs = max(0, int(durationMs))

        if self._showAnimationDurationMs <= 0 or self._showAnimationRunning:
            self.setWindowOpacity(1.0)
            super().show()
            return

        self._runShowAnimation()

    def show(self) -> None:
        """Qt show() entry — routes through animated Show()."""
        self.Show()

    # ------------------------------------------------------------------ properties
    @property
    def Settings(self) -> QSettings:
        return self._qsettings

    @Settings.setter
    def Settings(self, value: QSettings) -> None:
        self._qsettings = value

    @property
    def ShowAnimation(self) -> ShowAnimation:
        return self._showAnimation

    @ShowAnimation.setter
    def ShowAnimation(self, value: ShowAnimation | str) -> None:
        self._showAnimation = self._coerceShowAnimation(value)

    @property
    def ShowAnimationDurationMs(self) -> int:
        return self._showAnimationDurationMs

    @ShowAnimationDurationMs.setter
    def ShowAnimationDurationMs(self, value: int) -> None:
        self._showAnimationDurationMs = max(0, int(value))

    # ------------------------------------------------------------------ events
    def closeEvent(self, event) -> None:
        self.saveWindowState()
        super().closeEvent(event)

    # ------------------------------------------------------------------ private helpers
    @staticmethod
    def _coerceShowAnimation(value: ShowAnimation | str) -> ShowAnimation:
        if isinstance(value, ShowAnimation):
            return value
        lNormalized = str(value).strip().lower().replace("_", "").replace("-", "")
        lMap = {
            "popup": ShowAnimation.Popup,
            "slideright": ShowAnimation.SlideRight,
            "slideleft": ShowAnimation.SlideLeft,
            "slidetop": ShowAnimation.SlideTop,
            "slidedown": ShowAnimation.SlideDown,
        }
        return lMap.get(lNormalized, ShowAnimation.Popup)

    def _screenGeometry(self) -> QRect:
        lScreen = self.screen() or QGuiApplication.primaryScreen()
        if lScreen is None:
            return QRect(0, 0, 1920, 1080)
        return lScreen.availableGeometry()

    def _ensureTargetGeometry(self) -> QRect:
        """Return the final on-screen geometry; size is fixed for the whole animation."""
        lGeo = self.geometry()
        if lGeo.width() <= 1 or lGeo.height() <= 1:
            lHint = self.sizeHint()
            if lHint.width() <= 1 or lHint.height() <= 1:
                lHint = QSize(800, 600)
            lScreen = self._screenGeometry()
            lX = lScreen.x() + max(0, (lScreen.width() - lHint.width()) // 2)
            lY = lScreen.y() + max(0, (lScreen.height() - lHint.height()) // 2)
            lGeo = QRect(lX, lY, lHint.width(), lHint.height())
        return QRect(lGeo)

    def _startPos(self, target: QRect) -> QPoint:
        lScreen = self._screenGeometry()
        lAnim = self._showAnimation

        if lAnim is ShowAnimation.SlideRight:
            return QPoint(lScreen.right() + 4, target.y())
        if lAnim is ShowAnimation.SlideLeft:
            return QPoint(lScreen.left() - target.width() - 4, target.y())
        if lAnim is ShowAnimation.SlideTop:
            return QPoint(target.x(), lScreen.top() - target.height() - 4)
        if lAnim is ShowAnimation.SlideDown:
            return QPoint(target.x(), lScreen.bottom() + 4)

        # Popup: same position — only opacity is animated
        return target.topLeft()

    def _stopRunningAnimations(self) -> None:
        if self._showAnimGroup is not None:
            self._showAnimGroup.stop()
            self._showAnimGroup.deleteLater()
            self._showAnimGroup = None

    def _onShowAnimationFinished(self) -> None:
        self._showAnimationRunning = False
        self.setWindowOpacity(1.0)
        self._showAnimGroup = None

    def _runShowAnimation(self) -> None:
        self._stopRunningAnimations()
        self._showAnimationRunning = True

        lTarget = self._ensureTargetGeometry()
        lStartPos = self._startPos(lTarget)
        lEndPos = lTarget.topLeft()
        lDuration = self._showAnimationDurationMs
        lIsPopup = self._showAnimation is ShowAnimation.Popup

        # Lock size once; only pos / opacity will change during the animation
        self.setFixedSize(lTarget.size())
        self.move(lStartPos)
        self.setWindowOpacity(0.0 if lIsPopup else 1.0)

        # Map the window before starting animations (required for compositor opacity)
        super().show()
        self.raise_()

        lCurve = QEasingCurve(QEasingCurve.Type.OutCubic)
        lGroup = QParallelAnimationGroup(self)
        self._showAnimGroup = lGroup

        if not lIsPopup:
            lPosAnim = QPropertyAnimation(self, b"pos", self)
            lPosAnim.setDuration(lDuration)
            lPosAnim.setStartValue(lStartPos)
            lPosAnim.setEndValue(lEndPos)
            lPosAnim.setEasingCurve(lCurve)
            # Keep animation on the render thread's vsync-ish pacing
            lPosAnim.setUpdateInterval(0)
            lGroup.addAnimation(lPosAnim)

        lOpacityAnim = QPropertyAnimation(self, b"windowOpacity", self)
        lOpacityAnim.setDuration(lDuration)
        lOpacityAnim.setStartValue(0.0 if lIsPopup else 0.85)
        lOpacityAnim.setEndValue(1.0)
        lOpacityAnim.setEasingCurve(lCurve)
        lOpacityAnim.setUpdateInterval(0)
        lGroup.addAnimation(lOpacityAnim)

        def _finish() -> None:
            # Release fixed size so the window can be resized normally afterwards
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            self.setGeometry(lTarget)
            self.setWindowOpacity(1.0)
            self._onShowAnimationFinished()

        lGroup.finished.connect(_finish)
        lGroup.start()
