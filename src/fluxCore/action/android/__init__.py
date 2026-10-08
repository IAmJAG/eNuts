# ==================================================================================
# src/fluxCore/action/android/__init__.py
# Lazy export so importing action.android.enums does not load AndroidAction first.
# ==================================================================================


def __getattr__(name: str):
    if name == "AndroidAction":
        from .__androidAction import AndroidAction

        return AndroidAction
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ==================================================================================
__all__ = ["AndroidAction"]
