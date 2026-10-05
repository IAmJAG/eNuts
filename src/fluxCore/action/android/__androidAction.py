# ==================================================================================
# src/fluxCore/emitter/androidEmitter/actions/__action.py
# ==================================================================================
from struct import pack

# ==================================================================================
from utilities import createTask

# ==================================================================================
from ...types.interface.action import iActionMetadata, iAndroidAction
from ...types.interface.sockets import iControlSocket
from .. import Action
from .androidAction.enums import eCommandType


# ==================================================================================
class AndroidAction(Action, iActionMetadata, iAndroidAction):    
    def __init__(self, name: str = None, commandType: eCommandType = eCommandType.UNKNOWN, *args, **kwargs):
        name = name if name else f"ANDROID_ACTION_{commandType.name.upper()}"
        super().__init__(name, *args, **kwargs)
        self._commandType: int = commandType.value

    def execute(self, control: iControlSocket, payload: bytes):
        try:
            payload: bytes = pack(">B", self._commandType) + payload        
            createTask(control.send, payload)
        
        except Exception as ex:
            raise ex
