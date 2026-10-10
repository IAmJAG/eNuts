# ==================================================================================
# src/jAGQt/widgets/dashboard/__card.py
# ==================================================================================
from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QFrame, QLabel, QSizePolicy, QWidget

from jAGFx.workflow import workflow

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class Card(QFrame, ComponentBase):
    """Styleable square shell. Subclass for domain cards; grid types against iCard."""

    OBJECT_NAME = "Card"

    def __init__(
        self,
        title: str = "",
        minColSpan: int = 1,
        minRowSpan: int = 1,
        preferredColSpan: int = 1,
        preferredRowSpan: int = 1,
        variant: str = "",
        id: Optional[str | UUID] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self._id: str | UUID = uuid4() if id is None else id
        self._titleText: str = title
        self._minColSpan: int = max(1, int(minColSpan))
        self._minRowSpan: int = max(1, int(minRowSpan))
        self._preferredColSpan: int = max(self._minColSpan, int(preferredColSpan))
        self._preferredRowSpan: int = max(self._minRowSpan, int(preferredRowSpan))
        self._variant: str = variant or ""

    def _wInitializeUI(self) -> None:
        lObjName: str = self.OBJECT_NAME
        lTitleText: str = self._titleText
        lVariant: str = self._variant

        del self._titleText

        self.setObjectName(lObjName)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.setProperty("variant", lVariant)
        self.setProperty("dragging", "false")
        self.setProperty("resizing", "false")

        lTitle: QLabel = QLabel(lTitleText)
        lTitle.setObjectName(f"{lObjName}_Title")
        lTitle.setVisible(bool(lTitleText))

        lBody: QWidget = QWidget()
        lBody.setObjectName(f"{lObjName}_Body")
        lBody.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        lBodyLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=0, margins=0
        )
        lBody.setLayout(lBodyLayout)

        lOuter: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=4,
            margins=(8, 8, 8, 8),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        lOuter.addWidget(lTitle, 0)
        lOuter.addWidget(lBody, 1)

        self.setLayout(lOuter)
        self._layout: QBoxLayout = lOuter
        self._titleLabel: QLabel = lTitle
        self._body: QWidget = lBody
        self._bodyLayout: QBoxLayout = lBodyLayout

    # ==================================================================================
    def SetBodyWidget(self, widget: QWidget) -> None:
        """Replace body content. Subclasses use this or override body build."""
        while self._bodyLayout.count():
            lItem = self._bodyLayout.takeAt(0)
            if lItem is None:
                continue
            lW = lItem.widget()
            if lW is not None:
                lW.setParent(None)
                lW.deleteLater()
        self._bodyLayout.addWidget(widget, 1)

    def SetDragging(self, value: bool) -> None:
        self.setProperty("dragging", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def SetResizing(self, value: bool) -> None:
        self.setProperty("resizing", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    # ==================================================================================
    @property
    def Id(self) -> str | UUID:
        return self._id

    @property
    def Title(self) -> str:
        return self._titleLabel.text()

    @Title.setter
    def Title(self, value: str) -> None:
        self._titleLabel.setText(value)
        self._titleLabel.setVisible(bool(value))

    @property
    def MinColSpan(self) -> int:
        return self._minColSpan

    @MinColSpan.setter
    def MinColSpan(self, value: int) -> None:
        self._minColSpan = max(1, int(value))

    @property
    def MinRowSpan(self) -> int:
        return self._minRowSpan

    @MinRowSpan.setter
    def MinRowSpan(self, value: int) -> None:
        self._minRowSpan = max(1, int(value))

    @property
    def PreferredColSpan(self) -> int:
        return self._preferredColSpan

    @PreferredColSpan.setter
    def PreferredColSpan(self, value: int) -> None:
        self._preferredColSpan = max(self._minColSpan, int(value))

    @property
    def PreferredRowSpan(self) -> int:
        return self._preferredRowSpan

    @PreferredRowSpan.setter
    def PreferredRowSpan(self, value: int) -> None:
        self._preferredRowSpan = max(self._minRowSpan, int(value))

    @property
    def Variant(self) -> str:
        return str(self.property("variant") or "")

    @Variant.setter
    def Variant(self, value: str) -> None:
        self.setProperty("variant", value or "")
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def Body(self) -> QWidget:
        return self._body
