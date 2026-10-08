# ==================================================================================
# src/fluxCore/action/android/injectKey/__injectKeyBase.py
# ==================================================================================
from struct import pack

# ==================================================================================
from ....types.interface.sockets import iControlSocket
from ..__androidAction import AndroidAction as Action
from ..enums import eCommandType, eKeyCode, eKeyState, eMetaState


# ==================================================================================
class InjectKeyBase(Action):
    def __init__(
        self,
        keyCode: eKeyCode,
        keyState: eKeyState,
        repeat: int = 0,
        metaState: eMetaState = eMetaState.NONE,
        *args,
        **kwargs,
    ):
        lName = f"ANDROID_ACTION_INJECT_KEYCODE_{keyCode.name}_{keyState.name}"
        super().__init__(lName, eCommandType.INJECT_KEYCODE, *args, **kwargs)
        self._pkg: bytes = pack(
            ">BIII", keyState.value, keyCode.value, repeat, metaState.value
        )

    def execute(self, control: iControlSocket):
        self.delayBefore()
        super().execute(control, self._pkg)
