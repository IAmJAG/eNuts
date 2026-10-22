# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ....types.interface.policy.vocabulary import iLabel


# ==================================================================================
class Label(iLabel, Serializable):
    """One discrete vocabulary entry: stable id + human description."""

    def __init__(self, id: str = "", description: str = "") -> None:
        Serializable.__init__(self)
        self._id: str = id if id is not None else ""
        self._description: str = description if description is not None else ""
        self.Properties.extend(["id", "description"])

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value if value is not None else ""

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value if value is not None else ""

    @property
    def vocabularyKey(self) -> str:
        return f"{self._id}"