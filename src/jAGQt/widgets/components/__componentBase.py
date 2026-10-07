# ==================================================================================
# src/jAGQt/types/components/__component.py
# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

# ==================================================================================
from ...utilities import contentMargins, replaceLayout


# ==================================================================================
class ComponentBase:
    @property
    def Name(self: QWidget | QMainWindow) -> str:
        return self.objectName()

    @Name.setter
    def Name(self: QWidget | QMainWindow, value: str):
        self.setObjectName(value)

    @property
    def Parent(self: QWidget | QMainWindow) -> QWidget:
        return self.parent()

    @Parent.setter
    def Parent(self: QWidget, value: QWidget | QMainWindow):
        self.setParent(value)

    @property
    def Layout(self: QWidget | QMainWindow) -> QBoxLayout:
        lLayout: QBoxLayout = getattr(self, "_layout", None)
        if lLayout is None: lLayout = self.layout()
        return lLayout

    @Layout.setter
    def Layout(self: QWidget | QMainWindow, value: QBoxLayout) -> None:
        lOldLayout: QBoxLayout = getattr(self, "_layout", None)
        replaceLayout(self, lOldLayout, value)
        self._layout: QBoxLayout = value

    @property
    def ContentSpacing(self: QWidget | QMainWindow):
        layout: QBoxLayout = self.Layout
        return layout.spacing()

    @ContentSpacing.setter
    def ContentSpacing(self: QWidget | QMainWindow, value: int):        
        layout: QBoxLayout = self.Layout
        layout.setSpacing(value)

    @property
    def ContentMargins(self: QWidget | QMainWindow) -> QMargins:
        layout: QBoxLayout = self.Layout
        return layout.contentsMargins()

    @ContentMargins.setter
    def ContentMargins(self: QWidget | QMainWindow, value: QMargins | int | tuple[int] | list[int]):
        layout: QBoxLayout = self.Layout
        if isinstance(value, QMargins):
            layout.setContentsMargins(value)

        else:
            layout.setContentsMargins(contentMargins(value))
