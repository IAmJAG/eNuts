# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Mapping, Optional, Type, Union

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel
from ...utilities import G_DEFAULT_EMBED_DIM
from .__vocabulary import Vocabulary
from .labels import IntentLabel


# ==================================================================================
class IntentVocabulary(Vocabulary[IntentLabel]):
    labelClass: Type[iLabel] = IntentLabel

    def __init__(
        self,
        vocab: Optional[Mapping[str, Union[IntentLabel, str]]] = None,
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__(vocab=vocab, dimension=dimension)
