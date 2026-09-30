# ==================================================================================
# src/jAGQt/widgets/mixins/__component.py
# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QBoxLayout, QLayout, QMainWindow, QWidget

# ==================================================================================
from ...utilities import contentMargins
from ..interface.components import icomponent


# ==================================================================================
class ComponentBase(icomponent):
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
        if hasattr(self, "_layout"):
            return self._layout

        return self.layout()

    @Layout.setter
    def Layout(self: QWidget, value: QLayout) -> None:
        if hasattr(self, "_layout"):            
            self._layout = value

        self.setLayout(value)

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
