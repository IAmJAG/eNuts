# ==================================================================================
from typing import Callable, Type

from .__lifecyclebase import D, LifeCycleBase


# ==================================================================================
class Factory(LifeCycleBase[D]):
    def __init__(self, dependencyReference: Type[D], factory: Callable[..., D], *args, **kwargs):
        super().__init__(dependencyReference)

        if not callable(factory):
            raise TypeError("Factory callable must be a function, method, or callable object.")

        self._factory: Callable[..., D] = factory
        self._args = args
        self._kwargs = kwargs
        self._id = self._factory.__qualname__ if hasattr(self._factory, '__qualname__') else str(factory)

    @property
    def DependencyId(self) -> str:
        return self._id

    def create(self, *args, **kwargs) -> D | None:
        lArgs, lKWArgs = (args, kwargs) if (len(args) > 0 or len(kwargs) > 0) else (self._args, self._kwargs)

        instance = self._factory(*lArgs, **lKWArgs)
        return instance
