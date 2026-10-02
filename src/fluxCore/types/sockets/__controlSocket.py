# ==================================================================================
# src/fluxCore/types/sockets/__controlSocket.py
# ==================================================================================
from ...types.interface.sockets import iControlSocket
from .__socket import SocketBase


# ==================================================================================
class ControlSocket(SocketBase, iControlSocket): ...
    
