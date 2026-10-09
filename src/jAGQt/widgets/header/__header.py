# ==================================================================================
# src/jAGQt/widgets/header/__header.py
# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QLabel,
    QWidget,
)

from jAGFx.workflow import workflow

# ==================================================================================
from ...utilities import newLayout
from ..components import ComponentBase
from .__headerIcon import IconType, _headerIcon
from .__iconPosition import IconPosition


# ==================================================================================
@workflow("InitializeUI")
class Header(QFrame, ComponentBase):
    OBJECT_NAME = "W_HEADER"

    def __init__(
        self,
        title: str = "jAGQt Page",
        description: str = "",
        icon: IconType = None,
        iconSize: int = 24,
        iconFormat: IconPosition = IconPosition.TitleRow,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._title = title
        self._description = description
        self._icon: IconType = icon
        self._iconSize = max(1, int(iconSize))
        self._iconFormat = iconFormat

    def _wInitializeUI(self) -> None:
        lObjName: str = self.OBJECT_NAME
        self.setObjectName(lObjName)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        lTitleText: str = self._title
        lDescriptionText: str = self._description
        lIcon: IconType = self._icon
        lIconSize: int = self._iconSize
        lIconFormat: IconPosition = self._iconFormat

        del self._title
        del self._description
        del self._icon
        del self._iconSize
        del self._iconFormat

        lIconWidget: _headerIcon = _headerIcon(icon=lIcon, iconSize=lIconSize)
        lIconWidget.setObjectName(f"{lObjName}_ICON")

        lTitle: QLabel = QLabel(lTitleText)
        lTitle.setObjectName(f"{lObjName}_TITLE")

        lDescription: QLabel = QLabel(lDescriptionText)
        lDescription.setObjectName(f"{lObjName}_DESCRIPTION")

        # Text column (title over description) — shared by both formats
        lTextLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        lTextLayout.addWidget(lTitle)
        lTextLayout.addWidget(lDescription)
        lTextColumn: QWidget = QWidget()
        lTextColumn.setLayout(lTextLayout)
        lTextColumn.setObjectName(f"{lObjName}_TEXT")

        # Format 1 host: title-row only (icon + title), description full-width below
        lTitleRow: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=8,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.LeftToRight,
        )
        lTitleRowWidget: QWidget = QWidget()
        lTitleRowWidget.setLayout(lTitleRow)
        lTitleRowWidget.setObjectName(f"{lObjName}_TITLE_ROW")

        # Format 2 host: icon | text-column
        lSpanRow: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=8,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.LeftToRight,
        )
        lSpanRowWidget: QWidget = QWidget()
        lSpanRowWidget.setLayout(lSpanRow)
        lSpanRowWidget.setObjectName(f"{lObjName}_SPAN_ROW")

        lOuterLayout: QBoxLayout = newLayout(
            QBoxLayout,
            spacing=0,
            margins=(0, 0, 0, 0),
            direction=QBoxLayout.Direction.TopToBottom,
        )
        lOuterLayout.addWidget(lTitleRowWidget)
        lOuterLayout.addWidget(lSpanRowWidget)
        # description is reparented between formats; placeholder slot for format 1
        lDescHost: QWidget = QWidget()
        lDescHost.setObjectName(f"{lObjName}_DESC_HOST")
        lDescHostLayout: QBoxLayout = newLayout(
            QBoxLayout, spacing=0, margins=(0, 0, 0, 0)
        )
        lDescHost.setLayout(lDescHostLayout)
        lOuterLayout.addWidget(lDescHost)

        self.setLayout(lOuterLayout)
        self._layout: QBoxLayout = lOuterLayout

        self._title: QLabel = lTitle
        self._description: QLabel = lDescription
        self._iconWidget: _headerIcon = lIconWidget
        self._textColumn: QWidget = lTextColumn
        self._titleRow: QBoxLayout = lTitleRow
        self._titleRowWidget: QWidget = lTitleRowWidget
        self._spanRow: QBoxLayout = lSpanRow
        self._spanRowWidget: QWidget = lSpanRowWidget
        self._descHost: QWidget = lDescHost
        self._descHostLayout: QBoxLayout = lDescHostLayout
        self._iconSize: int = lIconSize
        self._iconFormat: IconPosition = lIconFormat

        if not lDescriptionText:
            lDescription.hide()

        self._applyFormat()

    # ==================================================================================
    def _clearLayout(self, layout: QBoxLayout) -> None:
        while layout.count():
            lItem = layout.takeAt(0)
            if lItem is None:
                continue
            lWidget = lItem.widget()
            if lWidget is not None:
                lWidget.setParent(None)

    def _applyFormat(self) -> None:
        """Rebuild child parenting for the active icon format."""
        self._clearLayout(self._titleRow)
        self._clearLayout(self._spanRow)
        self._clearLayout(self._descHostLayout)

        lHasIcon: bool = self._iconWidget.HasIcon

        if self._iconFormat is IconPosition.SpanRows and lHasIcon:
            # Format 2: [icon | title/description stack]
            self._titleRowWidget.hide()
            self._descHost.hide()
            self._spanRowWidget.show()
            self._spanRow.addWidget(self._iconWidget, 0, Qt.AlignmentFlag.AlignTop)
            self._spanRow.addWidget(self._textColumn, 1)
            self._title.setParent(self._textColumn)
            self._description.setParent(self._textColumn)
            self._textColumn.layout().addWidget(self._title)
            self._textColumn.layout().addWidget(self._description)
        else:
            # Format 1 (or no icon): [icon?] Title  /  Description full width
            self._spanRowWidget.hide()
            self._titleRowWidget.show()
            self._descHost.show()
            if lHasIcon:
                self._titleRow.addWidget(
                    self._iconWidget, 0, Qt.AlignmentFlag.AlignVCenter
                )
            self._titleRow.addWidget(self._title, 1)
            self._descHostLayout.addWidget(self._description)

    # ==================================================================================
    @property
    def Title(self) -> str:
        return self._title.text()

    @Title.setter
    def Title(self, value: str) -> None:
        self._title.setText(value)
        self._title.setVisible(bool(value))

    @property
    def Description(self) -> str:
        return self._description.text()

    @Description.setter
    def Description(self, value: str) -> None:
        self._description.setText(value)
        self._description.setVisible(bool(value))

    @property
    def Icon(self) -> Optional[Union[QIcon, QPixmap]]:
        return self._iconWidget._icon

    @Icon.setter
    def Icon(self, value: IconType) -> None:
        self._iconWidget.SetIcon(value)
        self._applyFormat()

    @property
    def IconFormat(self) -> IconPosition:
        return self._iconFormat

    @IconFormat.setter
    def IconFormat(self, value: IconPosition) -> None:
        if value is self._iconFormat:
            return
        self._iconFormat = value
        self._applyFormat()

    @property
    def IconSize(self) -> int:
        return self._iconSize

    @IconSize.setter
    def IconSize(self, value: int) -> None:
        lSize: int = max(1, int(value))
        if lSize == self._iconSize:
            return
        self._iconSize = lSize
        self._iconWidget.SetIconSize(lSize)
