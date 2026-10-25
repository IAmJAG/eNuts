# ==================================================================================
# src/fluxCore/action/android/__androidAction.py
# ==================================================================================
from struct import pack

# ==================================================================================
from utilities import createTask

# ==================================================================================
from ...types.interface.sockets import iControlSocket
from .. import Action
from .enums import eCommandType


# ==================================================================================
# Inherit only the concrete Action base. Do not mix in iActionMetadata /
# iAndroidAction Protocols here: Action already subclasses iActionMetadata, and
# iAndroidAction also extends iActionMetadata, which yields an inconsistent MRO.
# Structural typing (runtime_checkable Protocols) still applies without inheritance.
class AndroidAction(Action):
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
