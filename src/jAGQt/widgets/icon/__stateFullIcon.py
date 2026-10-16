# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import Enum
from traceback import format_exc
from typing import Dict, List, Optional, Union

# ==================================================================================
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPixmap

# ==================================================================================
from jAGQt.animations import WipeTransition, eWipeMode

# ==================================================================================
from .__icon import Icon

# ==================================================================================
C_DEFAULT_WIPE_MS = 220
# ==================================================================================


# ==================================================================================
class StatefullIcon[T: Enum](Icon):
    """Multi-state icon; left-click cycles states with WipeTransition."""

    stateChanged = Signal(object)  # new state (Enum member)

    def __init__(
        self,
        icons: Dict[T, Optional[Union[QIcon, QPixmap, str]]] = {},
        background: Optional[Union[str, QColor]] = None,
        foreground: Optional[Union[str, QColor]] = None,
        wipeEnabled: bool = True,
        wipeMode: eWipeMode = eWipeMode.Horizontal,
        wipeDurationMs: int = C_DEFAULT_WIPE_MS,
        *args,
        **kwargs,
    ) -> None:
        if icons is None or len(icons) == 0:
            raise ValueError("icons must not be None or empty")

        lKeys = list(icons.keys())
        lInitialState: T = lKeys[0]
        lInitialIcon: Optional[Union[QIcon, QPixmap, str]] = icons[lInitialState]

        super().__init__(lInitialIcon, background, foreground, *args, **kwargs)
        self._icons: Dict[T, Optional[Union[QIcon, QPixmap, str]]] = dict(icons)
        self._stateOrder: List[T] = list(lKeys)
        self._state: T = lInitialState
        self._wipeEnabled: bool = wipeEnabled
        self._wipeMode: eWipeMode = wipeMode
        self._wipeDurationMs: int = wipeDurationMs
        self._transition: Optional[WipeTransition] = None
        self._pendingIcon: Optional[Union[QIcon, QPixmap, str]] = None
        self._animating: bool = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # ==================================================================================
    def _ensureTransition(self) -> WipeTransition:
        if self._transition is None:
            self._transition = WipeTransition(
                target=self,
                mode=self._wipeMode,
                durationMs=self._wipeDurationMs,
                parent=self,
            )
            self._transition.finished.connect(self._onWipeFinished)
            self._transition.stopped.connect(self._onWipeStopped)
        else:
            self._transition.mode = self._wipeMode
            self._transition.durationMs = self._wipeDurationMs
        return self._transition

    def _iconToPixmap(
        self, icon: Optional[Union[QIcon, QPixmap, str]]
    ) -> QPixmap:
        if icon is None:
            return QPixmap()
        if isinstance(icon, QPixmap):
            return icon
        if isinstance(icon, str):
            return QPixmap(icon)
        if isinstance(icon, QIcon):
            size = self.size()
            if size.isEmpty() or size.width() <= 0 or size.height() <= 0:
                size = QSize(24, 24)
            return icon.pixmap(size)
        return QPixmap()

    def _nextState(self) -> T:
        if len(self._stateOrder) < 2:
            return self._state
        idx = self._stateOrder.index(self._state)
        return self._stateOrder[(idx + 1) % len(self._stateOrder)]

    def _runWipeToState(self, state: T) -> None:
        if state not in self._icons:
            raise KeyError(f"No icon registered for state {state!r}")

        previous = self._state
        targetIcon = self._icons[state]
        self._pendingIcon = targetIcon
        self._state = state

        if not self._wipeEnabled or len(self._stateOrder) < 2:
            self._animating = False
            super().setIcon(targetIcon)
            self._pendingIcon = None
            if previous != state:
                self.stateChanged.emit(state)
            return

        try:
            transition = self._ensureTransition()
            if transition.isRunning:
                transition.stop()

            targetPx = self._iconToPixmap(targetIcon)
            self._animating = True
            transition.start(targetImage=targetPx, originalImage=None)
            if previous != state:
                self.stateChanged.emit(state)
        except Exception as ex:
            error("[StatefullIcon] _runWipeToState FAIL", ex)
            error(f"[StatefullIcon] traceback:\n{format_exc()}")
            self._animating = False
            super().setIcon(targetIcon)
            self._pendingIcon = None
            if previous != state:
                self.stateChanged.emit(state)
            raise

    def _onWipeFinished(self) -> None:
        try:
            if self._pendingIcon is not None:
                self._animating = False
                super().setIcon(self._pendingIcon)
                self._pendingIcon = None
            else:
                self._animating = False
        except Exception as ex:
            error("[StatefullIcon] _onWipeFinished FAIL", ex)
            error(f"[StatefullIcon] traceback:\n{format_exc()}")
            self._animating = False
            raise

    def _onWipeStopped(self) -> None:
        self._animating = False

    # ==================================================================================
    def mousePressEvent(self, event: QMouseEvent) -> None:
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                if self._animating:
                    event.accept()
                    return
                nextState = self._nextState()
                if nextState != self._state:
                    verbose(
                        f"[StatefullIcon] click {self._state!r} -> {nextState!r}"
                    )
                    self._runWipeToState(nextState)
                event.accept()
                return
            super().mousePressEvent(event)
        except Exception as ex:
            error("[StatefullIcon] mousePressEvent FAIL", ex)
            error(f"[StatefullIcon] traceback:\n{format_exc()}")
            raise

    # ==================================================================================
    @property
    def state(self) -> T:
        return self._state

    @state.setter
    def state(self, state: T) -> None:
        if state == self._state:
            return
        if state not in self._icons:
            raise KeyError(f"No icon registered for state {state!r}")
        self._runWipeToState(state)

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]) -> None:
        if self._animating and self._transition is not None and self._transition.isRunning:
            self._transition.stop()
            self._animating = False
        self._pendingIcon = None
        super().setIcon(icon)

    def addIcon(self, state: T, icon: Optional[Union[QIcon, QPixmap, str]] = None) -> None:
        self._icons[state] = icon
        if state not in self._stateOrder:
            self._stateOrder.append(state)
        if state == self._state and not self._animating:
            self.setIcon(icon)

    def removeIcon(self, state: T) -> None:
        if state not in self._icons:
            return
        del self._icons[state]
        if state in self._stateOrder:
            self._stateOrder.remove(state)
        if not self._icons:
            raise ValueError("StatefullIcon must retain at least one icon")
        if state == self._state:
            self._runWipeToState(self._stateOrder[0])
