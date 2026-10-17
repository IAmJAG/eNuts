# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Tuple

# ==================================================================================
from .__optionsBase import OptionsBase

# ==================================================================================
C_DEFAULT_EXPANDED_WIDTH: int = 200
C_DEFAULT_COLLAPSED_WIDTH: int = 48
C_DEFAULT_NAME: str = "SideBar"
C_DEFAULT_MENU_ICON_SIZE: int = 20
C_DEFAULT_MENU_HEADER_MARGIN: Tuple[int, int, int, int] = (8, 8, 8, 8)
C_DEFAULT_MENU_LEAF_MARGIN: Tuple[int, int, int, int] = (28, 6, 8, 6)
# ==================================================================================


# ==================================================================================
class SideBarOptions(OptionsBase):
    """Configuration settings for :class:`~jAGQt.widgets.SideBar.SideBar`.

    Chrome widths + optional animation class name, plus **menu row metrics**
    (header/leaf margins and icon size) applied in code — not via QSS sizing.
    """

    def __init__(
        self,
        name: str = C_DEFAULT_NAME,
        version: int = 1,
        description: str = "",
        expandedWidth: int = C_DEFAULT_EXPANDED_WIDTH,
        collapsedWidth: int = C_DEFAULT_COLLAPSED_WIDTH,
        animation: Optional[str] = None,
        menuIconSize: int = C_DEFAULT_MENU_ICON_SIZE,
        menuHeaderMarginLeft: int = C_DEFAULT_MENU_HEADER_MARGIN[0],
        menuHeaderMarginTop: int = C_DEFAULT_MENU_HEADER_MARGIN[1],
        menuHeaderMarginRight: int = C_DEFAULT_MENU_HEADER_MARGIN[2],
        menuHeaderMarginBottom: int = C_DEFAULT_MENU_HEADER_MARGIN[3],
        menuLeafMarginLeft: int = C_DEFAULT_MENU_LEAF_MARGIN[0],
        menuLeafMarginTop: int = C_DEFAULT_MENU_LEAF_MARGIN[1],
        menuLeafMarginRight: int = C_DEFAULT_MENU_LEAF_MARGIN[2],
        menuLeafMarginBottom: int = C_DEFAULT_MENU_LEAF_MARGIN[3],
    ) -> None:
        super().__init__(name=name or C_DEFAULT_NAME, version=version, description=description)
        self._expandedWidth: int = int(expandedWidth)
        self._collapsedWidth: int = int(collapsedWidth)
        self._animation: Optional[str] = animation if animation else None
        self._menuIconSize: int = int(menuIconSize)
        self._menuHeaderMarginLeft: int = int(menuHeaderMarginLeft)
        self._menuHeaderMarginTop: int = int(menuHeaderMarginTop)
        self._menuHeaderMarginRight: int = int(menuHeaderMarginRight)
        self._menuHeaderMarginBottom: int = int(menuHeaderMarginBottom)
        self._menuLeafMarginLeft: int = int(menuLeafMarginLeft)
        self._menuLeafMarginTop: int = int(menuLeafMarginTop)
        self._menuLeafMarginRight: int = int(menuLeafMarginRight)
        self._menuLeafMarginBottom: int = int(menuLeafMarginBottom)
        self.Properties.extend(
            [
                "expandedWidth",
                "collapsedWidth",
                "animation",
                "menuIconSize",
                "menuHeaderMarginLeft",
                "menuHeaderMarginTop",
                "menuHeaderMarginRight",
                "menuHeaderMarginBottom",
                "menuLeafMarginLeft",
                "menuLeafMarginTop",
                "menuLeafMarginRight",
                "menuLeafMarginBottom",
            ]
        )
        self._validateWidths()
        self._validateMenuMetrics()

    def _validateWidths(self) -> None:
        if self._expandedWidth <= 0:
            raise ValueError(f"expandedWidth must be > 0, got {self._expandedWidth}")
        if self._collapsedWidth <= 0:
            raise ValueError(f"collapsedWidth must be > 0, got {self._collapsedWidth}")

    def _validateMenuMetrics(self) -> None:
        if self._menuIconSize <= 0:
            raise ValueError(f"menuIconSize must be > 0, got {self._menuIconSize}")

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

    @property
    def menuIconSize(self) -> int:
        return self._menuIconSize

    @menuIconSize.setter
    def menuIconSize(self, value: int) -> None:
        self._menuIconSize = int(value)
        self._validateMenuMetrics()

    @property
    def menuHeaderMarginLeft(self) -> int:
        return self._menuHeaderMarginLeft

    @menuHeaderMarginLeft.setter
    def menuHeaderMarginLeft(self, value: int) -> None:
        self._menuHeaderMarginLeft = int(value)

    @property
    def menuHeaderMarginTop(self) -> int:
        return self._menuHeaderMarginTop

    @menuHeaderMarginTop.setter
    def menuHeaderMarginTop(self, value: int) -> None:
        self._menuHeaderMarginTop = int(value)

    @property
    def menuHeaderMarginRight(self) -> int:
        return self._menuHeaderMarginRight

    @menuHeaderMarginRight.setter
    def menuHeaderMarginRight(self, value: int) -> None:
        self._menuHeaderMarginRight = int(value)

    @property
    def menuHeaderMarginBottom(self) -> int:
        return self._menuHeaderMarginBottom

    @menuHeaderMarginBottom.setter
    def menuHeaderMarginBottom(self, value: int) -> None:
        self._menuHeaderMarginBottom = int(value)

    @property
    def menuLeafMarginLeft(self) -> int:
        return self._menuLeafMarginLeft

    @menuLeafMarginLeft.setter
    def menuLeafMarginLeft(self, value: int) -> None:
        self._menuLeafMarginLeft = int(value)

    @property
    def menuLeafMarginTop(self) -> int:
        return self._menuLeafMarginTop

    @menuLeafMarginTop.setter
    def menuLeafMarginTop(self, value: int) -> None:
        self._menuLeafMarginTop = int(value)

    @property
    def menuLeafMarginRight(self) -> int:
        return self._menuLeafMarginRight

    @menuLeafMarginRight.setter
    def menuLeafMarginRight(self, value: int) -> None:
        self._menuLeafMarginRight = int(value)

    @property
    def menuLeafMarginBottom(self) -> int:
        return self._menuLeafMarginBottom

    @menuLeafMarginBottom.setter
    def menuLeafMarginBottom(self, value: int) -> None:
        self._menuLeafMarginBottom = int(value)

    def menuHeaderMargins(self) -> Tuple[int, int, int, int]:
        return (
            self._menuHeaderMarginLeft,
            self._menuHeaderMarginTop,
            self._menuHeaderMarginRight,
            self._menuHeaderMarginBottom,
        )

    def menuLeafMargins(self) -> Tuple[int, int, int, int]:
        return (
            self._menuLeafMarginLeft,
            self._menuLeafMarginTop,
            self._menuLeafMarginRight,
            self._menuLeafMarginBottom,
        )
