# ==================================================================================
from typing import TYPE_CHECKING, Protocol, runtime_checkable

# ==================================================================================
if TYPE_CHECKING:    
    from .__commandBarBase import iCommandBarBase


# ==================================================================================
@runtime_checkable
class iCommandBarGroup(iCommandBarBase, Protocol): ...