# ==================================================================================
# src/jAGQt/types/components/__component.py
# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QLayout, QMainWindow, QWidget

# ==================================================================================
from ...utilities import contentMargins, replaceLayout
from ..interface.components import iComponentBase


# ==================================================================================
class ComponentBase(iComponentBase):
    @property
    def Name(self: QWidget | QMainWindow) -> str:
        return self.objectName()

    @Name.setter
    def Name(self: QWidget | QMainWindow, value: str):
        self.setObjectName(value)

    @property
    def Parent(self: QWidget) -> QWidget:
        return self.parent()

    @Parent.setter
    def Parent(self: QWidget, value: QWidget):
        self.setParent(value)

    @property
    def Layout(self: QWidget) -> QLayout:
        lLayout = getattr(self, "_layout", None)
        if lLayout is not None: return lLayout

        return self.layout()

    @Layout.setter
    def Layout(self: QWidget, value: QLayout) -> None:
        lOldLayout = getattr(self, "_layout", None)
        replaceLayout(self, lOldLayout, value)
        self._layout = value

    @property
    def ContentSpacing(self: QWidget):
        return self.Layout.spacing()

    @ContentSpacing.setter
    def ContentSpacing(self, value: int):
        self.Layout.setSpacing(value)

    @property
    def ContentMargins(self: QWidget) -> QMargins:
        return self.Layout.contentsMargins()

    @ContentMargins.setter
    def ContentMargins(
        self: QWidget | QMainWindow, value: QMargins | int | tuple[int] | list[int]
    ):
        if isinstance(value, QMargins):
            self.Layout.setContentsMargins(value)

        else:
            self.Layout.setContentsMargins(contentMargins(value))
