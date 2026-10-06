# ==================================================================================
# src/jAGQt/widgets/__header.py
# ==================================================================================
from traceback import format_exc
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QLabel,
)

from jAGFx.workflow import workflow

# ==================================================================================
from ..utilities import newLayout
from .components import ComponentBase


# ==================================================================================
@workflow("InitializeUI")
class Header(QFrame, ComponentBase):
    OBJECT_NAME = "W_HEADER"

    def __init__(
        self,
        title: str = "jAGQt Page",
        description: str = "",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._title = title
        self._description = description

    def _wInitializeUI(self) -> None:
        try:
            debug("[header] step1 objectName/attrs")
            objName: str = self.OBJECT_NAME
            self.setObjectName(objName)
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

            titleText: str = self._title
            descriptionText: str = self._description
            debug(f"[header] step2 titleText={titleText!r} desc={descriptionText!r}")

            del self._title
            del self._description

            debug("[header] step3 QLabel title")
            title: QLabel = QLabel(titleText)
            title.setObjectName(f"{objName}_TITLE")
            debug(
                f"[header] step3b title parent={title.parent()!r} "
                f"isWindow={title.isWindow()} visible={title.isVisible()}"
            )

            debug("[header] step4 QLabel description")
            description: QLabel = QLabel(descriptionText)
            description.setObjectName(f"{objName}_DESCRIPTION")
            debug(
                f"[header] step4b desc parent={description.parent()!r} "
                f"isWindow={description.isWindow()} visible={description.isVisible()}"
            )

            debug("[header] step5 newLayout")
            outerLayout: QBoxLayout = newLayout(
                QBoxLayout,
                spacing=0,
                margins=(0, 0, 0, 0),
                direction=QBoxLayout.Direction.TopToBottom,
            )

            debug("[header] step6 addWidget title+description")
            outerLayout.addWidget(title)
            outerLayout.addWidget(description)

            debug("[header] step7 setLayout")
            self.setLayout(outerLayout)
            self._layout: QBoxLayout = outerLayout
            self._title: QLabel = title
            self._description: QLabel = description
            debug(
                f"[header] step7b after setLayout title.parent={title.parent()!r} "
                f"header.isWindow={self.isWindow()} header.visible={self.isVisible()}"
            )

            debug("[header] step8 setVisible on labels")
            title.setVisible(bool(titleText))
            description.setVisible(bool(descriptionText))
            debug(
                f"[header] step8b title.visible={title.isVisible()} "
                f"desc.visible={description.isVisible()} "
                f"header.visible={self.isVisible()} header.isWindow={self.isWindow()}"
            )
            debug("[header] _wInitializeUI DONE")
        except Exception:
            error(f"[header] _wInitializeUI FAIL\n{format_exc()}")
            raise

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
