# ==================================================================================
from inspect import isclass

# ==================================================================================
from ...types.interface.dependencyInjection import iDependency
from .__lifecyclebase import D, LifeCycleBase


# ==================================================================================
class Transient(LifeCycleBase[D]):
    def __init__(self, dependencyReference: type[D], dependency: type[D], *args, **kwargs):
        super().__init__(dependencyReference)

        if not isclass(dependency) or not issubclass(dependency, iDependency):
            raise ValueError(f"Dependency is expected to be a subclass of {dependencyReference.__name__}")

        self._instance: type[D] = dependency
        self._args = args
        self._kwargs = kwargs
        self._id = dependency.__qualname__

    @property
    def DependencyId(self) -> str:
        return self._id

    def create(self, *args, **kwargs) -> D | None:
        if len(args) > 0 or len(kwargs) > 0:
            lArgs, lKWArgs = args, kwargs
        else:
            lArgs, lKWArgs = self._args, self._kwargs

        return self._instance(*lArgs, **lKWArgs)
