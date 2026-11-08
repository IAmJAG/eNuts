# ==================================================================================
from enum import Enum


# ==================================================================================
class eCanvasFitMode(Enum):
    """
    How content is mapped into the widget on resize.

    Scale  — scale proportionally to fit inside the widget (letterbox / pillarbox).
    Fill   — stretch to fill the entire widget (aspect ignored).
    Crop   — scale proportionally to cover the widget, center, crop overflow.
    """
    Scale = "scale"
    Fill = "fill"
    Crop = "crop"


# ==================================================================================
eImageFitMode = eCanvasFitMode
# ==================================================================================

# ==================================================================================
__all__ = ["eCanvasFitMode", "eImageFitMode"]
# ==================================================================================
