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
# Tab indices inside KAndGRecorderTabs
C_TAB_STREAM = 0
C_TAB_CONFIGURATION = 1
# ==================================================================================


# ==================================================================================
class KAndGRecorderPage(Page):
    """Key & Gesture Recorder page.

    Page layout contract (jAGQt.widgets.Page):

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

    CommandBar uses jAGQt CommandBar.AddButton (see
    src/jAGQt/widgets/workspace/__commandBar.py).
    Content is assigned via Page.Content.
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
        """Page-level CommandBar via the real jAGQt API."""
        lBar = CommandBar(parent=self)

        self._startBtn = QPushButton("Start Recording")
        self._startBtn.setObjectName("StartRecordingBtn")
        self._startBtn.clicked.connect(self._onStartRecording)

        self._stopBtn = QPushButton("Stop Recording")
        self._stopBtn.setObjectName("StopRecordingBtn")
        self._stopBtn.clicked.connect(self._onStopRecording)
        self._stopBtn.setEnabled(False)

        lBar.AddStretch()
        lBar.AddButton(self._startBtn)
        lBar.AddButton(self._stopBtn)

        self.CommandBar = lBar

    # ==================================================================================
    def _buildUI(self) -> None:
        self._tabs = QTabWidget()
        self._tabs.setObjectName("KAndGRecorderTabs")

        self._streamTab = self._buildStreamTab()
        self._configTab = self._buildConfigTab()

        self._tabs.addTab(self._streamTab, "Stream")
        self._tabs.addTab(self._configTab, "Configuration")

        # Page.Content places the body between Header and CommandBar
        self.Content = self._tabs

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
        self._streamPlaceholder.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
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

        self._deviceCombo = QComboBox(lPanel)
        self._deviceCombo.setObjectName("DeviceCombo")
        self._deviceCombo.setMinimumWidth(280)
        lForm.addRow("Device", self._deviceCombo)

        self._maxSizeSpin = QSpinBox(lPanel)
        self._maxSizeSpin.setObjectName("MaxSizeSpin")
        self._maxSizeSpin.setRange(320, 4096)
        self._maxSizeSpin.setSingleStep(160)
        self._maxSizeSpin.setValue(self._maxSize)
        self._maxSizeSpin.valueChanged.connect(self._onMaxSizeChanged)
        lForm.addRow("Max Size", self._maxSizeSpin)

        self._fpsSpin = QSpinBox(lPanel)
        self._fpsSpin.setObjectName("FpsSpin")
        self._fpsSpin.setRange(1, 120)
        self._fpsSpin.setValue(self._fps)
        self._fpsSpin.valueChanged.connect(self._onFpsChanged)
        lForm.addRow("FPS", self._fpsSpin)

        self._bitrateSpin = QSpinBox(lPanel)
        self._bitrateSpin.setObjectName("BitrateSpin")
        self._bitrateSpin.setRange(100_000, 50_000_000)
        self._bitrateSpin.setSingleStep(100_000)
        self._bitrateSpin.setValue(self._bitrate)
        self._bitrateSpin.valueChanged.connect(self._onBitrateChanged)
        lForm.addRow("Bitrate", self._bitrateSpin)

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
    # Recording control
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
        """Apply UI state for IDLE / RECORDING / STOPPING."""
        self._state = state

        lIsIdle = state is eRecorderState.IDLE
        lIsRecording = state is eRecorderState.RECORDING
        lIsStopping = state is eRecorderState.STOPPING
        lConfigLocked = lIsRecording or lIsStopping

        self._tabs.setTabEnabled(C_TAB_CONFIGURATION, not lConfigLocked)

        self._deviceCombo.setEnabled(not lConfigLocked)
        self._maxSizeSpin.setEnabled(not lConfigLocked)
        self._fpsSpin.setEnabled(not lConfigLocked)
        self._bitrateSpin.setEnabled(not lConfigLocked)
        self._outputEdit.setEnabled(not lConfigLocked)
        self._browseBtn.setEnabled(not lConfigLocked)

        self._startBtn.setEnabled(lIsIdle)
        self._stopBtn.setEnabled(lIsRecording)

        if lIsRecording:
            self._tabs.setCurrentIndex(C_TAB_STREAM)
            self._streamPlaceholder.setFocus(Qt.FocusReason.OtherFocusReason)

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
