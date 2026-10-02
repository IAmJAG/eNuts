# ==================================================================================
# src/fluxCore/types/interface/sockets/__controlSocket.py
# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from .__socket import iSocket


# ==================================================================================
@runtime_checkable
class iControlSocket(iSocket, Protocol): ...
    
