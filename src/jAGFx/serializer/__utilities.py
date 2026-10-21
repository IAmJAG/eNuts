# ==================================================================================
from datetime import datetime
from enum import Enum
from importlib import import_module
from inspect import isfunction
from sys import modules
from typing import Any, Dict, Type, get_type_hints
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
        raise Exception(f"Error occur: Type Error {lType.__name__}: {ex!r}") from ex

    except Exception as ex:
        raise Exception(f"Error occur initializing {lType.__name__}: {ex!r}") from ex


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
            if lType is None:
                raise ModuleNotFoundError(f"Unable to resolve type path {lClass!r}")

            if issubclass(lType, Enum):
                return _decodeEnum(lType, obj)

            elif issubclass(lType, iSerializable):
                return _decodeSerializeable(lType, obj)

            else:
                if isfunction(lType):
                    lNewObj: iSerializable = _decodeFunction(lType, obj)
                    if lNewObj is not None:
                        return lNewObj

                payload = {k: v for k, v in obj.items() if k != "__type__"}
                lNewObj = lType(**payload)
                return lNewObj

        except ModuleNotFoundError as ex:
            raise Exception(f"Module {lClass} not found!") from ex

        except AttributeError as ex:
            raise Exception(f"Class {lClass} not found in module!") from ex

        except Exception as e:
            raise Exception(
                f"Error trying to deserialize {lClass}: {e!r}"
            ) from e

    return None


# ==================================================================================
def jsonDecode(obj: Any):
    try:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj

        if isinstance(obj, list):
            return [jsonDecode(lVal) for lVal in obj]

        if isinstance(obj, tuple):
            return tuple(jsonDecode(lVal) for lVal in obj)

        if isinstance(obj, dict):
            lNewObj = _decodeCustomType(obj)
            if lNewObj is not None:
                return lNewObj

            if "__datetime__" in obj:
                return datetime.fromisoformat(obj["__datetime__"])

            if "__uuid__" in obj:
                return UUID(obj["__uuid__"])

            return {lKey: jsonDecode(lValue) for lKey, lValue in obj.items()}

        if type(obj).__name__ in KNOWN_TYPES:
            return obj

        warning(f"jsonDecode: Unknown type {type(obj)}")
        return obj

    except Exception as ex:
        raise ex


def importClass(clsPth: str) -> Type | None:
    """Resolve 'package.module.Class' from sys.modules or via importlib."""
    lModName, lClassName = clsPth.rsplit(".", 1)

    for lName, lModule in modules.items():
        if lModule and (lName == lModName or lName.endswith("." + lModName)):
            if hasattr(lModule, lClassName):
                return getattr(lModule, lClassName)

    try:
        lModule = import_module(lModName)
    except ModuleNotFoundError:
        private = f"{lModName}.__{lClassName[0].lower()}{lClassName[1:]}"
        try:
            lModule = import_module(private)
        except ModuleNotFoundError:
            return None

    if hasattr(lModule, lClassName):
        return getattr(lModule, lClassName)

    return None
