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
        def _processNames(_names: dict[str, bool]):
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
        maxLen: int = min(maxLen, 32)  # make the name length up to 32

        # in case the user is confused :). Normalize the variable
        lMinMax = [minLen, maxLen]
        maxLen = max(lMinMax)
        minLen = min(lMinMax)

        try:
            lName: str = EMPTY
            if trueName:            
                lChoices: list[str] = {
                    name: value
                    for name, value in self._names.items()
                    if len(name) >= minLen <= maxLen and not value
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


# class _names(metaclass=SingletonM):
#     POPCONST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

#     def __init__(self):
#         self._manager = Manager()

#         self._namesFilename = "./assets/names.json"
#         self._names: dict[str, dict[str, int]] = self._manager.dict()
#         self._snames: dict[int, list[str]] = self._manager.dict()
#         self._fnames: dict[int, list[str]] = self._manager.dict()

#         self._snames[0] = self._manager.list()
#         self._snames[1] = self._manager.list()
#         self._fnames[0] = self._manager.list()
#         self._fnames[1] = self._manager.list()

#         self._usedNames: list[str] = self._manager.list()
#         self._ender: object = None
#         self._loadNames()

#         def _cleanup():
#             self._ender = None

#         atexit.register(_cleanup)

#     def _loadNames(self):
#         lNames: dict[str, dict[str, int]] = dict[str, dict[str, int]]()
#         try:
#             with open(self._namesFilename) as lFile:
#                 lNames = json.load(lFile)

#         except json.JSONDecodeError:
#             try:
#                 with open(self._namesFilename, encoding="utf-8") as lFile:
#                     lNames = json.load(lFile)

#                 self._saveNames()

#             except Exception as ex:
#                 raise Exception("Names file read error") from ex

#         except Exception as ex:
#             raise Exception("Names file read error") from ex

#         if not lNames:
#             raise Exception("Names is empty")

#         for lPart, lXNames in lNames.items():
#             lPart = lPart.strip()
#             if lPart not in self._names:
#                 self._names[lPart] = self._manager.dict()

#             lErrorOccured: bool = False
#             for lName, lValue in lXNames.items():
#                 try:
#                     self._names[lPart][lName.strip()] = lValue

#                 except Exception as ex:
#                     raise Exception("Error populating names") from ex
#                     lErrorOccured = True
#                     break

#                 if lPart == "firstnames":
#                     self._fnames[0].append(lName.strip())

#                 elif lPart == "surnames":
#                     self._snames[0].append(lName.strip())

#             if lErrorOccured:
#                 break

#         if self._fnames is None:
#             self._fnames = self._manager.dict()
#             self._fnames[0] = self._manager.list()
#             self._fnames[1] = self._manager.list()

#         if self._snames is None:
#             self._snames = self._manager.dict()
#             self._snames[0] = self._manager.list()
#             self._snames[1] = self._manager.list()

#         self._snames[0][:] = []
#         self._snames[1][:] = []
#         self._fnames[0][:] = []
#         self._fnames[1][:] = []

#         self._fnames[0].extend(list(self._names["firstnames"].keys()))
#         self._snames[0].extend(list(self._names["surnames"].keys()))

#     def _saveNames(self):
#         with open(self._namesFilename, "w") as lFile:
#             lNames: dict[str, dict[str, int]] = dict[str, dict[str, int]]()
#             for lNType, lXNames in self._names.items():
#                 if lNType not in lNames:
#                     lNames[lNType] = dict[str, int]()
#                 for lKey, lVal in lXNames.items():
#                     lNames[lNType][lKey.strip()] = lVal

#             json.dump(lNames, lFile)

#     def objectName(self, obj):
#         if hasattr(obj, "_name"):
#             obj._name = self.RandomNames()

#             def _objCleanName():
#                 lName: str = obj._name
#                 lSName, lFName = lName.split(",")
#                 if lName in self._usedNames:
#                     self._usedNames.remove(lName)
#                 self._names["firstnames"][lFName.strip()] -= 1
#                 self._names["surnames"][lSName.strip()] -= 1
#                 self._saveNames()

#             wref(obj, _objCleanName)

#     def RandomNames(self, trueName: bool = True, length: int = 12):
#         lName: str = ""
#         try:
#             if trueName:
#                 while True:
#                     if len(self._fnames[0]) == 0:
#                         self._fnames[0].extend(self._fnames[1])
#                         self._fnames[1][:] = []

#                     if len(self._snames[0]) == 0:
#                         self._snames[0].extend(self._snames[1])
#                         self._snames[1][:] = []
#                         if not self._snames[0]:
#                             break

#                     lFName: str = random.choice(list(self._fnames[0]))
#                     lSName: str = random.choice(list(self._snames[0]))

#                     lName = f"{lSName}, {lFName}"

#                     if lName not in self._usedNames:
#                         self._usedNames.append(lName)
#                         self._names["firstnames"][lFName] += 1
#                         self._names["surnames"][lSName] += 1
#                         self._saveNames()

#                         self._fnames[0].remove(lFName)
#                         self._fnames[1].append(lFName)

#                         self._snames[0].remove(lSName)
#                         self._snames[1].append(lSName)
#                         break

#             if lName == "":
#                 while lName in self._usedNames:
#                     lName = f"{(lambda: ''.join(random.choices(_names.POPCONST, k=length)))()}"

#                 self._usedNames.append(lName)
#             return lName

#         except Exception as ex:
#             raise Exception("Error generating random name") from ex

#     def ResetNames(self):
#         for lPart, lNames_dict_proxy in self._names.items():
#             for lName in list(lNames_dict_proxy.keys()):
#                 lNames_dict_proxy[lName.strip()] = 0

#         self._usedNames[:] = []

#         self._fnames[0][:] = list(self._names["firstnames"].keys())
#         self._fnames[1][:] = []
#         self._snames[0][:] = list(self._names["surnames"].keys())
#         self._snames[1][:] = []

#         self._saveNames()
