# ==================================================================================
# src/fluxCore/types/interface/action/__init__.py
# ==================================================================================
from .__actionMetadata import iActionMetadata

# iAndroidAction is imported lazily so loading iActionMetadata (used by Action)
# does not pull action.android and re-enter a circular import.


def __getattr__(name: str):
    if name == "iAndroidAction":
        from .__androidAction import iAndroidAction

        return iAndroidAction
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ==================================================================================
__all__ = ["iActionMetadata", "iAndroidAction"]
