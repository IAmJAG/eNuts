# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from jAGFx.serializer import Serializable
from utilities.io import getConfigPath

# ==================================================================================
C_OPTIONS_SUBDIR: str = "options"
C_THEMES_SUBDIR: str = "themes"
# ==================================================================================


# ==================================================================================
class OptionsBase(Serializable):
    """Named serializable settings blob. Apply once to a host, then drop.

    Persist under ``config/themes/options/<themeName>/<Name>.json`` via
    :meth:`resolvePath`. Load/save I/O is owned by a theme handler (or caller);
    this type only encodes/decodes and resolves paths.
    """

    def __init__(
        self,
        name: str = "",
        version: int = 1,
        description: str = "",
    ) -> None:
        super().__init__()
        self._name: str = name
        self._version: int = int(version)
        self._description: str = description if description is not None else ""
        self.Properties.extend(["name", "version", "description"])

    # ==================================================================================
    @property
    def Name(self) -> str:
        return self._name

    @Name.setter
    def Name(self, value: str) -> None:
        self._name = value if value is not None else ""

    @property
    def Version(self) -> int:
        return self._version

    @Version.setter
    def Version(self, value: int) -> None:
        self._version = int(value)

    @property
    def Description(self) -> str:
        return self._description

    @Description.setter
    def Description(self, value: str) -> None:
        self._description = value if value is not None else ""

    # ==================================================================================
    def resolvePath(self, themeName: str) -> str:
        """Return absolute path for this named option under themes/options/<theme>/."""
        if not self._name:
            raise ValueError("OptionsBase.Name must be non-empty to resolve a path")
        if not themeName or not str(themeName).strip():
            raise ValueError("themeName must be non-empty")
        relative = os.path.join(
            C_THEMES_SUBDIR,
            C_OPTIONS_SUBDIR,
            str(themeName).strip(),
            f"{self._name}.json",
        )
        return getConfigPath(relative)
