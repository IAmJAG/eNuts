# ==================================================================================
# src/jAGQt/widgets/workspace/__workspace.py
# ==================================================================================
from traceback import format_exc
from typing import Dict, Optional

# ==================================================================================
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QBoxLayout, QSizePolicy, QStackedWidget, QWidget

from jAGQt.utilities import newLayout

# ==================================================================================
from jAGQt.widgets.components import ComponentBase

# ==================================================================================
from ..page.__page import Page


# ==================================================================================
class Workspace(QWidget, ComponentBase):
    """Manages multiple Pages inside a stacked layout."""

    CurrentPageChanged = Signal(object)  # emits Page | None

    def __init__(self, parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.setObjectName("Workspace")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._stack: QStackedWidget = QStackedWidget(self)
        self._pages: Dict[str, Page] = {}
        self._nameToId: Dict[str, str] = {}

        self._layout: QBoxLayout = newLayout(QBoxLayout, spacing=0, margins=0)
        self.Layout.addWidget(self._stack)

        self._stack.currentChanged.connect(self._onStackChanged)

    # ==================================================================================
    def AddPage(self, page: Page, name: Optional[str] = None) -> None:
        print(
            f"[workspace] AddPage ENTER name={name!r} "
            f"pageId={page.Id!r} isWindow={page.isWindow()} "
            f"stackCount={self._stack.count()}",
            flush=True,
        )
        try:
            if page.Id in self._pages:
                print("[workspace] AddPage skip duplicate Id", flush=True)
                return

            print("[workspace] AddPage before stack.addWidget", flush=True)
            self._stack.addWidget(page)
            print(
                f"[workspace] AddPage after stack.addWidget "
                f"isWindow={page.isWindow()} parent={type(page.parent()).__name__ if page.parent() else None} "
                f"stackCount={self._stack.count()}",
                flush=True,
            )

            self._pages[page.Id] = page
            lKey = name if name is not None else page.Title
            if lKey:
                self._nameToId[lKey] = page.Id
            print(f"[workspace] AddPage END key={lKey!r}", flush=True)
        except Exception:
            print(f"[workspace] AddPage FAIL\n{format_exc()}", flush=True)
            raise

    def RemovePage(self, key: str) -> None:
        """Remove by Id or by registered name."""
        lId = self._nameToId.pop(key, key)
        lPage = self._pages.pop(lId, None)
        if lPage is None:
            return
        # clean reverse map
        for lName, lMappedId in list(self._nameToId.items()):
            if lMappedId == lId:
                del self._nameToId[lName]
        self._stack.removeWidget(lPage)
        lPage.hide()
        lPage.deleteLater()

    def SetCurrentPage(self, key: str) -> None:
        """Switch by Id or by registered name."""
        lId = self._nameToId.get(key, key)
        lPage = self._pages.get(lId)
        if lPage is not None:
            self._stack.setCurrentWidget(lPage)

    def GetPage(self, key: str) -> Optional[Page]:
        lId = self._nameToId.get(key, key)
        return self._pages.get(lId)

    def Clear(self) -> None:
        for lKey in list(self._pages.keys()):
            self.RemovePage(lKey)

    addPage = AddPage
    setCurrentPage = SetCurrentPage

    # ==================================================================================
    @property
    def CurrentPage(self) -> Optional[Page]:
        lWidget = self._stack.currentWidget()
        return lWidget if isinstance(lWidget, Page) else None

    @property
    def Pages(self) -> Dict[str, Page]:
        return dict(self._pages)

    @property
    def Count(self) -> int:
        return len(self._pages)

    # ==================================================================================
    def _onStackChanged(self, index: int) -> None:
        print(f"[workspace] currentChanged index={index}", flush=True)
        lPage = self._stack.widget(index) if index >= 0 else None
        self.CurrentPageChanged.emit(lPage if isinstance(lPage, Page) else None)
