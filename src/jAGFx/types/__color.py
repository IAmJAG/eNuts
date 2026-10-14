# ==================================================================================
from typing import Union, overload


# ==================================================================================
class Color:
    CL_DEFAULT_ALPHA: float = 1.0
    def __init__(self, *args, **kwargs) -> None:
        self._alpha: float = 1.0
        self._red: float = 0.0
        self._green: float = 0.0
        self._blue: float = 0.0

        if kwargs:
            alphaVal = kwargs.get("a", kwargs.get("alpha", 1.0))
            redVal = kwargs.get("r", kwargs.get("red", 0.0))
            greenVal = kwargs.get("g", kwargs.get("green", 0.0))
            blueVal = kwargs.get("b", kwargs.get("blue", 0.0))
            self._setValues(alphaVal, redVal, greenVal, blueVal)
            return

        if not args:
            return

        firstArg = args[0]

        if isinstance(firstArg, str):
            self._parseHex(firstArg)

        elif isinstance(firstArg, tuple):
            if len(firstArg) == 3:
                rVal, gVal, bVal = firstArg
                self._setValues(1.0, rVal, gVal, bVal)
            elif len(firstArg) == 4:
                aVal, rVal, gVal, bVal = firstArg
                self._setValues(aVal, rVal, gVal, bVal)

        else:
            if len(args) == 3:
                rVal, gVal, bVal = args
                self._setValues(1.0, rVal, gVal, bVal)
                
            elif len(args) == 4:
                aVal, rVal, gVal, bVal = args
                self._setValues(aVal, rVal, gVal, bVal)

    def _setValues(
        self,
        alphaVal: Union[float, int],
        redVal: Union[float, int],
        greenVal: Union[float, int],
        blueVal: Union[float, int],
    ) -> None:
        self._alpha = (
            float(alphaVal) / 255.0 if isinstance(alphaVal, int) else float(alphaVal)
        )
        self._red = float(redVal) / 255.0 if isinstance(redVal, int) else float(redVal)
        self._green = (
            float(greenVal) / 255.0 if isinstance(greenVal, int) else float(greenVal)
        )
        self._blue = (
            float(blueVal) / 255.0 if isinstance(blueVal, int) else float(blueVal)
        )

    def _parseHex(self, hexStr: str) -> None:
        hexStr = hexStr.lstrip("#")
        if len(hexStr) == 3:
            r = int(hexStr[0] * 2, 16)
            g = int(hexStr[1] * 2, 16)
            b = int(hexStr[2] * 2, 16)
            self._setValues(255, r, g, b)
        elif len(hexStr) == 6:
            r = int(hexStr[0:2], 16)
            g = int(hexStr[2:4], 16)
            b = int(hexStr[4:6], 16)
            self._setValues(255, r, g, b)
        elif len(hexStr) == 8:
            a = int(hexStr[0:2], 16)
            r = int(hexStr[2:4], 16)
            g = int(hexStr[4:6], 16)
            b = int(hexStr[6:8], 16)
            self._setValues(a, r, g, b)
        else:
            raise ValueError(f"Invalid hex color format: {hexStr}")

    @property
    def Red(self) -> float:
        return self._red

    @property
    def Green(self) -> float:
        return self._green

    @property
    def Blue(self) -> float:
        return self._blue

    @property
    def Alpha(self) -> float:
        return self._alpha

    def toTuple(self) -> tuple[float, float, float, float]:
        return (self._alpha, self._red, self._green, self._blue)

    def toHex(self) -> str:
        aInt = int(round(self._alpha * 255))
        rInt = int(round(self._red * 255))
        gInt = int(round(self._green * 255))
        bInt = int(round(self._blue * 255))
        return f"#{aInt:02x}{rInt:02x}{gInt:02x}{bInt:02x}"
