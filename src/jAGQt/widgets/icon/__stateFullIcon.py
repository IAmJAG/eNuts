# ==================================================================================
from enum import Enum
from typing import Dict, Optional, Type, Union

# ==================================================================================
from PySide6.QtGui import QColor, QIcon, QPixmap

# ==================================================================================
from ...icons.animations import IconMorphAnimation
from ...types.interface.icons.animation import iIconAnimation
from .__icon import Icon


# ==================================================================================
class StatefullIcon[T: Enum](Icon):
    def __init__(
        self,
        icons: Dict[T, Optional[Union[QIcon, QPixmap, str]]] = {},
        background: Optional[Union[str, QColor]] = None,
        foreground: Optional[Union[str, QColor]] = None,        
        *args, **kwargs,
    ) -> None:
        if icons is None or len(icons) == 0:
            raise ValueError("icons must not be None or empty")
        icon = icons[list(icons.values())[0]]
        super().__init__(icons[icon], background, foreground, *args, **kwargs)                
        self._icons: Dict[Enum, Optional[Union[QIcon, QPixmap, str]]] = icons
        self._state: T = list(icons.keys())[0]                

        self._switchAnimation: Optional[iIconAnimation] = None
        if len(icons) > 1:
            startIcon: Optional[QIcon] = icons[list(icons.values())[0]]
            endIcon: Optional[QIcon] = icons[list(icons.values())[1]]
            self._switchAnimation: Optional[iIconAnimation] = IconMorphAnimation(startIcon=startIcon, endIcon=endIcon, target=self)
    
    @property
    def state(self) -> T:
        return self._state

    @state.setter
    def state(self, state: T):
        self._state = state
        self.setIcon(self._icons[state])

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str]]):        
        # TODO: validate animation with start and end icon
        switchAnimation: IconMorphAnimation = self._switchAnimation   
        icons: Dict[Enum, Optional[Union[QIcon, QPixmap, str]]] = self._icons

        endIcon: Optional[QIcon] = self._icons[self._state]
        switchAnimation.setIcons(icon, endIcon)
        switchAnimation.start()        

    def addIcon(self, state: T, icon: Optional[Union[QIcon, QPixmap, str]] = None):
        self._icons[state] = icon

        if state == self._state:
            self.setIcon(icon)

    def removeIcon(self, state: T):
        if state in self._icons:
            del self._icons[state]

        if state == self._state:
            self.state = list(self._icons.keys())[0]

        
    

    