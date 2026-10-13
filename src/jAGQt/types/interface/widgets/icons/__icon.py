# ==================================================================================
from typing import Optional, Protocol, Union, runtime_checkable

# ==================================================================================
from PySide6.QtGui import QColor, QIcon, QPixmap

# ==================================================================================
from ...components import iComponentBase


# ==================================================================================
@runtime_checkable
class iIcon(iComponentBase, Protocol):
    def __init__(
        self,
        icon: Optional[Union[QIcon, QPixmap, str]] = None,
        background: Optional[Union[str, QColor]] = None,
        foreground: Optional[Union[str, QColor]] = None,
        *args, **kwargs,
    ) -> None: ...
    def setBackground(self, background: Optional[Union[str, QColor]]): ...
    def setForeground(self, foreground: Optional[Union[str, QColor]]): ...
    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]):...    
    def resizeEvent(self, event): ...
    def clear(self): ...