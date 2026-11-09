# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from .__dependency import iDependency


# ==================================================================================
@runtime_checkable
class iDependent(Protocol):
    @property
    def ResolveDepency(self, iDependency) -> iDependency:
        raise NotImplementedError("Provider property is not implemented.")
