# ==================================================================================
# src/jAGFx/names/__names.py
# ==================================================================================
import json
import random

# ==================================================================================
from ..collections import TSDictionary
from ..singleton import SingletonC

# ==================================================================================
__all__ = ["_names"]
# ==================================================================================

# ==================================================================================
@SingletonC
class _names:
    def __init__(self):
        self._namesFileName = "./assets/names.json"
        self._names: TSDictionary = self._loadNames()

    def _loadNames(self) -> TSDictionary:
        def _processNames(lNames: dict[str, bool]):
            lUniqueKeys: set = set()
            lUNames: dict[str, bool] = {}
            for name, value in lNames.items():
                if name not in lUniqueKeys:
                    lUNames.update({name: value})
                    lUniqueKeys.add(name)

            return lUNames

        lNames: dict[str, bool] = {}
        try:
            with open(self._namesFileName, "r") as lFile:
                lNames = json.load(lFile)

            return TSDictionary(_processNames(lNames))

        except (json.JSONDecodeError, UnicodeDecodeError):
            with open(self._namesFileName, "r", encoding="utf-8-sig") as lFile:
                lNames = json.load(lFile)

            with open(self._namesFileName, "w") as lFile:
                json.dump(lNames, lFile)

            return TSDictionary(_processNames(lNames))

        except Exception as ex:
            raise ex

    def _saveNames(self):
        with open(self._namesFileName, "w") as lFile:
            json.dump(self._names, lFile, indent=4)

    def RandomName(self, minLen: int = -1, maxLen: int = -1, trueName: bool = True):
        lName: str = ""
        minLen: int = max(minLen, 4)  # make the name length down to 4
        maxLen: int = min(maxLen, 32) if maxLen > 0 else 32  # make the name length up to 32

        # in case the user is confused :). Normalize the variable
        lMinMax = [minLen, maxLen]
        maxLen = max(lMinMax)
        minLen = min(lMinMax)

        try:
            lName: str = EMPTY
            if trueName:
                lChoices: dict[str, bool] = {
                    name: value
                    for name, value in self._names.items()
                    if minLen <= len(name) <= maxLen and not value
                }

                if len(lChoices) > 0:
                    lName = random.choices(list(lChoices.keys()))[0]
                    self._names[lName] = True

            if lName == "":
                lPopConst = (
                    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                )
                lName = f"{(lambda: ''.join(random.choices(lPopConst, k=maxLen)))()}"

            return lName

        except Exception as ex:
            raise ex

    def SecureName(self, name: str):
        if name in self._names:
            lXName = self._names[name]
            self._names[name] = True

            if lXName is False:
                self._saveNames()

    def ResetNames(self):
        for lName in self._names:
            self._names[lName] = False
        self._saveNames()
