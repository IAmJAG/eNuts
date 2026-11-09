# ==================================================================================
from inspect import isclass
from typing import Generic, TypeVar

# ==================================================================================
from ...types.interface.dependencyInjection import iDependency

# ==================================================================================
D = TypeVar('D', bound=iDependency)
# ==================================================================================

# ==================================================================================
class LifeCycleBase(Generic[D]):
    def __init__(self, dependencyReference: type[D]):

        if type(self) is LifeCycleBase:
            raise TypeError("LifeCycleBase cannot be instantiated directly. Use one of its subclasses.")

        if not isclass(dependencyReference):
            raise TypeError(f"Dependency Reference is expected to be a class, a subclass of {D.__name__}")

        if not issubclass(dependencyReference, iDependency):
            raise TypeError(f"Dependency Reference is expected to be a subclass of {D.__name__}, got {dependencyReference.__name__} instead.")

    @property
    def DependencyId(self) -> str:
        raise NotImplementedError("Subclasses must DependencyId property.")

    def create(self, *args, **kwargs) -> D | None:
        raise NotImplementedError("Subclasses must implement the 'create' method.")
