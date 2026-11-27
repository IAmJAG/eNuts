class ClientNotFoundException(Exception):
    def __init__(self, clientId: str| int, *args):        
        super().__init__(clientId, *args)
        self._clientId:  str | int = clientId

    @property
    def clientId(self) ->str | int:
        return self._clientId