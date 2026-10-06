# ==================================================================================
# src/jAGQt/widgets/workspace/__commandBar.py
# ==================================================================================
from typing import Optional, Protocol, Union, overload, runtime_checkable

# ==================================================================================
from ...components import iComponentBase
from .__commandBarBase import iCommandBarBase
from .__commandBarButton import iCommandBarButton
from .__commandBarGroup import iCommandBarGroup


# ==================================================================================
@runtime_checkable
class iCommandBar(iCommandBarBase, iComponentBase, Protocol):
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
    def addGroup(self, name: str): ...
    @overload
    def addGroup(self, group: iCommandBarGroup): ...
    def addGroup(self, name: str | iCommandBarGroup) -> iCommandBarGroup: ...