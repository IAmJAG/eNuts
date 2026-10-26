# ==================================================================================
# src/jAGQt/widgets/Image/__fitMode.py
# ==================================================================================
from enum import Enum


# ==================================================================================
class ImageFitMode(Enum):
    """How the image is mapped into the widget on resize.

    Scale  — scale proportionally to fit inside the widget (letterbox / pillarbox).
    Fill   — stretch to fill the entire widget (aspect ignored).
    Crop   — scale proportionally to cover the widget, center, crop overflow.
    """

    Scale = "scale"
    Fill = "fill"
    Crop = "crop"
