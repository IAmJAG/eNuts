# ==================================================================================
# src/jAGQt/window/__mainWindowBase.py
# ==================================================================================
from enum import Enum
from typing import Optional

# ==================================================================================
from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSettings,
    QSize,
    Qt,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QGraphicsOpacityEffect

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
        *,
        showAnimation: ShowAnimation | str = ShowAnimation.Popup,
        showAnimationDurationMs: int = 320,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name, frameless, *args, **kwargs)
        self._showAnimation: ShowAnimation = self._coerceShowAnimation(showAnimation)
        self._showAnimationDurationMs: int = max(0, int(showAnimationDurationMs))
        self._showAnimationRunning: bool = False
        self._opacityEffect: Optional[QGraphicsOpacityEffect] = None
        self._geometryAnimation: Optional[QPropertyAnimation] = None
        self._opacityAnimation: Optional[QPropertyAnimation] = None

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
    def Settings(self, value: QSettings):
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

    def _targetGeometry(self) -> QRect:
        lGeo = self.geometry()
        if lGeo.width() <= 0 or lGeo.height() <= 0:
            lHint = self.sizeHint()
            if lHint.width() <= 0 or lHint.height() <= 0:
                lHint = QSize(800, 600)
            lScreen = self._screenGeometry()
            lX = lScreen.x() + max(0, (lScreen.width() - lHint.width()) // 2)
            lY = lScreen.y() + max(0, (lScreen.height() - lHint.height()) // 2)
            lGeo = QRect(lX, lY, lHint.width(), lHint.height())
            self.setGeometry(lGeo)
        return QRect(lGeo)

    def _startGeometry(self, target: QRect) -> QRect:
        lScreen = self._screenGeometry()
        lAnim = self._showAnimation

        if lAnim is ShowAnimation.SlideRight:
            return QRect(lScreen.right() + 8, target.y(), target.width(), target.height())
        if lAnim is ShowAnimation.SlideLeft:
            return QRect(lScreen.left() - target.width() - 8, target.y(), target.width(), target.height())
        if lAnim is ShowAnimation.SlideTop:
            return QRect(target.x(), lScreen.top() - target.height() - 8, target.width(), target.height())
        if lAnim is ShowAnimation.SlideDown:
            return QRect(target.x(), lScreen.bottom() + 8, target.width(), target.height())

        # Popup: start slightly smaller / same center (scale is approximated via geometry)
        lCx = target.center().x()
        lCy = target.center().y()
        lW = max(1, int(target.width() * 0.85))
        lH = max(1, int(target.height() * 0.85))
        return QRect(lCx - lW // 2, lCy - lH // 2, lW, lH)

    def _ensureOpacityEffect(self) -> QGraphicsOpacityEffect:
        if self._opacityEffect is None:
            self._opacityEffect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self._opacityEffect)
        return self._opacityEffect

    def _stopRunningAnimations(self) -> None:
        if self._geometryAnimation is not None:
            self._geometryAnimation.stop()
            self._geometryAnimation = None
        if self._opacityAnimation is not None:
            self._opacityAnimation.stop()
            self._opacityAnimation = None

    def _onShowAnimationFinished(self) -> None:
        self._showAnimationRunning = False
        if self._opacityEffect is not None:
            self._opacityEffect.setOpacity(1.0)

    def _runShowAnimation(self) -> None:
        self._stopRunningAnimations()
        self._showAnimationRunning = True

        lTarget = self._targetGeometry()
        lStart = self._startGeometry(lTarget)

        self.setGeometry(lStart)
        self.setWindowOpacity(1.0)

        lEffect = self._ensureOpacityEffect()
        lEffect.setOpacity(0.0 if self._showAnimation is ShowAnimation.Popup else 1.0)

        # Show first so the window is mapped, then animate into place
        super().show()

        lDuration = self._showAnimationDurationMs
        lCurve = QEasingCurve.Type.OutCubic

        self._geometryAnimation = QPropertyAnimation(self, b"geometry", self)
        self._geometryAnimation.setDuration(lDuration)
        self._geometryAnimation.setStartValue(lStart)
        self._geometryAnimation.setEndValue(lTarget)
        self._geometryAnimation.setEasingCurve(lCurve)

        if self._showAnimation is ShowAnimation.Popup:
            self._opacityAnimation = QPropertyAnimation(lEffect, b"opacity", self)
            self._opacityAnimation.setDuration(lDuration)
            self._opacityAnimation.setStartValue(0.0)
            self._opacityAnimation.setEndValue(1.0)
            self._opacityAnimation.setEasingCurve(lCurve)
            self._opacityAnimation.start()

        self._geometryAnimation.finished.connect(self._onShowAnimationFinished)
        self._geometryAnimation.start()
