# ==================================================================================
from enum import Enum


# ==================================================================================
class ShowAnimation(str, Enum):
    """Available window show animations."""

    Popup = "popup"
    SlideRight = "slideRight"
    SlideLeft = "slideLeft"
    SlideTop = "slideTop"
    SlideDown = "slideDown"
