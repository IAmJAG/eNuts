# ==================================================================================
from functools import wraps
from types import MethodType
from typing import Callable

# ==================================================================================
from PySide6.QtWidgets import QBoxLayout, QLayout, QLayoutItem, QWidget

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...configuration import ApplicationInformation
from ..widgets import EvolvingNeuralOrb


# ==================================================================================
# Layout method names that change child membership
C_MORPH_METHODS: tuple[str, ...] = (
    "addWidget",
    "insertWidget",
    "addLayout",
    "insertLayout",
    "addItem",
    "insertItem",
    "addStretch",
    "addSpacing",
    "addStrut",
    "removeWidget",
    "removeItem",
    "takeAt",
)


# ==================================================================================
@workflow(
    "InitializeSettings", "InitializeUI", "RestoreWindowsState",
    "InitializeInfo"
)
class MainWindow(MainWindowBase, ApplicationInformation):
    def __init__(self, *args, **kwargs) -> None:
        self._orbWidget: EvolvingNeuralOrb | None = None
        self._orbSyncing: bool = False
        self._hookedLayoutId: int | None = None
        super().__init__("ENUTS_WINDOW", frameless=False, *args, **kwargs)

    # ------------------------------------------------------------------ Orb helpers
    def _isOrbWidget(self, widget: QWidget | None) -> bool:
        if widget is None:
            return False
        if self._orbWidget is not None and widget is self._orbWidget:
            return True
        return isinstance(widget, EvolvingNeuralOrb)

    def _resolveLayout(self) -> QLayout | None:
        lLayout: QLayout | None = getattr(self, "_layout", None)
        if lLayout is None:
            lCentral = self.centralWidget()
            if lCentral is not None:
                lLayout = lCentral.layout()

        if lLayout is None:
            lLayout = self.layout()

        return lLayout

    def _iterLayoutWidgets(self, layout: QLayout) -> list[QWidget]:
        lWidgets: list[QWidget] = []
        for lIndex in range(layout.count()):
            lItem: QLayoutItem | None = layout.itemAt(lIndex)
            if lItem is None:
                continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidgets.append(lWidget)
        return lWidgets

    def _nonOrbWidgetCount(self, layout: QLayout) -> int:
        lCount = 0
        for lWidget in self._iterLayoutWidgets(layout):
            if not self._isOrbWidget(lWidget):
                lCount += 1
        return lCount

    def _findOrbInLayout(self, layout: QLayout) -> EvolvingNeuralOrb | None:
        for lWidget in self._iterLayoutWidgets(layout):
            if self._isOrbWidget(lWidget):
                return lWidget  # type: ignore[return-value]
        return None

    def _createOrb(self, parent: QWidget | None = None) -> EvolvingNeuralOrb:
        lOrb = EvolvingNeuralOrb(parent=parent if parent is not None else self)
        lOrb.setMinimumSize(320, 320)
        self._orbWidget = lOrb
        return lOrb

    def _removeOrbFromLayout(self, layout: QLayout) -> None:
        lOrb = self._findOrbInLayout(layout)
        if lOrb is None:
            lOrb = self._orbWidget
        if lOrb is None:
            return

        layout.removeWidget(lOrb)
        lOrb.setParent(None)
        lOrb.deleteLater()
        if self._orbWidget is lOrb:
            self._orbWidget = None

    def _ensureOrbInLayout(self, layout: QLayout) -> None:
        if self._findOrbInLayout(layout) is not None:
            return
        if self._nonOrbWidgetCount(layout) > 0:
            return

        lOrb = self._createOrb(parent=layout.parentWidget())
        # Prefer stretch-centered placement on box layouts
        if isinstance(layout, QBoxLayout):
            if layout.count() == 0:
                layout.addStretch(1)
                layout.addWidget(lOrb, 0)
                layout.addStretch(1)
            else:
                layout.addWidget(lOrb)
        else:
            layout.addWidget(lOrb)

    def _syncOrbWithLayout(self, layout: QLayout | None = None) -> None:
        if self._orbSyncing:
            return

        lLayout = layout if layout is not None else self._resolveLayout()
        if lLayout is None:
            return

        self._orbSyncing = True
        try:
            if self._nonOrbWidgetCount(lLayout) > 0:
                self._removeOrbFromLayout(lLayout)
            else:
                self._ensureOrbInLayout(lLayout)
        finally:
            self._orbSyncing = False

    # ------------------------------------------------------------------ Layout morph hooks
    def _wrapMorphMethod(self, layout: QLayout, methodName: str) -> None:
        lOriginal: Callable | None = getattr(layout, methodName, None)
        if lOriginal is None or not callable(lOriginal):
            return

        # Already wrapped
        if getattr(lOriginal, "_eNutsOrbHook", False):
            return

        lWindow = self

        @wraps(lOriginal)
        def lWrapped(*args, **kwargs):
            lResult = lOriginal(*args, **kwargs)
            if not lWindow._orbSyncing:
                lWindow._syncOrbWithLayout(layout)
            return lResult

        lWrapped._eNutsOrbHook = True  # type: ignore[attr-defined]
        setattr(layout, methodName, MethodType(lWrapped, layout) if False else lWrapped)

        # Bind as instance method so `self` inside original still works:
        # lOriginal is already a bound method; call it directly in lWrapped.
        setattr(layout, methodName, lWrapped)

    def _hookLayoutMorphs(self, layout: QLayout) -> None:
        lLayoutId = id(layout)
        if self._hookedLayoutId == lLayoutId and getattr(layout, "_eNutsMorphHooked", False):
            return

        for lName in C_MORPH_METHODS:
            self._wrapMorphMethod(layout, lName)

        layout._eNutsMorphHooked = True  # type: ignore[attr-defined]
        self._hookedLayoutId = lLayoutId

    # ------------------------------------------------------------------ Layout property
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
