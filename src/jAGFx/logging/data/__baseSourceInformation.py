# ==================================================================================
from ...types.interface.logger import iSourceInformation


# ==================================================================================
class BaseSourceInformation(iSourceInformation):
    __slots__ = ["_module", "_class", "_member", "_package", "_file"]
    def __init__(self, File: str, Package: str, Module: str = None, Class: str = None, Member: str = None):
        self._module: str = Module
        self._class: str = Class
        self._member: str = Member
        self._package: str = Package
        self._file: str = File
        ##self.Properties.extend(["Module", "Class", "Member", "File", "Package"])
            
    @property
    def FullyQualifiedName(self) -> str:
        if self._class is None or self._class == '':
            fqn = f"{'' if self._package is None else self._package}"
            if self._module is not None: fqn = f"{fqn}.{self._module}"
            if self._member is not None: fqn = f"{fqn}.{self._member}"
            return fqn
        
        fqn = f"{'' if self._package is None else self._package}"
        if self._module is not None: fqn = f"{fqn}.{self._module}"
        if self._class is not None: fqn = f"{fqn}.{self._class}"
        if self._member is not None: fqn = f"{fqn}.{self._member}"
        return fqn

    @property
    def File(self) -> str:
        return self._file
    
    @property
    def Package(self) -> str:
        return self._package    
    
    @property
    def Module(self) -> str:
        return self._module.strip() if self._module else ""

    @property
    def Class(self) -> str:
        return self._class.strip() if self._class else ""

    @property
    def Member(self) -> str:
        return self._member.strip() if self._member else ""

    @property
    def __repr__(self):
        return f"CallerInformation:" \
                f"{LF}{TAB}File: {self.File}" \
                f"{LF}{TAB}Package: {self.Package}" \
                f"{LF}{TAB}Module: {self.Module}" \
                f"{LF}{TAB}Class: {self.Class}" \
                f"{LF}{TAB}Member: {self.Member}"

    def __str__(self):
        return self.FullyQualifiedName
