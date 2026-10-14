# ==================================================================================
# src/jAGQt/widgets/workspace/__commandBar.py
# ==================================================================================
from typing import TYPE_CHECKING, Optional, Protocol, Union, overload, runtime_checkable

# ==================================================================================
from ...components import iComponentBase
from .__commandBarButton import iCommandBarButton
from .__commandBarGroup import iCommandBarGroup


# ==================================================================================
@runtime_checkable
class iCommandBar(iComponentBase, Protocol):
    @overload
    def addButton(self, button: str) -> iCommandBarButton: ...
    @overload
    def addButton(self, button: iCommandBarButton) -> iCommandBarButton: ...    

    @overload
    def addButton(self, caption: str, group: str) -> iCommandBarButton: ...
    @overload
    def addButton(self, caption: str, group: iCommandBarGroup) -> iCommandBarButton: ...   

    @overload    
    def addButton(self, button: iCommandBarButton, group: str) -> iCommandBarButton: ...
    @overload
    def addButton(self, button: iCommandBarButton, group: iCommandBarGroup) -> iCommandBarButton: ...

    def addButton(
        self, button: iCommandBarButton | str, 
        group: Optional[Union[str, iCommandBarGroup]] = None
    ) -> iCommandBarButton:
        
        lButtonInstance = button
        if isinstance(button, str):
            lButtonInstance = iCommandBarButton(text=button)

        return super().addButton(lButtonInstance, group)

    @overload
    def removeButton(self, button: str): ...
    @overload
    def removeButton(self, button: iCommandBarButton): ...
    def removeButton(self, button: str | iCommandBarButton): ...

    @overload
    def contains(self, button: str) -> bool: ...
    @overload
    def contains(self, button: iCommandBarButton) -> bool: ...    
    def contains(self, button: str |iCommandBarButton) -> bool: ...

    @overload
    def addGroup(self, name: str): ...
    @overload
    def addGroup(self, group: iCommandBarGroup): ...
    def addGroup(self, name: str | iCommandBarGroup) -> iCommandBarGroup: ...

    def clear(self) -> None: ...

    