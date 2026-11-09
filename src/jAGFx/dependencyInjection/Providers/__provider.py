# ==================================================================================
from inspect import currentframe
from typing import Any, Callable

# ==================================================================================
from ...singleton import SingletonM
from ...types.interface.dependencyInjection import iDependency, iDependent, iProvider
from ..lifecycle import Factory, LifeCycleBase, Singleton, Transient


# ==================================================================================
class _provider(metaclass=SingletonM):
    def __init__(self):
        self._dependents: dict[type[iDependent], dict[type[iDependency], str]] = {}
        self._defaults: dict[type[iDependency], str] = {}

        self._dependencies: dict[type[iDependency], dict[str, LifeCycleBase]] = {}

    def _register(
        self,
        genericInterface: type[iDependency],
        dependency: LifeCycleBase[Any],
        dependent: type[iDependent] | None = None,
        isDefault: bool = False,
    ):
        # create interface(contract) library
        if genericInterface not in self._dependencies:
            self._dependencies.update({genericInterface: {}})

        # set default settings
        isDefault = (
            isDefault
            or dependency.DependencyId not in self._dependencies[genericInterface]
        )

        if isDefault:
            self._defaults.update({genericInterface: dependency.DependencyId})

        self._dependencies[genericInterface].update({dependency.DependencyId: dependency})

        if dependent is not None:
            if dependent not in self._dependents:
                self._dependents.update({dependent: {}})

            self._dependents[dependent].update({genericInterface: dependency.DependencyId})

    def RegisterSingleton(
        self,
        genericInterface: type[iDependency],
        dependency: iDependency | type[iDependency],
        dependent: type[iDependent] | None = None,
        isDefault: bool = False,
        *args,
        **kwargs,
    ):
        lDependency: Singleton = Singleton(genericInterface, dependency, *args, **kwargs)
        self._register(genericInterface, lDependency, dependent=dependent, isDefault=isDefault)

    def RegisterTransient(self,genericInterface: type[iDependency],dependency: type[iDependency],dependent: type[iDependent] | None = None,
        isDefault: bool = False,
        *args,
        **kwargs,
    ):
        lDependency: Transient = Transient(genericInterface, dependency, *args, **kwargs
                                           )
        self._register(genericInterface, lDependency, dependent=dependent, isDefault=isDefault)

    def RegisterFactory(
        self,
        genericInterface: type[iDependency],
        dependency: Callable[..., iDependency],
        dependent: type[iDependent] | None = None,
        isDefault: bool = False,
        *args,
        **kwargs,
    ):
        lDependency: Factory = Factory(genericInterface, dependency, *args, **kwargs)
        self._register(
            genericInterface, lDependency, dependent=dependent, isDefault=isDefault
        )

    def Resolve(self, genericInterface: type[iDependency], *args, **kwargs) -> iDependency:

        # gets the default, empty string there is no default
        lDependencyName: str = self._defaults.get(genericInterface, "")

        # Check and use the current caller registered dependency if available
        lCurrentframe = currentframe()
        if lCurrentframe is not None and hasattr(lCurrentframe, "f_back"):
            lCallerFrame = lCurrentframe.f_back
            if lCallerFrame is not None:
                lCallerSelf = lCallerFrame.f_locals.get("self", None)
                if lCallerSelf is not None:
                    lCallerType = type(lCallerSelf)
                    if lCallerType in self._dependents:
                        lDependencyName: str = self._dependents[lCallerType].get(genericInterface, lDependencyName)

        lLCList: dict[str, LifeCycleBase] = self._dependencies.get(genericInterface, {})
        lDependency: LifeCycleBase | None = lLCList.get(lDependencyName, None)

        lInstance: iDependency | None = None
        if lDependency is not None:
            lInstance = lDependency.create(*args, **kwargs)

        return lInstance


Provider: _provider = _provider()
