
class SideBarConfig:
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            
            setattr(self, f"_{k}", v)

    Title: str = ""
    ExpandedWidth: int = 240
    CollapsedWidth: int = 48
    IconSize: int = 24
    DockPosition: DockPosition = DockPosition.Left
    StartCollapsed: bool = False
    AutoCollapse: bool = False
    AnimationDurationMs: int = 220
