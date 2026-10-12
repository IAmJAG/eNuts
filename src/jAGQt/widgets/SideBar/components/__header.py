# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.icons import MakeBurgerIcon, MakeCloseIcon
from jAGQt.icons.animations import IconMorphAnimation

# ==================================================================================
from ....utilities import newLayout
from ...components import ComponentBase

# ==================================================================================
from .__icon import Icon as SideBarIcon
from .__text import Text as SideBarText

# ==================================================================================
QPolicy = QSizePolicy.Policy
# ==================================================================================


# ==================================================================================
@workflow
class Header(QWidget, ComponentBase):
    OBJECT_NAME = "W_HEADER"
    CollapseRequested = Signal()

    def __init__(
        self, title: str = "", iconSize: int = 20,
        spacing: int = 8, *args, **kwargs,
    ) -> None:
        OBJNAME: str = kwargs.pop("objectName", self.OBJECT_NAME)
        super().__init__(objectName=OBJNAME, *args, **kwargs)
        self._title: str = title if title is not None else ""
        self._iconSize: int = max(1, int(iconSize))
        self._spacing: int = int(spacing)

    def _wInitializeUI(self) -> None:
        title: str = self._title if self._title is not None else ""
        iconSize: int = max(1, int(self._iconSize))
        spacing: int = int(self._spacing)

        del self._title
        del self._iconSize
        del self._spacing

        self._collapsed: bool = False

        self.setSizePolicy(QPolicy.Expanding, QPolicy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._burgerIcon: QIcon = MakeBurgerIcon(iconSize)
        self._closeIcon: QIcon = MakeCloseIcon(iconSize)

        self._toggleIcon: SideBarIcon = SideBarIcon(
            icon=self._burgerIcon,
            iconSize=iconSize,
            parent=self,
        )
        self._toggleIcon.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggleIcon.installEventFilter(self)

        self._titleWidget: SideBarText = SideBarText(text=title, parent=self)
        self._titleWidget.setObjectName("SideBarHeaderTitle")

        mainLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=spacing,
            margins=(8, 8, 8, 8),
            direction=QBoxLayout.Direction.LeftToRight,
        )
        mainLayout.addWidget(self._toggleIcon)
        mainLayout.addWidget(self._titleWidget, 1)
        self.setLayout(mainLayout)

        self._morph: IconMorphAnimation = IconMorphAnimation(
            target=self._toggleIcon,
            iconSize=iconSize,
            durationMs=160,
            parent=self,
        )
        self._applyCollapsedVisual(animate=False, deferTitleHide=False)

    # ==================================================================================
    def prepareCollapse(self, animateIcon: bool = True) -> None:
        """Start icon morph only; keep title visible until width animation ends."""
        # Morph toward the collapsed icon while title stays in layout.
        lStart: QIcon = self._burgerIcon if not self._collapsed else self._closeIcon
        lEnd: QIcon = self._closeIcon
        if animateIcon:
            self._morph.setIcons(lStart, lEnd)
            self._morph.start()
        else:
            self._toggleIcon.setIcon(lEnd)

    def _setCollapsed(
        self,
        collapsed: bool,
        animate: bool = True,
        *,
        deferTitleHide: bool = False,
    ) -> None:
        lValue: bool = bool(collapsed)
        if lValue is self._collapsed:
            if lValue and not deferTitleHide and self._titleWidget.isVisible():
                self._titleWidget.setVisible(False)
            return
        self._collapsed = lValue
        self._applyCollapsedVisual(animate=animate, deferTitleHide=deferTitleHide)

    def finalizeTitleVisibility(self) -> None:
        self._titleWidget.setVisible(not self._collapsed)

    # ==================================================================================
    @property
    def title(self) -> str:
        return self._titleWidget.Text

    @title.setter
    def title(self, value: str) -> None:
        self._titleWidget.Text = value if value is not None else ""

    @property
    def iconSize(self) -> int:
        return self._toggleIcon.iconSize

    @iconSize.setter
    def iconSize(self, value: int) -> None:
        lSize: int = max(1, int(value))
        if lSize == self._toggleIcon.iconSize:
            return
        self._toggleIcon.iconSize = lSize
        self._burgerIcon = MakeBurgerIcon(lSize)
        self._closeIcon = MakeCloseIcon(lSize)
        self._morph.setIconSize(lSize)
        self._refreshToggleIcon(animate=False)

    @property
    def collapsed(self) -> bool:
        return self._collapsed

    @collapsed.setter
    def collapsed(self, value: bool) -> None:
        self._setCollapsed(value)

    # ==================================================================================
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            watched is self._toggleIcon
            and event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.CollapseRequested.emit()
            return True
        return super().eventFilter(watched, event)

    def _refreshToggleIcon(self, animate: bool = True) -> None:
        lStart: QIcon = self._closeIcon if not self._collapsed else self._burgerIcon
        lEnd: QIcon = self._closeIcon if self._collapsed else self._burgerIcon
        if animate:
            self._morph.setIcons(lStart, lEnd)
            self._morph.start()
        else:
            self._toggleIcon.setIcon(lEnd)

    def _applyCollapsedVisual(
        self, animate: bool = True, deferTitleHide: bool = False,
    ) -> None:
        self._refreshToggleIcon(animate=animate)

        if self._collapsed:
            if not deferTitleHide:
                self._titleWidget.setVisible(False)
        else:
            self._titleWidget.setVisible(True)

        self.setProperty("collapsed", "true" if self._collapsed else "false")
        self.style().unpolish(self)
        self.style().polish(self)
