# ==================================================================================
from __future__ import annotations

# ==================================================================================
from traceback import format_exc
from typing import Dict, Optional, Tuple, Type, Union

# ==================================================================================
from PySide6.QtGui import QIcon, QPixmap, QResizeEvent
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QWidget

# ==================================================================================
from jAGFx.serializer.__utilities import importClass
from jAGFx.workflow import workflow
from jAGQt.animations import SizeAnimationBase
from jAGQt.options import AnimationOptions, SideBarOptions
from jAGQt.options.__sideBarOptions import (
    C_DEFAULT_MENU_CHILD_FONT_PT,
    C_DEFAULT_MENU_CHILD_ICON_SIZE,
    C_DEFAULT_MENU_CHILD_INDENT,
    C_DEFAULT_MENU_FONT_PT,
    C_DEFAULT_MENU_ICON_SIZE,
    C_DEFAULT_MENU_ITEM_MARGIN,
)
from jAGQt.types.interface.animations import iAnimation

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase, ObjectName
from .__eSideBarState import eSideBarState
from .components import SideBarHeader
from .menu import SideBarMenu, SideBarMenuItem

# ==================================================================================
QSPolicy = QSizePolicy.Policy
C_EXPANDED_WIDTH = 200
C_COLLAPSED_WIDTH = 48
C_STATE_ANIM_MS = 280
C_WIDTH_TOLERANCE = 4
# ==================================================================================


# ==================================================================================
@workflow
class SideBar(ComponentBase, ObjectName, QWidget):
    OBJECT_NAME = "W_SIDEBAR"

    def __init__(
        self,
        icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]],
        title: str = "",
        description: str = "",
        initialState: eSideBarState = eSideBarState.Expanded,
        options: Optional[SideBarOptions] = None,
        animationOptions: Optional[AnimationOptions] = None,
        *args,
        **kwargs,
    ) -> None:
        if icons is None or len(icons) == 0:
            raise ValueError("icons must not be None or empty")

        verbose(
            f"[SideBar] __init__ ENTER title={title!r} "
            f"initialState={initialState!r} iconKeys={list(icons.keys())!r}"
        )
        try:
            super().__init__(*args, **kwargs)
            self._titleText: str = title
            self._descriptionText: str = description
            self._icons: Dict[eSideBarState, Optional[Union[QIcon, QPixmap, str]]] = (
                dict(icons)
            )
            self._initialState: eSideBarState = initialState
            self._pendingOptions: Optional[SideBarOptions] = options
            self._pendingAnimationOptions: Optional[AnimationOptions] = animationOptions

            self._expandedWidth: int = C_EXPANDED_WIDTH
            self._collapsedWidth: int = C_COLLAPSED_WIDTH
            self._animation: Optional[iAnimation] = None
            self._menuIconSize: int = C_DEFAULT_MENU_ICON_SIZE
            self._menuChildIconSize: int = C_DEFAULT_MENU_CHILD_ICON_SIZE
            self._menuFontPt: int = C_DEFAULT_MENU_FONT_PT
            self._menuChildFontPt: int = C_DEFAULT_MENU_CHILD_FONT_PT
            self._menuItemMargins: Tuple[int, int, int, int] = C_DEFAULT_MENU_ITEM_MARGIN
            self._menuChildIndent: int = C_DEFAULT_MENU_CHILD_INDENT
            self._sidebarState: eSideBarState = initialState
            self._layoutReady: bool = False
            self._content: Optional[QWidget] = None
            self._footer: Optional[QWidget] = None
            self._contentHost: Optional[QWidget] = None
            self._footerHost: Optional[QWidget] = None
        except Exception as ex:
            error("[SideBar] __init__ FAIL", ex)
            error(f"[SideBar] __init__ traceback:\n{format_exc()}")
            raise
        verbose(f"[SideBar] __init__ EXIT objectName={self.objectName()!r}")

    def _wInitializeUI(self) -> None:
        verbose("[SideBar] _wInitializeUI ENTER")
        try:
            self.setSizePolicy(QSPolicy.Fixed, QSPolicy.Expanding)

            titleText: str = self._titleText
            descriptionText: str = self._descriptionText
            icons = self._icons
            initialState: eSideBarState = self._initialState
            pendingOptions = self._pendingOptions
            pendingAnimOptions = self._pendingAnimationOptions
            del self._titleText
            del self._descriptionText
            del self._icons
            del self._initialState
            del self._pendingOptions
            del self._pendingAnimationOptions

            header: SideBarHeader = SideBarHeader(
                title=titleText,
                description=descriptionText,
                icons=icons,
                initialState=initialState,
            )

            contentHost: QWidget = QWidget(self)
            contentHost.setObjectName(f"{self.OBJECT_NAME}_CONTENT")
            contentHost.setSizePolicy(QSPolicy.Expanding, QSPolicy.Expanding)
            contentLayout: QBoxLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=(0, 0, 0, 0),
                direction=QBoxLayout.Direction.TopToBottom,
            )
            contentHost.setLayout(contentLayout)

            footerHost: QWidget = QWidget(self)
            footerHost.setObjectName(f"{self.OBJECT_NAME}_FOOTER")
            footerHost.setSizePolicy(QSPolicy.Expanding, QSPolicy.Fixed)
            footerLayout: QBoxLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=(0, 0, 0, 0),
                direction=QBoxLayout.Direction.TopToBottom,
            )
            footerHost.setLayout(footerLayout)

            outerLayout: QBoxLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=(0, 0, 0, 0),
                direction=QBoxLayout.Direction.TopToBottom,
            )
            outerLayout.addWidget(header, stretch=0)
            outerLayout.addWidget(contentHost, stretch=1)
            outerLayout.addWidget(footerHost, stretch=0)

            self.setLayout(outerLayout)
            self._layout: QBoxLayout = outerLayout
            self._header: SideBarHeader = header
            self._contentHost = contentHost
            self._contentLayout: QBoxLayout = contentLayout
            self._footerHost = footerHost
            self._footerLayout: QBoxLayout = footerLayout
            self._content = None
            self._footer = None
            self._sidebarState = initialState

            self._installOptionsFrom(pendingOptions, pendingAnimOptions)
            header.setCollapsedWidth(self._collapsedWidth)

            if self._animation is not None:
                finished = getattr(self._animation, "finished", None)
                stopped = getattr(self._animation, "stopped", None)
                if finished is not None:
                    finished.connect(self._onSizeAnimFinished)
                if stopped is not None:
                    stopped.connect(self._onSizeAnimFinished)

            header.stateChanged.connect(self._onHeaderStateChanged)

            # Force header icon + rail into the same initial state (no animation).
            if header.State is not initialState:
                header.State = initialState
            self._sidebarState = initialState
            endWidth = self._targetWidthForState(initialState)
            self.setFixedWidth(endWidth)
            # Expanded => captions on; never leave items icon-only while wide.
            self._pushChromeCollapsed(initialState is eSideBarState.Collapsed)
            self.updateGeometry()
            self._layoutReady = True

            verbose(
                f"[SideBar] _wInitializeUI EXIT "
                f"state={self._sidebarState!r} "
                f"fixedWidth={self.width()} "
                f"targetWidth={endWidth} "
                f"animation={type(self._animation).__name__ if self._animation else None}"
            )
        except Exception as ex:
            error("[SideBar] _wInitializeUI FAIL", ex)
            error(f"[SideBar] _wInitializeUI traceback:\n{format_exc()}")
            raise

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        # Keep captions aligned with the *actual* rail width.
        if self._layoutReady:
            self._syncChromeFromWidth()

    def _installOptionsFrom(
        self,
        options: Optional[SideBarOptions],
        animationOptions: Optional[AnimationOptions],
    ) -> None:
        if options is None:
            self._expandedWidth = C_EXPANDED_WIDTH
            self._collapsedWidth = C_COLLAPSED_WIDTH
            self._menuIconSize = C_DEFAULT_MENU_ICON_SIZE
            self._menuChildIconSize = C_DEFAULT_MENU_CHILD_ICON_SIZE
            self._menuFontPt = C_DEFAULT_MENU_FONT_PT
            self._menuChildFontPt = C_DEFAULT_MENU_CHILD_FONT_PT
            self._menuItemMargins = C_DEFAULT_MENU_ITEM_MARGIN
            self._menuChildIndent = C_DEFAULT_MENU_CHILD_INDENT
            className: Optional[str] = None
        else:
            self._expandedWidth = int(options.expandedWidth)
            self._collapsedWidth = int(options.collapsedWidth)
            self._menuIconSize = int(options.menuIconSize)
            self._menuChildIconSize = int(options.menuChildIconSize)
            self._menuFontPt = int(options.menuFontPt)
            self._menuChildFontPt = int(options.menuChildFontPt)
            self._menuItemMargins = options.menuItemMargins()
            self._menuChildIndent = int(options.menuChildIndent)
            className = options.animation

        self._animation = self._resolveAnimation(className, animationOptions)

    def _pushMenuMetrics(self, widget: Optional[QWidget]) -> None:
        if widget is None:
            return
        kwargs = dict(
            rootIconSize=self._menuIconSize,
            childIconSize=self._menuChildIconSize,
            rootFontPt=self._menuFontPt,
            childFontPt=self._menuChildFontPt,
            itemMargins=self._menuItemMargins,
            childIndent=self._menuChildIndent,
            collapsedWidth=self._collapsedWidth,
        )
        if isinstance(widget, SideBarMenu):
            widget.applyMetrics(**kwargs)
        elif isinstance(widget, SideBarMenuItem):
            widget.applyMetrics(**kwargs)

    def _pushChromeCollapsed(self, collapsed: bool) -> None:
        verbose(f"[SideBar] pushChrome collapsed={collapsed} width={self.width()}")
        if isinstance(self._content, SideBarMenu):
            self._content.setChromeCollapsed(collapsed)
        elif isinstance(self._content, SideBarMenuItem):
            self._content.setChromeCollapsed(collapsed)
        if isinstance(self._footer, SideBarMenuItem):
            self._footer.setChromeCollapsed(collapsed)
        self._header.setChromeCollapsed(collapsed)

    def _shouldCollapseChrome(self) -> bool:
        """Captions hide only when the rail is actually narrow (or state says so at w=0)."""
        if self._sidebarState is eSideBarState.Expanded:
            return False
        w = self.width()
        if w <= 0:
            return self._sidebarState is eSideBarState.Collapsed
        return w <= self._collapsedWidth + C_WIDTH_TOLERANCE

    def _syncChromeFromWidth(self) -> None:
        self._pushChromeCollapsed(self._shouldCollapseChrome())

    def _resolveAnimation(
        self,
        className: Optional[str],
        animationOptions: Optional[AnimationOptions],
    ) -> Optional[iAnimation]:
        if className is None or not str(className).strip():
            return None

        className = str(className).strip()
        try:
            import jAGQt.animations  # noqa: F401
        except Exception:
            pass

        cls: Optional[Type] = importClass(className)
        if cls is None:
            raise ValueError(
                f"SideBar could not resolve animation class {className!r}"
            )

        if not issubclass(cls, SizeAnimationBase):
            if not (
                hasattr(cls, "start")
                and hasattr(cls, "stop")
                and hasattr(cls, "isRunning")
            ):
                raise TypeError(
                    f"Animation class {className!r} does not satisfy iAnimation / SizeAnimationBase"
                )

        durationMs = (
            animationOptions.durationMs
            if animationOptions is not None
            else C_STATE_ANIM_MS
        )
        try:
            instance = cls(target=self, durationMs=durationMs)
        except TypeError:
            instance = cls(target=self)

        verbose(f"[SideBar] resolved animation {className!r} -> {type(instance)!r}")
        return instance

    def toOptions(self) -> SideBarOptions:
        o = SideBarOptions()
        o.expandedWidth = self._expandedWidth
        o.collapsedWidth = self._collapsedWidth
        o.menuIconSize = self._menuIconSize
        o.menuChildIconSize = self._menuChildIconSize
        o.menuFontPt = self._menuFontPt
        o.menuChildFontPt = self._menuChildFontPt
        o.menuItemMarginLeft = self._menuItemMargins[0]
        o.menuItemMarginTop = self._menuItemMargins[1]
        o.menuItemMarginRight = self._menuItemMargins[2]
        o.menuItemMarginBottom = self._menuItemMargins[3]
        o.menuChildIndent = self._menuChildIndent
        if self._animation is not None:
            t = type(self._animation)
            o.animation = f"{t.__module__}.{t.__name__}"
        else:
            o.animation = None
        return o

    def _onHeaderStateChanged(self, state: object) -> None:
        if not isinstance(state, eSideBarState):
            warning(f"[SideBar] ignoring non-eSideBarState: {state!r}")
            return
        verbose(f"[SideBar] header stateChanged -> {state!r}")
        self._syncLayoutForState(state, animate=self._layoutReady)

    def _targetWidthForState(self, state: eSideBarState) -> int:
        if state is eSideBarState.Collapsed:
            return self._collapsedWidth
        return self._expandedWidth

    def _syncLayoutForState(
        self,
        state: eSideBarState,
        *,
        animate: bool = True,
    ) -> None:
        """State drives target width; chrome follows width (and Expanded always shows)."""
        self._sidebarState = state
        endWidth = self._targetWidthForState(state)

        # Show captions as soon as we are expanding — do not wait for anim end.
        if state is eSideBarState.Expanded:
            self._pushChromeCollapsed(False)

        useAnim = (
            animate
            and self._animation is not None
            and endWidth != self.width()
        )

        if not useAnim:
            self.setFixedWidth(endWidth)
            self._syncChromeFromWidth()
            self.updateGeometry()
            return

        try:
            anim = self._animation
            assert anim is not None
            if anim.isRunning:
                anim.stop()
            anim.start(endWidth=endWidth)
        except Exception as ex:
            error("[SideBar] animation start FAIL", ex)
            error(f"[SideBar] traceback:\n{format_exc()}")
            self.setFixedWidth(endWidth)
            self._syncChromeFromWidth()
            self.updateGeometry()

    def _onSizeAnimFinished(self) -> None:
        try:
            endWidth = self._targetWidthForState(self._sidebarState)
            self.setFixedWidth(endWidth)
            self._syncChromeFromWidth()
            self.updateGeometry()
        except Exception as ex:
            error("[SideBar] _onSizeAnimFinished FAIL", ex)
            error(f"[SideBar] traceback:\n{format_exc()}")
            raise

    def setContent(self, widget: Optional[QWidget]) -> None:
        host = self._contentHost
        layout = self._contentLayout
        if host is None or layout is None:
            raise RuntimeError("SideBar UI not initialized")

        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        self._content = widget
        if widget is not None:
            self._pushMenuMetrics(widget)
            layout.addWidget(widget, stretch=1)
            self._syncChromeFromWidth()

    def setFooter(self, widget: Optional[QWidget]) -> None:
        host = self._footerHost
        layout = self._footerLayout
        if host is None or layout is None:
            raise RuntimeError("SideBar UI not initialized")

        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        self._footer = widget
        if widget is not None:
            self._pushMenuMetrics(widget)
            layout.addWidget(widget, stretch=0)
            self._syncChromeFromWidth()

    @property
    def Header(self) -> SideBarHeader:
        return self._header

    @property
    def Content(self) -> Optional[QWidget]:
        return self._content

    @Content.setter
    def Content(self, value: Optional[QWidget]) -> None:
        self.setContent(value)

    @property
    def Footer(self) -> Optional[QWidget]:
        return self._footer

    @Footer.setter
    def Footer(self, value: Optional[QWidget]) -> None:
        self.setFooter(value)

    @property
    def Title(self) -> str:
        return self._header.Title

    @Title.setter
    def Title(self, value: str) -> None:
        self._header.Title = value

    @property
    def Description(self) -> str:
        return self._header.Description

    @Description.setter
    def Description(self, value: str) -> None:
        self._header.Description = value

    @property
    def ExpandedWidth(self) -> int:
        return self._expandedWidth

    @ExpandedWidth.setter
    def ExpandedWidth(self, value: int) -> None:
        self._expandedWidth = int(value)

    @property
    def CollapsedWidth(self) -> int:
        return self._collapsedWidth

    @CollapsedWidth.setter
    def CollapsedWidth(self, value: int) -> None:
        self._collapsedWidth = int(value)
        self._header.setCollapsedWidth(self._collapsedWidth)

    @property
    def MenuIconSize(self) -> int:
        return self._menuIconSize

    @property
    def MenuChildIconSize(self) -> int:
        return self._menuChildIconSize

    @property
    def MenuItemMargins(self) -> Tuple[int, int, int, int]:
        return self._menuItemMargins

    @property
    def MenuChildIndent(self) -> int:
        return self._menuChildIndent

    @property
    def Animation(self) -> Optional[iAnimation]:
        return self._animation

    @Animation.setter
    def Animation(self, value: Optional[iAnimation]) -> None:
        if self._animation is not None:
            finished = getattr(self._animation, "finished", None)
            stopped = getattr(self._animation, "stopped", None)
            if finished is not None:
                try:
                    finished.disconnect(self._onSizeAnimFinished)
                except Exception:
                    pass
            if stopped is not None:
                try:
                    stopped.disconnect(self._onSizeAnimFinished)
                except Exception:
                    pass
        self._animation = value
        if value is not None:
            finished = getattr(value, "finished", None)
            stopped = getattr(value, "stopped", None)
            if finished is not None:
                finished.connect(self._onSizeAnimFinished)
            if stopped is not None:
                stopped.connect(self._onSizeAnimFinished)

    @property
    def State(self) -> eSideBarState:
        return self._sidebarState

    @State.setter
    def State(self, value: eSideBarState) -> None:
        if not isinstance(value, eSideBarState):
            raise TypeError(f"State must be eSideBarState, got {type(value)!r}")
        icon = getattr(self._header, "_icon", None)
        if icon is not None:
            registered = getattr(icon, "_icons", None)
            if registered is not None and value not in registered:
                raise ValueError(
                    f"State {value!r} has no icon registered on header StatefullIcon"
                )
        if value == self._sidebarState and self._header.State == value:
            self.setFixedWidth(self._targetWidthForState(value))
            self._syncChromeFromWidth()
            return
        self._header.State = value
