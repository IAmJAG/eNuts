# ==================================================================================
from ...types.interface.dependencyInjection import iDependent
from ..Providers import Provider


# ==================================================================================
class Dependent(iDependent):
    @property
    def Provider(self):
        return Provider
