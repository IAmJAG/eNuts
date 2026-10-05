# ==================================================================================
# src/fluxCore/actions/androidAction/injectKey/__injectKeyPress.py
# ==================================================================================
from ..androidAction.enums import eKeyCode, eKeyState, eMetaState
from .__injectKeyBase import InjectKeyBase


# ==================================================================================
class InjectKeyPress(InjectKeyBase):
    def __init__(
        self, 
        keyCode: eKeyCode, 
        repeat: int = 0, 
        metaState: eMetaState = eMetaState.NONE,
        *args, **kwargs,
    ):
        super().__init__(keyCode, eKeyState.DOWN, repeat, metaState, *args, **kwargs)