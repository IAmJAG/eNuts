# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Mapping, Optional, Union

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel
from ...utilities import G_DEFAULT_EMBED_DIM
from .__vocabulary import Vocabulary
from .labels import ActionLabel


# ==================================================================================
class ActionVocabulary(Vocabulary[ActionLabel]):
    def __init__(
        self,vocab: Optional[Mapping[str, Union[ActionLabel, str]]] = None,
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__(vocab=vocab, dimension=dimension)