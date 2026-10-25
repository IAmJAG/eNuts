# ==================================================================================
# src/fluxCore/action/android/__androidAction.py
# ==================================================================================
from struct import pack

# ==================================================================================
from utilities import createTask

# ==================================================================================
from ...types.interface.action import iActionMetadata, iAndroidAction
from ...types.interface.sockets import iControlSocket
from .. import Action
from .enums import eCommandType


# ==================================================================================
# Concrete Action must come before Protocol bases so super().__init__ reaches
# Action.__init__ and sets _name / _data. Protocol-first MRO skips Action and
# leaves Touch/InjectKey with "object has no attribute '_name'".
class AndroidAction(Action, iActionMetadata, iAndroidAction):
    def __init__(
        self,
        name: str = None,
        commandType: eCommandType = eCommandType.UNKNOWN,
        *args,
        **kwargs,
    ):
        name = name if name else f"ANDROID_ACTION_{commandType.name.upper()}"
        super().__init__(name, *args, **kwargs)
        self._commandType: int = commandType.value

    def execute(self, control: iControlSocket, payload: bytes):
        try:
            payload: bytes = pack(">B", self._commandType) + payload
            createTask(control.send, payload)

        except Exception as ex:
            raise ex
