# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from ...utilities import G_DEFAULT_EMBED_DIM
from .__vocabulary import Vocabulary
from .labels import ArgumentKindLabel


# ==================================================================================
class ArgumentKindVocabulary(Vocabulary):
    def __init__(
        self, key: str, description: Optional[str], dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__(ArgumentKindLabel(key, description), dimension)