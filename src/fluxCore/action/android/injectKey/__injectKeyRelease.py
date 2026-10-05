# ==================================================================================
from ..androidAction.enums import eKeyCode, eKeyState, eMetaState
from .__injectKeyBase import InjectKeyBase


# ==================================================================================
class InjectKeyRelease(InjectKeyBase):
    def __init__(
        self,
        keyCode: eKeyCode,
        repeat: int = 0,
        metaState: eMetaState = eMetaState.NONE,
        *args, **kwargs,
    ):
        super().__init__(keyCode, eKeyState.UP, repeat, metaState, *args, **kwargs)
