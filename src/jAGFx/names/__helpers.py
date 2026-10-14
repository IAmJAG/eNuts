# ==================================================================================
# src/jAGFx/names/__helpers.py
# ==================================================================================
from .__names import _names

# ==================================================================================
__all__ = ["getRandomName", "name", "resetNames"]

# ==================================================================================
def getRandomName(length: int = 12, trueName: bool = True):
    try:
        lGen: _names = _names()
        return lGen.RandomName(trueName=trueName, maxLen=length, minLen=5)

    except Exception as ex:
        raise ex

# ==================================================================================
def resetNames():
    lGen: _names = _names()
    lGen.ResetNames()

# ==================================================================================
def name(obj):
    lGen: _names = _names()
    if hasattr(lGen, "objectName"):
        lGen.objectName(obj)
    else:
        if not getattr(obj, "_name", None):
            obj._name = lGen.RandomName()
