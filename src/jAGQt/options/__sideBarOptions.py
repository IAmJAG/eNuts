# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from .__optionsBase import OptionsBase

# ==================================================================================
C_DEFAULT_EXPANDED_WIDTH: int = 200
C_DEFAULT_COLLAPSED_WIDTH: int = 48
C_DEFAULT_NAME: str = "SideBar"
# ==================================================================================


# ==================================================================================
class SideBarOptions(OptionsBase):
    """Configuration settings for :class:`~jAGQt.widgets.SideBar.SideBar`.

    ``animation`` is a fully qualified class name string (e.g.
    ``jAGQt.animations.RubberBand``) or empty/None for no animation.
    Live animation instances are never stored here; the host resolves the class
    at apply time and keeps the instance on its own properties.
    """

    def __init__(
        self,
        name: str = C_DEFAULT_NAME,
        version: int = 1,
        description: str = "",
        expandedWidth: int = C_DEFAULT_EXPANDED_WIDTH,
        collapsedWidth: int = C_DEFAULT_COLLAPSED_WIDTH,
        animation: Optional[str] = None,
    ) -> None:
        super().__init__(name=name or C_DEFAULT_NAME, version=version, description=description)
        self._expandedWidth: int = int(expandedWidth)
        self._collapsedWidth: int = int(collapsedWidth)
        self._animation: Optional[str] = animation if animation else None
        self.Properties.extend(["expandedWidth", "collapsedWidth", "animation"])
        self._validateWidths()

    def _validateWidths(self) -> None:
        if self._expandedWidth <= 0:
            raise ValueError(f"expandedWidth must be > 0, got {self._expandedWidth}")
        if self._collapsedWidth <= 0:
            raise ValueError(f"collapsedWidth must be > 0, got {self._collapsedWidth}")

    # ==================================================================================
    @property
    def expandedWidth(self) -> int:
        return self._expandedWidth

    @expandedWidth.setter
    def expandedWidth(self, value: int) -> None:
        self._expandedWidth = int(value)
        self._validateWidths()

    @property
    def collapsedWidth(self) -> int:
        return self._collapsedWidth

    @collapsedWidth.setter
    def collapsedWidth(self, value: int) -> None:
        self._collapsedWidth = int(value)
        self._validateWidths()

    @property
    def animation(self) -> Optional[str]:
        return self._animation

    @animation.setter
    def animation(self, value: Optional[str]) -> None:
        if value is None or (isinstance(value, str) and not value.strip()):
            self._animation = None
        else:
            self._animation = str(value).strip()
