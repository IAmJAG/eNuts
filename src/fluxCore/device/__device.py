# ==================================================================================
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.names import getRandomName
from jAGFx.serializer import Serializable

# ==================================================================================
from ..types.interface.device import iDevice


# ==================================================================================
class Device(Serializable, iDevice):
    def __init__(self, ident: str | UUID | None = None, name: str | None = None) -> None:
        super().__init__()

        if ident is None:  ident = uuid4()
        if name is None: name = getRandomName()

        self._id = ident
        self._name = name

        self.Properties.extend(["id", "name"])

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str | None:
        return self._name
