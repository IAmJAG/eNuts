# ==================================================================================
from functools import wraps
from typing import Callable

# ==================================================================================
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QBoxLayout, QLayout, QLayoutItem, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...configuration import ApplicationInformation
from ..widgets import EvolvingNeuralBrain

# ==================================================================================
C_MORPH_METHODS: tuple[str, ...] = (
    "addWidget", "insertWidget", "addLayout", "insertLayout", "addItem",
    "insertItem", "addStretch", "addSpacing", "addStrut", "removeWidget",
    "removeItem", "takeAt",
)

# ==================================================================================
@workflow("InitializeSettings", "InitializeUI", "RestoreWindowsState","InitializeInfo")
class MainWindow(MainWindowBase, ApplicationInformation):
    """Main window with EvolvingNeuralBrain as a background layer.

    The brain is NOT a layout item. It fills the central widget behind content:
    - layout empty  → brain shown + running
    - content added → brain paused + hidden
    - content cleared → brain shown + running again
    """

    def __init__(self, *args, **kwargs) -> None:
        self._orbWidget: EvolvingNeuralBrain | None = None
        self._orbSyncing: bool = False
        self._hookedLayoutId: int | None = None
        super().__init__("ENUTS_WINDOW", frameless=False, *args, **kwargs)

        self.installEventFilter(self)
        self._ensureOrbBackground()
        self._syncOrbWithLayout()

    def _hostWidget(self) -> QWidget:
        lCentral = self.centralWidget()
        return lCentral if lCentral is not None else self

    def _resolveLayout(self) -> QLayout | None:
        lLayout: QLayout | None = getattr(self, "_layout", None)
        if lLayout is None:
            lCentral = self.centralWidget()
            if lCentral is not None: lLayout = lCentral.layout()

        if lLayout is None: lLayout = self.layout()
        return lLayout

    def _iterLayoutWidgets(self, layout: QLayout) -> list[QWidget]:
        lWidgets: list[QWidget] = []
        for lIndex in range(layout.count()):
            lItem: QLayoutItem | None = layout.itemAt(lIndex)
            if lItem is None: continue
            lWidget = lItem.widget()
            if lWidget is not None: lWidgets.append(lWidget)

        return lWidgets

    def _contentWidgetCount(self, layout: QLayout) -> int:
        return len(self._iterLayoutWidgets(layout))

    def _ensureOrbBackground(self) -> EvolvingNeuralBrain:
        lHost = self._hostWidget()
        if self._orbWidget is not None:
            if self._orbWidget.parent() is not lHost:
                self._orbWidget.setParent(lHost)
                lHost.installEventFilter(self)
            return self._orbWidget

        lOrb = EvolvingNeuralBrain(parent=lHost)
        lOrb.setObjectName("EvolvingNeuralBrainBackground")
        lOrb.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        lOrb.lower()
        lOrb.hide()
        self._orbWidget = lOrb

        lHost.installEventFilter(self)
        self._fitOrbToHost()
        return lOrb

    def _fitOrbToHost(self) -> None:
        if self._orbWidget is None: return
        lHost = self._hostWidget()
        lRect = lHost.rect()
        if lRect.width() < 1 or lRect.height() < 1: return
        self._orbWidget.setGeometry(lRect)
        self._orbWidget.lower()
        if self._orbWidget.isVisible():
            self._orbWidget.update()

    def _showOrbBackground(self) -> None:
        lOrb = self._ensureOrbBackground()
        self._fitOrbToHost()
        lOrb.show()
        lOrb.lower()
        lOrb.Resume()

    def _hideOrbBackground(self) -> None:
        if self._orbWidget is None: return
        self._orbWidget.Pause()
        self._orbWidget.hide()

    def _syncOrbWithLayout(self, layout: QLayout | None = None) -> None:
        if self._orbSyncing: return

        lLayout = layout if layout is not None else self._resolveLayout()
        self._orbSyncing = True
        try:
            if lLayout is None or self._contentWidgetCount(lLayout) == 0:
                self._showOrbBackground()

            else:
                self._hideOrbBackground()

        finally:
            self._orbSyncing = False

    def _wrapMorphMethod(self, layout: QLayout, methodName: str) -> None:
        lOriginal: Callable | None = getattr(layout, methodName, None)
        if lOriginal is None or not callable(lOriginal): return
        if getattr(lOriginal, "_eNutsOrbHook", False): return

        lWindow = self

        @wraps(lOriginal)
        def lWrapped(*args, **kwargs):
            lResult = lOriginal(*args, **kwargs)
            if not lWindow._orbSyncing: lWindow._syncOrbWithLayout(layout)
            return lResult

        lWrapped._eNutsOrbHook = True  # type: ignore[attr-defined]
        setattr(layout, methodName, lWrapped)

    def _hookLayoutMorphs(self, layout: QLayout) -> None:
        lLayoutId = id(layout)
        if self._hookedLayoutId == lLayoutId and getattr(layout, "_eNutsMorphHooked", False):
            return

        for lName in C_MORPH_METHODS:
            self._wrapMorphMethod(layout, lName)

        layout._eNutsMorphHooked = True  # type: ignore[attr-defined]
        self._hookedLayoutId = lLayoutId

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if self._orbWidget is not None:
            lType = event.type()
            if lType in (QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.LayoutRequest):
                if watched is self or watched is self._hostWidget(): self._fitOrbToHost()

            elif lType == QEvent.Type.WindowStateChange and watched is self: self._fitOrbToHost()

        return super().eventFilter(watched, event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._fitOrbToHost()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._fitOrbToHost()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._releaseSizeConstraints()
        self._syncOrbWithLayout()
        self._fitOrbToHost()

    @property
    def Layout(self) -> QBoxLayout:
        lLayout = self._resolveLayout()
        if lLayout is not None:
            self._hookLayoutMorphs(lLayout)
            self._syncOrbWithLayout(lLayout)
        return lLayout  # type: ignore[return-value]

    @Layout.setter
    def Layout(self, value: QBoxLayout) -> None:
        lCentral = self.centralWidget()
        if lCentral is not None:
            lCentral.setLayout(value)

        else:
            self.setLayout(value)

        self._layout = value
        self._hookedLayoutId = None

        if value is not None:
            self._hookLayoutMorphs(value)
            self._syncOrbWithLayout(value)
