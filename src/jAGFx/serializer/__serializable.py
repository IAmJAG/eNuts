# ==================================================================================
import datetime

# ==================================================================================
from enum import Enum
from typing import Any, Dict, List
from uuid import UUID
from weakref import ref as wref

# ==================================================================================
from ..types.interface.serializer import iSerializable
from .__utilities import jsonDecode


# ==================================================================================
class Serializable(iSerializable):
    def __init__(self) -> None:
        self._properties: list[str] = []
        wref(self, self.cleanUp)

    @property
    def Properties(self) -> list[str]:
        return self._properties

    def cleanUp(self):
        debug(f"Cleaning up {type(self).__name__}...")

    def encode(self) -> Dict[str, object]:
        lErrors: List[Exception] = list[Exception]()
        lDict: Dict[str, object] = dict[str, object]()

        try:
            for attrbName in self.Properties:
                try:
                    if attrbName.startswith("_"): continue
                    lvalue, lskip = self._encodeProperty(attrbName)
                    if lskip: continue
                    lDict[attrbName] = lvalue

                except KeyError:
                    lErrors.append(
                        KeyError(
                            f"Error encoding {type(self).__name__}. Could not find {attrbName} key _{attrbName.lower()}"
                        )
                    )

                except Exception as e:
                    lErrors.append(
                        Exception(
                            f"Unhandled exception from encoding {type(self).__name__}: {e!r}"
                        )
                    )

            lModule: list[str] = self.__module__.split(".")
            if lModule[len(lModule) - 1].startswith("__"):
                lModule: str = ".".join(lModule[:-1])

            else:
                lModule: str = ".".join(lModule)

            lDict["__type__"] = f"{lModule}.{type(self).__name__}"
            if lErrors:
                raise Exception(f"Encoding encountered {len(lErrors)} error(s): {lErrors}")

            return lDict

        except Exception as ex:
            raise Exception(f"Error encoding {type(self).__name__}") from ex

    def decode(self, dct: Any):
        lErrors: List[Exception] = list[Exception]()
        for attrbName in self.Properties:
            if attrbName.startswith("_"): continue

            try:
                lval = self._decodeProperty(dct, attrbName)
                if lval is not None:
                    lval = jsonDecode(lval)
                    if not hasattr(self, f"_{attrbName}"):
                        raise KeyError(f"Could not find property {attrbName} key _{attrbName}")
                    setattr(self, f"_{attrbName}", lval)

            except KeyError:
                lErrors.append(
                    KeyError(
                        f"Error decoding {type(self).__name__}. Could not find {attrbName} key _{attrbName}"
                    )
                )

            except Exception as ex:
                # Preserve the real cause — was previously swallowed as a bare string.
                lErrors.append(
                    Exception(
                        f"Unhandled exception from decoding {type(self).__name__}.{attrbName}: {ex!r}"
                    )
                )

        if lErrors:
            raise Exception(f"Decoding encountered {len(lErrors)} error(s): {lErrors}")

    def _encodeProperty(self, prop: str):
        def _exEncode(obj: iSerializable | Any):
            if isinstance(obj, dict):
                return {k: _exEncode(v) for k, v in obj.items()}

            if isinstance(obj, list):
                return [_exEncode(v) for v in obj]

            if isinstance(obj, tuple):
                return tuple(_exEncode(v) for v in obj)

            if isinstance(obj, iSerializable):
                return obj.encode()

            if isinstance(obj, Enum):
                lEnum = {
                    "__member__": obj.name,
                    "__type__": f"{obj.__module__}.{type(obj).__name__}",
                }
                return lEnum

            if isinstance(obj, UUID):
                return {"__uuid__": str(obj)}

            if isinstance(obj, datetime.datetime):
                return {"__datetime__": obj.isoformat()}

            return obj

        lProp = _exEncode(getattr(self, f"_{prop}", None))
        return lProp, False

    def _decodeProperty(self, dct: dict, lProp: str):
        return dct.get(lProp, None)
