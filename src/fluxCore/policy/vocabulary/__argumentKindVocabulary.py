# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Mapping, Optional, Union

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel
from ...utilities import G_DEFAULT_EMBED_DIM
from .__vocabulary import Vocabulary
from .labels import ArgumentKindLabel


# ==================================================================================
class ArgumentKindVocabulary(Vocabulary):
    """Vocabulary specialized for argument kinds (extension point for kind embeddings)."""

    def __init__(
        self, vocab: Optional[Mapping[str, Union[iLabel, str]]] = None,
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__(vocab=vocab, dimension=dimension)

    def _put(self, key: str, value: Union[iLabel, str, Mapping, object]) -> None:
        if isinstance(value, str):
            value = ArgumentKindLabel(key, value)

        elif isinstance(value, ArgumentKindLabel):
            pass

        elif isinstance(value, Mapping):
            value = ArgumentKindLabel(
                str(value.get("id", key) or key),
                str(value.get("description", "") or ""),
            )

        elif not isinstance(value, ArgumentKindLabel):
            value = ArgumentKindLabel(
                str(getattr(value, "id", key)),
                str(getattr(value, "description", "")),
            )
            
        super()._put(key, value)
