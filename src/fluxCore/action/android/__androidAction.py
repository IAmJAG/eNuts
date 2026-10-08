# ==================================================================================
# src/fluxCore/action/android/__androidAction.py
# ==================================================================================
from struct import pack

# ==================================================================================
from utilities import createTask

# ==================================================================================
from ...types.interface.action.__actionMetadata import iActionMetadata
from ...types.interface.action.__androidAction import iAndroidAction
from ...types.interface.sockets import iControlSocket
from ..__action import Action
from .enums.__eCommands import eCommandType


# ==================================================================================
class AndroidAction(iAndroidAction, Action):
    def __init__(
        self,
        name: str = None,
        commandType: eCommandType = eCommandType.UNKNOWN,
        *args,
        **kwargs,
    ):
        lName: str = name if name else f"ANDROID_ACTION_{commandType.name.upper()}"
        # Call Action explicitly so _name is always set (avoids MRO/Protocol quirks).
        Action.__init__(self, lName)
        self._commandType: int = commandType.value

    def execute(self, control: iControlSocket, payload: bytes):
        try:
            payload: bytes = pack(">B", self._commandType) + payload
            createTask(control.send, payload)

        except Exception as ex:
            raise ex
