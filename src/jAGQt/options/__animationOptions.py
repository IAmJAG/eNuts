# ==================================================================================
from __future__ import annotations

# ==================================================================================
from .__optionsBase import OptionsBase

# ==================================================================================
C_DEFAULT_DURATION_MS: int = 280
C_DEFAULT_NAME: str = "Animation"
# ==================================================================================


# ==================================================================================
class AnimationOptions(OptionsBase):
    """Configuration settings applied to an animation instance, then dropped.

    The animation object owns runtime configuration after apply. This type is
    the serializable settings blob (e.g. duration) loaded from a theme options file.
    """

    def __init__(
        self,
        name: str = C_DEFAULT_NAME,
        version: int = 1,
        description: str = "",
        durationMs: int = C_DEFAULT_DURATION_MS,
    ) -> None:
        super().__init__(name=name or C_DEFAULT_NAME, version=version, description=description)
        if int(durationMs) < 0:
            raise ValueError(f"durationMs must be >= 0, got {durationMs}")
        self._durationMs: int = int(durationMs)
        self.Properties.extend(["durationMs"])

    # ==================================================================================
    @property
    def durationMs(self) -> int:
        return self._durationMs

    @durationMs.setter
    def durationMs(self, value: int) -> None:
        if int(value) < 0:
            raise ValueError(f"durationMs must be >= 0, got {value}")
        self._durationMs = int(value)
