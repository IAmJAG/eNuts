# ==================================================================================
# src/jAGFx/types/__typeChecks.py
# ==================================================================================
import ast
import collections.abc
import inspect

# ==================================================================================
from inspect import Parameter as _parameter
from inspect import isclass
from types import UnionType
from typing import Any, Union, get_origin


# ==================================================================================
def isNoOpMethod(fn) -> bool:
    if fn is None: return True

    lActualFn = inspect.unwrap(fn)    
    if not inspect.isroutine(lActualFn):
        return False

    try:
        lSource = inspect.getsource(lActualFn)
        lSource = inspect.cleandoc(lSource)
        lParsedAst = ast.parse(lSource)

    except (TypeError, OSError, SyntaxError):
        return False

    lFuncDef = lParsedAst.body[0]
    if not isinstance(lFuncDef, (ast.FunctionDef, ast.AsyncFunctionDef)): return False

    lBody = lFuncDef.body

    for lStmt in lBody:
        if isinstance(lStmt, ast.Pass): continue

        if isinstance(lStmt, ast.Expr):
            lValue = lStmt.value
            if isinstance(lValue, ast.Constant):
                if lValue.value is Ellipsis or isinstance(lValue.value, (str, type(None))):
                    continue

        if isinstance(lStmt, ast.Return):
            if lStmt.value is None or (isinstance(lStmt.value, ast.Constant) and lStmt.value.value is None):
                continue

        return False

    return True

# ==================================================================================
def isUnion(paramType):
    return (hasattr(paramType, "__origin__") and paramType.__origin__ is Union) or type(paramType) is UnionType

# ==================================================================================
def isAny(paramType):
    return paramType in [_parameter.empty, Any, any]

# ==================================================================================
def isNone(paramType):
    return paramType in [None, type(None), EMPTY, EMPTYLIST, EMPTYDICT, EMPTYSET]

# ==================================================================================
def isListOfT(data: list, t: type) -> bool:
    return bool(data) and isinstance(data, list) and all(isinstance(i, t) for i in data)

# ==================================================================================
def _isStandardType(provided: Any, expectedType: type) -> bool:
    if provided != expectedType:
        if isclass(provided):
            return issubclass(provided, expectedType)
        else:
            return isinstance(provided, expectedType)
    else:
        return True

# ==================================================================================
def _isGenericType(provided: Any, expectedType: type, expected_origin) -> bool:
    if isclass(provided):
        provided_origin = get_origin(provided)
        compare_provided = provided_origin if provided_origin is not None else provided

    elif getattr(provided, "__orig_bases__", None) is not None and get_origin(provided) is not None:
        provided_origin = get_origin(provided)
        return Is(provided_origin, expected_origin)
    else:
        compare_provided = type(provided)

    try:
        if isclass(compare_provided):
            if expected_origin is collections.abc.Sequence:
                return issubclass(compare_provided, collections.abc.Sequence)
            if expected_origin is collections.abc.Mapping:
                return issubclass(compare_provided, collections.abc.Mapping)
            return issubclass(compare_provided, expected_origin)

        return False

    except TypeError:
        return False

# ==================================================================================
def Is(provided: Any, expectedType: type) -> bool:
    try:
        return _isStandardType(provided, expectedType)

    except TypeError:
        try:
            if isinstance(provided, expectedType):
                return True

        except TypeError:
            pass

        expected_origin = get_origin(expectedType)

        if expected_origin is Union:
            return isUnion(provided)

        if expected_origin is not None:
            return _isGenericType(provided, expectedType, expected_origin)

        return False
    except Exception:
        return False
    
