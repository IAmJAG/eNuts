# ==================================================================================
from functools import wraps
from inspect import isclass
from threading import RLock
from typing import Any, Callable

# ==================================================================================
_SINGLETONINSTANCES: dict[type, object] = dict[type, object]()
_INSTANCELOCK: RLock = RLock()

# ==================================================================================
class SingletonM: 
    def __call__(cls, *args, **kwargs) -> Any:
        if cls not in _SINGLETONINSTANCES:
            with _INSTANCELOCK:
                if cls not in _SINGLETONINSTANCES:
                    instance = super().__call__(*args, **kwargs)
                    _SINGLETONINSTANCES[cls] = instance
        return _SINGLETONINSTANCES[cls]

# ==================================================================================
def SingletonF(cls: type) -> Callable[..., Any]:  # Singleton Decorator the class becomes Function
    if not isclass(cls):
        raise TypeError("Singleton decorator can only be applied to classes.")

    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in _SINGLETONINSTANCES:
            with _INSTANCELOCK:
                if cls not in _SINGLETONINSTANCES:
                    _SINGLETONINSTANCES[cls] = cls(*args, **kwargs)
                return _SINGLETONINSTANCES[cls]

    return getinstance

# ==================================================================================
def SingletonC(cls: type) -> type: # Singleton Decorator: the class stay as class
    if not isclass(cls):
        raise TypeError("Singleton decorator must be applied to a class.")

    lOrigNew = cls.__new__
    lOrigInit = cls.__init__    

    def _init(self, *args, **kwargs):                
        if hasattr(self, "_initialized"): return        
        lOrigInit(self, *args, **kwargs)
        setattr(cls, "_initialized", True)

    def _new(_cls, *args, **kwargs):
        if _cls not in _SINGLETONINSTANCES:
            with _INSTANCELOCK:
                if _cls not in _SINGLETONINSTANCES:
                    if lOrigNew is object.__new__:
                        instance = object.__new__(_cls)

                    else:
                        instance = lOrigNew(_cls, *args, **kwargs)

                    _SINGLETONINSTANCES[_cls] = instance

        return _SINGLETONINSTANCES[_cls]

    cls.__new__ = _new
    cls.__init__ = _init
    return cls
