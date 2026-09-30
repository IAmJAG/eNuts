# ==================================================================================
from datetime import datetime
from enum import Enum
from inspect import isfunction
from sys import modules
from typing import Dict, Type, get_type_hints
from uuid import UUID

# ==================================================================================
from ..globals.serializer import KNOWN_TYPES
from ..types.interface.serializer import iSerializable


# ==================================================================================
def _decodeEnum(lType, obj):
    try:
        lMember = obj.get("__member__", None)
        lNewObj = lType[lMember]  # type: ignore
        return lNewObj

    except Exception as ex:
        raise Exception(f"Error retrieving enum type {lType.__class__.__name__}") from ex
    
# ==================================================================================
def _decodeSerializeable(lType: type, obj: dict):
    try:
        lNewObj: iSerializable = lType()
        lNewObj.decode(obj)
        return lNewObj
    
    except TypeError as ex:
        raise Exception(f"Error occur: Type Error {lType.__name__}") from ex

    except Exception as ex:
        raise Exception(f"Error occur initializing {lType.__name__}") from ex
    
# ==================================================================================
def _decodeFunction(lType, obj):
    lReturnType: type = get_type_hints(lType)
    if lReturnType is not None:
        if issubclass(lReturnType, iSerializable):
            lNewObj: iSerializable = lType()
            lNewObj.decode(obj)
            return lNewObj
    return None

# ==================================================================================
def _decodeCustomType(obj: Dict):
    lClass: str = obj.get("__type__", None)
    if lClass is not None:
        try:
            lType = importClass(lClass)

            if issubclass(lType, Enum):
                return _decodeEnum(lType, obj)

            elif issubclass(lType, iSerializable):
                return _decodeSerializeable(lType, obj)

            else:
                if isfunction(lType):
                    lNewObj: iSerializable = _decodeFunction(lType, obj)
                    if lNewObj is not None: return lNewObj

                obj.pop("__type__", None)
                lNewObj = lType(**obj)
                return lNewObj

        except ModuleNotFoundError as ex:
            raise Exception(f"Module {lClass} not found!") from ex

        except AttributeError as ex:
            raise Exception(f"Class {lClass} not found in module!") from ex

        except Exception as e:
            raise Exception(f"Error trying to deserialize {type(obj).__name__}") from e

    return None

# ==================================================================================
def jsonDecode(obj: dict):
    try:
        if isinstance(obj, list):
            return [jsonDecode(lVal) for lVal in obj]

        elif isinstance(obj, tuple):
            return (jsonDecode(lVal) for lVal in obj)

        elif isinstance(obj, dict):
            lNewObj = _decodeCustomType(obj)
            if lNewObj is not None:
                return lNewObj

            elif "__datetime__" in obj:
                lNewObj = datetime.fromisoformat(obj["__datetime__"])
                return lNewObj
            
            elif "__uuid__" in obj:
                lNewObj = UUID(obj["__uuid__"])
                return lNewObj
            
            else:
                return {lKey: jsonDecode(lValue) for lKey, lValue in obj.items()}

        if type(obj).__name__ in KNOWN_TYPES:
            return obj

        warning(f"jsonDecode: Unknown type {type(obj)}")
    
    except Exception as ex:
        raise ex

def importClass(clsPth: str) -> Type | None:
    lModName, lClassName = clsPth.rsplit(".", 1)
    for lName, lModule in modules.items():
        if lModule and (lName == lModName or lName.endswith("." + lModName)):
            if hasattr(lModule, lClassName):
                return getattr(lModule, lClassName)

    return None   
