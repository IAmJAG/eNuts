# ==================================================================================
# src/eNuts/UI/widgets/pages/recorder/__recorderPage.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from enum import Enum, auto
from typing import TYPE_CHECKING

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# ==================================================================================
from jAGQt.widgets import CommandBar, Page

# ==================================================================================
if TYPE_CHECKING:
    from ....types.interface.application import iShell
    from fluxCore.types.interface.device import iDevice


# ==================================================================================
class eRecorderState(Enum):
    IDLE = auto()
    RECORDING = auto()
    STOPPING = auto()


# ==================================================================================
class KAndGRecorderPage(Page):
    """Key & Gesture Recorder page.

    Page layout contract:

        Page
        ├── Header
        │   ├── Title: K&G Recorder
        │   └── Description
        ├── Content
        │   └── Tabs
        │       ├── Stream
        │       └── Configuration   (settings only)
        └── CommandBar              (page-level — not part of Header)
            ├── Start Recording
            └── Stop Recording

    Do not install a competing root layout on the Page itself.
    CommandBar is assigned via Page.CommandBar; it is not placed in the header.
    All visual chrome is left to the application QSS via object names.
    """

    def __init__(self, shell: iShell | None = None, parent=None) -> None:
        super().__init__(
            title="K&G Recorder",
            description="Key & Gesture Recorder — live scrcpy stream with action capture",
            parent=parent,
        )
        self.setObjectName("KAndGRecorderPage")

        self._shell: iShell | None = shell
        self._state: eRecorderState = eRecorderState.IDLE

        # Local configuration (lives for the lifetime of the page)
        self._maxSize: int = 1920
        self._fps: int = 30
        self._bitrate: int = 4_000_000
        self._outputPath: str = ""

        self._buildCommandBar()
        self._buildUI()
        self.RefreshDevices()

    # ==================================================================================
    def _buildCommandBar(self) -> None:
        """Recording lifecycle controls live on the page-level CommandBar."""
        lBar = CommandBar(parent=self)
        self.CommandBar = lBar

        self._startBtn = QPushButton("Start Recording", lBar)
        self._startBtn.setObjectName("StartRecordingBtn")
        self._startBtn.clicked.connect(self._onStartRecording)

        self._stopBtn = QPushButton("Stop Recording", lBar)
        self._stopBtn.setObjectName("StopRecordingBtn")
        self._stopBtn.clicked.connect(self._onStopRecording)
        self._stopBtn.setEnabled(False)

        self._attachToCommandBar(lBar, self._startBtn)
        self._attachToCommandBar(lBar, self._stopBtn)

    def _attachToCommandBar(self, bar: CommandBar, widget: QWidget) -> None:
        """Attach a control using the CommandBar API surface available on base."""
        if hasattr(bar, "Add") and callable(getattr(bar, "Add")):
            bar.Add(widget)
            return
        if hasattr(bar, "AddWidget") and callable(getattr(bar, "AddWidget")):
            bar.AddWidget(widget)
            return
        if hasattr(bar, "addWidget") and callable(getattr(bar, "addWidget")):
            bar.addWidget(widget)
            return

        lLayout = bar.layout()
        if lLayout is not None:
            lLayout.addWidget(widget)

    # ==================================================================================
    def _contentHost(self) -> QWidget:
        """Return the container Page exposes for body content.

        Prefer Page.Content. Never replace the Page root layout that owns the header.
        """
        lContent = getattr(self, "Content", None)
        if isinstance(lContent, QWidget):
            return lContent
        return self

    def _attachToContent(self, widget: QWidget) -> None:
        """Place recorder body into the Page content area without fighting the header."""
        lHost = self._contentHost()

        # If Page exposes an explicit content layout, use it.
        lContentLayout = getattr(self, "ContentLayout", None)
        if lContentLayout is not None:
            lContentLayout.addWidget(widget, 1)
            return

        # Otherwise attach under Content (or, as last resort, the existing page layout).
        if lHost is not self:
            lLayout = lHost.layout()
            if lLayout is None:
                lLayout = QVBoxLayout(lHost)
                lLayout.setContentsMargins(0, 0, 0, 0)
                lLayout.setSpacing(0)
            lLayout.addWidget(widget, 1)
            return

        lPageLayout = self.layout()
        if lPageLayout is not None:
            lPageLayout.addWidget(widget, 1)
            return

        # Page has no layout and no Content — should not happen under the Page contract.
        lEmergency = QVBoxLayout(self)
        lEmergency.setContentsMargins(0, 0, 0, 0)
        lEmergency.addWidget(widget, 1)

    def _buildUI(self) -> None:
        self._tabs = QTabWidget()
        self._tabs.setObjectName("KAndGRecorderTabs")

        self._streamTab = self._buildStreamTab()
        self._configTab = self._buildConfigTab()

        self._tabs.addTab(self._streamTab, "Stream")
        self._tabs.addTab(self._configTab, "Configuration")

        self._attachToContent(self._tabs)

    def _buildStreamTab(self) -> QWidget:
        lTab = QWidget()
        lTab.setObjectName("RecorderStreamTab")

        lLayout = QVBoxLayout(lTab)
        lLayout.setContentsMargins(0, 0, 0, 0)
        lLayout.setSpacing(0)

        self._streamPlaceholder = QLabel(
            "Stream surface (RecorderImage) will appear here in Phase 3.",
            lTab,
        )
        self._streamPlaceholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._streamPlaceholder.setObjectName("StreamPlaceholder")
        lLayout.addWidget(self._streamPlaceholder, 1)

        return lTab

    def _buildConfigTab(self) -> QWidget:
        """Configuration holds settings only — no Start/Stop lifecycle controls."""
        lTab = QWidget()
        lTab.setObjectName("RecorderConfigTab")

        lOuter = QVBoxLayout(lTab)
        lOuter.setContentsMargins(0, 0, 0, 0)
        lOuter.setSpacing(0)

        lPanel = QGroupBox("Recorder Configuration", lTab)
        lPanel.setObjectName("RecorderConfigPanel")

        lPanelLayout = QVBoxLayout(lPanel)
        lPanelLayout.setContentsMargins(12, 16, 12, 12)
        lPanelLayout.setSpacing(12)

        lForm = QFormLayout()
        lForm.setObjectName("RecorderConfigForm")
        lForm.setSpacing(10)
        lForm.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Device
        self._deviceCombo = QComboBox(lPanel)
        self._deviceCombo.setObjectName("DeviceCombo")
        self._deviceCombo.setMinimumWidth(280)
        lForm.addRow("Device", self._deviceCombo)

        # Max Size
        self._maxSizeSpin = QSpinBox(lPanel)
        self._maxSizeSpin.setObjectName("MaxSizeSpin")
        self._maxSizeSpin.setRange(320, 4096)
        self._maxSizeSpin.setSingleStep(160)
        self._maxSizeSpin.setValue(self._maxSize)
        self._maxSizeSpin.valueChanged.connect(self._onMaxSizeChanged)
        lForm.addRow("Max Size", self._maxSizeSpin)

        # FPS
        self._fpsSpin = QSpinBox(lPanel)
        self._fpsSpin.setObjectName("FpsSpin")
        self._fpsSpin.setRange(1, 120)
        self._fpsSpin.setValue(self._fps)
        self._fpsSpin.valueChanged.connect(self._onFpsChanged)
        lForm.addRow("FPS", self._fpsSpin)

        # Bitrate
        self._bitrateSpin = QSpinBox(lPanel)
        self._bitrateSpin.setObjectName("BitrateSpin")
        self._bitrateSpin.setRange(100_000, 50_000_000)
        self._bitrateSpin.setSingleStep(100_000)
        self._bitrateSpin.setValue(self._bitrate)
        self._bitrateSpin.valueChanged.connect(self._onBitrateChanged)
        lForm.addRow("Bitrate", self._bitrateSpin)

        # Output path + Browse
        lOutputRow = QWidget(lPanel)
        lOutputRow.setObjectName("OutputRow")
        lOutputLayout = QHBoxLayout(lOutputRow)
        lOutputLayout.setContentsMargins(0, 0, 0, 0)
        lOutputLayout.setSpacing(8)

        self._outputEdit = QLineEdit(lOutputRow)
        self._outputEdit.setObjectName("OutputEdit")
        self._outputEdit.setPlaceholderText("/path/to/output/folder")
        self._outputEdit.setText(self._outputPath)
        self._outputEdit.textChanged.connect(self._onOutputChanged)

        self._browseBtn = QPushButton("Browse…", lOutputRow)
        self._browseBtn.setObjectName("BrowseOutputBtn")
        self._browseBtn.clicked.connect(self._onBrowseOutput)

        lOutputLayout.addWidget(self._outputEdit, 1)
        lOutputLayout.addWidget(self._browseBtn)
        lForm.addRow("Output", lOutputRow)

        lPanelLayout.addLayout(lForm)

        lOuter.addWidget(lPanel, 0, Qt.AlignmentFlag.AlignTop)
        lOuter.addStretch(1)
        return lTab

    # ==================================================================================
    # Configuration callbacks
    # ==================================================================================
    def _onMaxSizeChanged(self, value: int) -> None:
        self._maxSize = value

    def _onFpsChanged(self, value: int) -> None:
        self._fps = value

    def _onBitrateChanged(self, value: int) -> None:
        self._bitrate = value

    def _onOutputChanged(self, text: str) -> None:
        self._outputPath = text.strip()

    def _onBrowseOutput(self) -> None:
        lDir = QFileDialog.getExistingDirectory(
            self,
            "Select Recording Output Folder",
            self._outputPath or "",
        )
        if lDir:
            self._outputEdit.setText(lDir)
            self._outputPath = lDir

    # ==================================================================================
    # Device population (Shell.Devices only — no ADB discovery)
    # ==================================================================================
    def RefreshDevices(self) -> None:
        """Repopulate the device combo from Shell.Devices."""
        lCurrentId: str | None = None
        lData = self._deviceCombo.currentData()
        if lData is not None:
            lCurrentId = getattr(lData, "id", None)

        self._deviceCombo.blockSignals(True)
        self._deviceCombo.clear()

        if self._shell is None:
            self._deviceCombo.blockSignals(False)
            return

        lDevices = self._shell.Devices
        for lId, lDevice in lDevices.items():
            lLabel = lDevice.name or lId
            self._deviceCombo.addItem(lLabel, lDevice)

        # Restore previous selection if still present
        if lCurrentId is not None:
            for lIdx in range(self._deviceCombo.count()):
                lItem: iDevice | None = self._deviceCombo.itemData(lIdx)
                if lItem is not None and lItem.id == lCurrentId:
                    self._deviceCombo.setCurrentIndex(lIdx)
                    break

        self._deviceCombo.blockSignals(False)

    def SelectedDevice(self) -> iDevice | None:
        """Return the currently selected iDevice, or None."""
        return self._deviceCombo.currentData()

    # ==================================================================================
    # Recording control (stubs for Phase 5 lifecycle)
    # ==================================================================================
    def _onStartRecording(self) -> None:
        if self._state is not eRecorderState.IDLE:
            return
        # Validation and full start logic land in Phase 5
        self._setState(eRecorderState.RECORDING)

    def _onStopRecording(self) -> None:
        if self._state is not eRecorderState.RECORDING:
            return
        self._setState(eRecorderState.STOPPING)
        # Flush / finalize lands in Phase 5
        self._setState(eRecorderState.IDLE)

    def _setState(self, state: eRecorderState) -> None:
        self._state = state
        lRecording = state is eRecorderState.RECORDING

        # Lock stream-affecting configuration while recording
        self._deviceCombo.setEnabled(not lRecording)
        self._maxSizeSpin.setEnabled(not lRecording)
        self._fpsSpin.setEnabled(not lRecording)
        self._bitrateSpin.setEnabled(not lRecording)
        self._outputEdit.setEnabled(not lRecording)
        self._browseBtn.setEnabled(not lRecording)

        self._startBtn.setEnabled(not lRecording)
        self._stopBtn.setEnabled(lRecording)

    # ==================================================================================
    # Public config accessors (used by later phases)
    # ==================================================================================
    @property
    def MaxSize(self) -> int:
        return self._maxSize

    @property
    def Fps(self) -> int:
        return self._fps

    @property
    def Bitrate(self) -> int:
        return self._bitrate

    @property
    def OutputPath(self) -> str:
        return self._outputPath

    @property
    def State(self) -> eRecorderState:
        return self._state
