# ==================================================================================
from inspect import isclass

# ==================================================================================
from ...types.interface.dependencyInjection import iDependency
from .__lifecyclebase import D, LifeCycleBase


# ==================================================================================
class Singleton(LifeCycleBase[D]):
    def __init__(self, dependencyReference: type[D], dependency: D | type[D], *args, **kwargs):
        # Call the base class constructor first
        super().__init__(dependencyReference)

        lResolvedDependency: D

        if isclass(dependency) and issubclass(dependency, iDependency):
            # If a class is provided, instantiate it
            lResolvedDependency = dependency(*args, **kwargs)

        elif isinstance(dependency, iDependency):
            # If an instance is provided, use it directly
            lResolvedDependency = dependency

        else:
            # If neither a class nor an instance is provided, it's an error
            raise TypeError(f"Dependency is expected to be an instance or a subclass of {iDependency.__name__}, "
                            f"got {type(dependency).__name__} instead.")

        # Type check to ensure the resolved_dependency matches the generic type D
        # This check is more robust and ensures the instance is of the expected type
        if not isinstance(lResolvedDependency, dependencyReference):
             raise TypeError(f"Provided dependency instance ({type(lResolvedDependency).__name__}) "
                             f"does not match the registered dependency reference ({dependencyReference.__name__}).")

        self._instance: D = lResolvedDependency
        self._id = type(lResolvedDependency).__qualname__

    @property
    def DependencyId(self) -> str:
        return self._id

    def create(self, *args, **kwargs) -> D:
        # For a singleton, 'create' just returns the already held instance
        return self._instance
