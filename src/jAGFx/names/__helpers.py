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
        return lGen.RandomNames(trueName=trueName, maxLen=length, minLen=5)

    except Exception as ex:
        raise ex
    
# ==================================================================================
def resetNames():
    lGen: _names = _names()
    lGen.ResetNames()

# ==================================================================================
def name(obj):
    lGen: _names = _names()
    lGen.objectName(obj)
