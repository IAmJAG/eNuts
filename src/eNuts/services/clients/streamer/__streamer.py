# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.IPC.client import Client
from jAGFx.types.interface.communication.messages import iMessage

# ==================================================================================
from ....types.interface.services import iServiceManager


# ==================================================================================
class Streamer(iServiceManager, Client):
    def __init__(self, clientId: int):
        Client.__init__(self, clientId=clientId)

    async def processMessage(self, msg: iMessage, handled: bool = False):        
        if handled: return
        await Client.processMessage(self, message=msg, handled=handled)
