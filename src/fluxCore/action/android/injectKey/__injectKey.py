# ==================================================================================
# src/fluxCore/action/android/injectKey/__injectKey.py
# ==================================================================================
from struct import pack

# ==================================================================================
from ....types.interface.sockets import iControlSocket
from ..__androidAction import AndroidAction as Action
from ..enums import eCommandType, eKeyCode, eKeyState, eMetaState


# ==================================================================================
class InjectKey(Action):
    def __init__(self, keyCode: eKeyCode, releaseDelay: float = 0, *args, **kwargs):
        lName = f"ANDROID_ACTION_INJECT_KEYCODE_{keyCode.name}"
        super().__init__(lName, eCommandType.INJECT_KEYCODE, *args, **kwargs)
        self._pkgPress: bytes = pack(
            ">BIII", eKeyState.DOWN.value, keyCode.value, 0, eMetaState.NONE.value
        )
        self._pkgRelease: bytes = pack(
            ">BIII", eKeyState.UP.value, keyCode.value, 0, eMetaState.NONE.value
        )
        self._releaseDelay: float = releaseDelay

    def execute(self, control: iControlSocket):
        self.delayBefore()
        super().execute(control, self._pkgPress)
        self.wait(self._releaseDelay)
        super().execute(control, self._pkgRelease)
        self.delayAfter()
