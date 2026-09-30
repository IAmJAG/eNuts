# ==================================================================================
# src/jAGFx/logging/data/__callerInformation.py
# ==================================================================================
from types import FrameType

# ==================================================================================
from utilities import getFrameInfo

# ==================================================================================
from . import BaseSourceInformation


# ==================================================================================
class CallerInformation(BaseSourceInformation):
    __slots__ = ["_lineno"]
    def __init__(
        self, File: str, Package: str, Module: str,
        Class: str, Member: str, LineNo: int
    ):        
        super().__init__(File, Package, Module, Class, Member)
        self._lineno: int = LineNo

    @classmethod
    def fromFrame(cls, frame: FrameType):
        frameInfo = getFrameInfo(frame)
        return cls(
            File=frameInfo["File"],
            Package=frameInfo["Package"],  
            Module=frameInfo["Module"],
            Class=frameInfo["Class"],
            Member=frameInfo["Member"],
            LineNo=frameInfo["LineNo"],
        )

    @property
    def LineNo(self) -> int:
        return self._lineno

    @property
    def __repr__(self):
        return f"CallerInformation:" \
                f"{LF}{TAB}File: {self.File}" \
                f"{LF}{TAB}Package: {self.Package}" \
                f"{LF}{TAB}Module: {self.Module}" \
                f"{LF}{TAB}Class: {self.Class}" \
                f"{LF}{TAB}Member: {self.Member}" \
                f"{LF}{TAB}LineNo: {self.LineNo}"    