# ==================================================================================
from PySide6.QtWidgets import QBoxLayout, QLayout

# ==================================================================================
from jAGFx.workflow import workflow
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...configuration import ApplicationInformation
from ..widgets import RevolvingNeuralOrb


# ==================================================================================
@workflow(
    "InitializeSettings", "InitializeUI", "RestoreWindowsState",
    "InitializeInfo"
)
class MainWindow(MainWindowBase, ApplicationInformation):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", frameless=False, *args, **kwargs)

    # ------------------------------------------------------------------ Layout override
    @property
    def Layout(self) -> QBoxLayout:
        lLayout: QLayout | None = getattr(self, "_layout", None)
        if lLayout is None:
            lCentral = self.centralWidget()
            if lCentral is not None:
                lLayout = lCentral.layout()

        if lLayout is None:
            lLayout = self.layout()

        if lLayout is not None and lLayout.count() == 0:
            lOrb = RevolvingNeuralOrb(parent=self)
            lOrb.setMinimumSize(280, 280)
            lLayout.addWidget(lOrb)

        return lLayout  # type: ignore[return-value]

    @Layout.setter
    def Layout(self, value: QBoxLayout) -> None:
        # Delegate to WindowBase / ComponentBase setter behaviour
        lCentral = self.centralWidget()
        if lCentral is not None:
            lCentral.setLayout(value)
        else:
            self.setLayout(value)
        self._layout = value
