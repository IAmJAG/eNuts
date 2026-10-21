# ==================================================================================
from __future__ import annotations

# ==================================================================================
import sys
from pathlib import Path

# ==================================================================================
# Repo root / .test/conftest.py → parents[1] == repo root
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"

if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Runtime builtins (trace, debug, warning, …) come from monkey patch — same as main.py.
# typings/__builtins__.pyi is stubs only; pytest does not load them.
import __monkeyPatch  # noqa: E402, F401
