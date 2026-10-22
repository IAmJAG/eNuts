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
class ActionVocabulary(Vocabulary):
    """Vocabulary specialized for actions (extension point for action embeddings)."""

    def __init__(
        self,
        vocab: Optional[Mapping[str, Union[iLabel, str]]] = None,
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__(vocab=vocab, dimension=dimension)

    def _put(self, key: str, value: Union[iLabel, str, Mapping, object]) -> None:
        if isinstance(value, str):
            value = ActionLabel(key, value)
        elif isinstance(value, ActionLabel):
            pass
        elif isinstance(value, Mapping):
            value = ActionLabel(
                str(value.get("id", key) or key),
                str(value.get("description", "") or ""),
            )
        elif not isinstance(value, ActionLabel):
            value = ActionLabel(
                str(getattr(value, "id", key)),
                str(getattr(value, "description", "")),
            )
        super()._put(key, value)
