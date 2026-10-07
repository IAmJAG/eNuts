# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from ...components import iComponentBase


# ==================================================================================
@runtime_checkable
class iSideBarItem(iComponentBase, Protocol):...