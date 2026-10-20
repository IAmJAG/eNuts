
# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
class iEmbeddingItem (iSerializable):
    @property
    def label(self) -> str: ...
    @property
    def description(self) -> str: ...
