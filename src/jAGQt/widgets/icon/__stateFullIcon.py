# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import Enum
from typing import Dict, Optional, Union

# ==================================================================================
from PySide6.QtGui import QColor, QIcon, QPixmap

# ==================================================================================
from ...icons.animations import IconMorphAnimation
from ...types.interface.icons.animation import iIconAnimation
from .__icon import Icon


# ==================================================================================
class StatefullIcon[T: Enum](Icon):
    def __init__(
        self,
        icons: Dict[T, Optional[Union[QIcon, QPixmap, str]]] = {},
        background: Optional[Union[str, QColor]] = None,
        foreground: Optional[Union[str, QColor]] = None,
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
        self._state: T = lInitialState
        self._applyingFrame: bool = False

        self._switchAnimation: Optional[iIconAnimation] = None
        if len(lKeys) > 1:
            lStart: Optional[Union[QIcon, QPixmap, str]] = icons[lKeys[0]]
            lEnd: Optional[Union[QIcon, QPixmap, str]] = icons[lKeys[1]]
            self._switchAnimation = IconMorphAnimation(
                startIcon=lStart,
                endIcon=lEnd,
                target=self,
            )

    @property
    def state(self) -> T:
        return self._state

    @state.setter
    def state(self, state: T) -> None:
        if state == self._state:
            return
        if state not in self._icons:
            raise KeyError(f"No icon registered for state {state!r}")
        lNewIcon: Optional[Union[QIcon, QPixmap, str]] = self._icons[state]
        self.setIcon(lNewIcon)
        self._state = state

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]) -> None:
        # Animation frames must paint without starting another morph.
        if self._applyingFrame:
            super().setIcon(icon)
            return

        switchAnimation = self._switchAnimation
        if switchAnimation is None:
            super().setIcon(icon)
            return

        if switchAnimation.isRunning:
            switchAnimation.stop()

        lCurrent: Optional[Union[QIcon, QPixmap, str]] = self._icons.get(self._state)
        switchAnimation.setIcons(lCurrent, icon)
        switchAnimation.start()

    def applyFrame(self, icon: Optional[Union[QIcon, QPixmap, str]]) -> None:
        """Apply a morph frame without re-entering the switch animation."""
        self._applyingFrame = True
        try:
            super().setIcon(icon)
        finally:
            self._applyingFrame = False

    def addIcon(self, state: T, icon: Optional[Union[QIcon, QPixmap, str]] = None) -> None:
        self._icons[state] = icon
        if state == self._state:
            self.setIcon(icon)

    def removeIcon(self, state: T) -> None:
        if state not in self._icons:
            return
        del self._icons[state]
        if not self._icons:
            raise ValueError("StatefullIcon must retain at least one icon")
        if state == self._state:
            self.state = list(self._icons.keys())[0]
