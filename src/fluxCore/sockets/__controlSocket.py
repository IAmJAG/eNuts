# ==================================================================================
from ..types.interface.sockets import iControlSocket
from .__socket import SocketBase


# ==================================================================================
class ControlSocket(SocketBase, iControlSocket): ...
    
