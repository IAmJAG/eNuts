# ==================================================================================
# src/jAGQt/types/interface/components/__componentBase.py
# ==================================================================================
from typing import Protocol, overload, runtime_checkable

# ==================================================================================
from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget


# ==================================================================================
@runtime_checkable
class iComponentBase(Protocol):    
    @overload
    @property        
    def Name(self: QMainWindow) -> str: ...
    @overload
    @property        
    def Name(self: QWidget) -> str: ...
    @property        
    def Name(self: QWidget | QMainWindow) -> str: ...

    @overload
    @property
    def Parent(self: QMainWindow) -> QWidget: ...    
    @overload
    @property
    def Parent(self: QWidget) -> QWidget: ...    
    @property
    def Parent(self: QWidget | QMainWindow) -> QWidget: ...    

    @overload
    @property
    def Layout(self: QMainWindow) -> QBoxLayout: ...
    @overload
    @property
    def Layout(self: QWidget) -> QBoxLayout: ...
    @property
    def Layout(self: QWidget | QMainWindow) -> QBoxLayout: ...

    @overload
    @property
    def ContentSpacing(self: QMainWindow): ...
    @overload
    @property
    def ContentSpacing(self: QWidget): ...
    @property
    def ContentSpacing(self: QWidget | QMainWindow): ...

    @property
    def ContentMargins(self: QMainWindow) -> QMargins: ...
    @property
    def ContentMargins(self: QWidget) -> QMargins: ...
    @property
    def ContentMargins(self: QWidget | QMainWindow) -> QMargins: ...