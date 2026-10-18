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
C_DEFAULT_MENU_ICON_SIZE: int = 22
C_DEFAULT_MENU_CHILD_ICON_SIZE: int = 16
C_DEFAULT_MENU_FONT_PT: int = 12
C_DEFAULT_MENU_CHILD_FONT_PT: int = 10
C_DEFAULT_MENU_ITEM_MARGIN: Tuple[int, int, int, int] = (8, 8, 8, 8)
C_DEFAULT_MENU_CHILD_INDENT: int = 20
# ==================================================================================


# ==================================================================================
class SideBarOptions(OptionsBase):
    """Configuration for :class:`~jAGQt.widgets.SideBar.SideBar`.

    Hierarchy (not role) drives visual weight:
    - root rows: ``menuIconSize`` / ``menuFontPt`` / bold
    - child rows: ``menuChildIconSize`` / ``menuChildFontPt`` / normal
    - indent: ``menuChildIndent`` when ``ParentItem`` is set
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
        menuChildIconSize: int = C_DEFAULT_MENU_CHILD_ICON_SIZE,
        menuFontPt: int = C_DEFAULT_MENU_FONT_PT,
        menuChildFontPt: int = C_DEFAULT_MENU_CHILD_FONT_PT,
        menuItemMarginLeft: int = C_DEFAULT_MENU_ITEM_MARGIN[0],
        menuItemMarginTop: int = C_DEFAULT_MENU_ITEM_MARGIN[1],
        menuItemMarginRight: int = C_DEFAULT_MENU_ITEM_MARGIN[2],
        menuItemMarginBottom: int = C_DEFAULT_MENU_ITEM_MARGIN[3],
        menuChildIndent: int = C_DEFAULT_MENU_CHILD_INDENT,
    ) -> None:
        super().__init__(name=name or C_DEFAULT_NAME, version=version, description=description)
        self._expandedWidth: int = int(expandedWidth)
        self._collapsedWidth: int = int(collapsedWidth)
        self._animation: Optional[str] = animation if animation else None
        self._menuIconSize: int = int(menuIconSize)
        self._menuChildIconSize: int = int(menuChildIconSize)
        self._menuFontPt: int = int(menuFontPt)
        self._menuChildFontPt: int = int(menuChildFontPt)
        self._menuItemMarginLeft: int = int(menuItemMarginLeft)
        self._menuItemMarginTop: int = int(menuItemMarginTop)
        self._menuItemMarginRight: int = int(menuItemMarginRight)
        self._menuItemMarginBottom: int = int(menuItemMarginBottom)
        self._menuChildIndent: int = int(menuChildIndent)
        self.Properties.extend(
            [
                "expandedWidth",
                "collapsedWidth",
                "animation",
                "menuIconSize",
                "menuChildIconSize",
                "menuFontPt",
                "menuChildFontPt",
                "menuItemMarginLeft",
                "menuItemMarginTop",
                "menuItemMarginRight",
                "menuItemMarginBottom",
                "menuChildIndent",
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
        if self._menuChildIconSize <= 0:
            raise ValueError(
                f"menuChildIconSize must be > 0, got {self._menuChildIconSize}"
            )
        if self._menuFontPt <= 0:
            raise ValueError(f"menuFontPt must be > 0, got {self._menuFontPt}")
        if self._menuChildFontPt <= 0:
            raise ValueError(
                f"menuChildFontPt must be > 0, got {self._menuChildFontPt}"
            )
        if self._menuChildIndent < 0:
            raise ValueError(f"menuChildIndent must be >= 0, got {self._menuChildIndent}")

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
    def menuChildIconSize(self) -> int:
        return self._menuChildIconSize

    @menuChildIconSize.setter
    def menuChildIconSize(self, value: int) -> None:
        self._menuChildIconSize = int(value)
        self._validateMenuMetrics()

    @property
    def menuFontPt(self) -> int:
        return self._menuFontPt

    @menuFontPt.setter
    def menuFontPt(self, value: int) -> None:
        self._menuFontPt = int(value)
        self._validateMenuMetrics()

    @property
    def menuChildFontPt(self) -> int:
        return self._menuChildFontPt

    @menuChildFontPt.setter
    def menuChildFontPt(self, value: int) -> None:
        self._menuChildFontPt = int(value)
        self._validateMenuMetrics()

    @property
    def menuItemMarginLeft(self) -> int:
        return self._menuItemMarginLeft

    @menuItemMarginLeft.setter
    def menuItemMarginLeft(self, value: int) -> None:
        self._menuItemMarginLeft = int(value)

    @property
    def menuItemMarginTop(self) -> int:
        return self._menuItemMarginTop

    @menuItemMarginTop.setter
    def menuItemMarginTop(self, value: int) -> None:
        self._menuItemMarginTop = int(value)

    @property
    def menuItemMarginRight(self) -> int:
        return self._menuItemMarginRight

    @menuItemMarginRight.setter
    def menuItemMarginRight(self, value: int) -> None:
        self._menuItemMarginRight = int(value)

    @property
    def menuItemMarginBottom(self) -> int:
        return self._menuItemMarginBottom

    @menuItemMarginBottom.setter
    def menuItemMarginBottom(self, value: int) -> None:
        self._menuItemMarginBottom = int(value)

    @property
    def menuChildIndent(self) -> int:
        return self._menuChildIndent

    @menuChildIndent.setter
    def menuChildIndent(self, value: int) -> None:
        self._menuChildIndent = int(value)
        self._validateMenuMetrics()

    def menuItemMargins(self) -> Tuple[int, int, int, int]:
        return (
            self._menuItemMarginLeft,
            self._menuItemMarginTop,
            self._menuItemMarginRight,
            self._menuItemMarginBottom,
        )
