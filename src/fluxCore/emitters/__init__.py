# ==================================================================================
def __getattr__(name: str):
    if name == "SCRCPYEmitter":
        from .scrcpy import SCRCPYEmitter

        return SCRCPYEmitter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ==================================================================================
__all__ = ["SCRCPYEmitter"]
