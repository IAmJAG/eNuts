# ==================================================================================
from ...types.interface.logger import iSourceInformation


# ==================================================================================
class BaseSourceInformation(iSourceInformation):
    __slots__ = ["_module", "_class", "_member", "_package", "_file"]
    def __init__(self, file: str, package: str, module: str = None, klass: str = None, member: str = None):
        self._module: str = module
        self._class: str = klass
        self._member: str = member
        self._package: str = package
        self._file: str = file
            
    @property
    def fullyQualifiedName(self) -> str:
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
    def sns(self) -> str:        
        return f"{self.package if not self.klass else self.klass}.{self.member}"

    @property
    def file(self) -> str:
        return self._file
    
    @property
    def package(self) -> str:
        return self._package    
    
    @property
    def module(self) -> str:
        return self._module.strip() if self._module else ""

    @property
    def klass(self) -> str:
        return self._class.strip() if self._class else ""

    @property
    def member(self) -> str:
        return self._member.strip() if self._member else ""

    @property
    def __repr__(self):
        return f"CallerInformation:" \
                f"{LF}{TAB}File: {self.file}" \
                f"{LF}{TAB}Package: {self.package}" \
                f"{LF}{TAB}Module: {self.module}" \
                f"{LF}{TAB}Class: {self.klass}" \
                f"{LF}{TAB}Member: {self.member}"

    def __str__(self):
        return self.fullyQualifiedName
