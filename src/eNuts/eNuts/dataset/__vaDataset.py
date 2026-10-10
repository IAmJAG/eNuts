# ==================================================================================
from __future__ import annotations

# ==================================================================================
import hashlib
import json

# ==================================================================================
from pathlib import Path
from typing import Any

# ==================================================================================
import av
import torch

# ==================================================================================
from torch import Tensor
from torch.utils.data import Dataset
from torchvision.models import MobileNet_V3_Small_Weights


# ==================================================================================
class VADataset(Dataset):
    """
    Stateful video action dataset featuring visual sequence uniqueness validation,
    dynamic retry-based window jittering, and runtime output caching.
    """

    def __init__(
        self, videoPath: str | Path, actionLogPath: str | Path,
        intentRegistry: Any, actionRegistry: Any, parameterRegistry: Any,
        sequenceLength: int = 16, frameStride: int = 1, maxRetries: int = 5,
    ) -> None:
        self._videoPath = Path(videoPath)
        self._intentRegistry = intentRegistry
        self._actionRegistry = actionRegistry
        self._parameterRegistry = parameterRegistry
        self._sequenceLength = sequenceLength
        self._frameStride = max(1, frameStride)
        self._maxRetries = maxRetries

        # Instant startup: load raw JSONL records
        self._records: list[dict[str, Any]] = []
        with open(actionLogPath, "r", encoding="utf-8") as lFile:
            for lLine in lFile:
                if lLine.strip():
                    self._records.append(json.loads(lLine))

        # Runtime cache tracking unique visual frame sequence hashes
        self._outputCache: set[str] = set()

        # Image preprocessing transform matching MobileNetV3-Small requirements
        self._transform = MobileNet_V3_Small_Weights.DEFAULT.transforms()

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> dict[str, Tensor] | None:
        lRecord = self._records[index]
        lTargetPts = lRecord["pts"]
        lIntentIndex = lRecord["intentIndex"]
        lActionIndex = lRecord["actionIndex"]
        lParameterIndex = lRecord["parameterIndex"]

        if index > 0:
            lPrevRecord = self._records[index - 1]
            lPrevActionIndex = lPrevRecord["actionIndex"]
            lPrevParameterIndex = lPrevRecord["parameterIndex"]
        else:
            lPrevActionIndex = self._actionRegistry.getIndex("<START>")
            lPrevParameterIndex = self._parameterRegistry.getIndex("<START>")

        # Attempt to extract a non-duplicate frame sequence via dynamic retries
        lFrames: Tensor | None = None
        for lAttempt in range(self._maxRetries):
            lCandidateFrames = self._extractFrameWindow(
                lTargetPts, index, attempt=lAttempt
            )

            # Hash the raw tensor bytes of the frame sequence
            lFrameChecksum = hashlib.md5(
                lCandidateFrames.detach().cpu().numpy().tobytes()
            ).hexdigest()

            if lFrameChecksum not in self._outputCache:
                self._outputCache.add(lFrameChecksum)
                lFrames = lCandidateFrames
                break

        # If threshold is reached and all attempts produced duplicate frames, return None
        if lFrames is None:
            return None

        # Resolve indices to embeddings via tripartite registries
        lIntentObj = self._intentRegistry.getByIndex(lIntentIndex)
        lTargetActionObj = self._actionRegistry.getByIndex(lActionIndex)
        lPrevActionObj = self._actionRegistry.getByIndex(lPrevActionIndex)

        lTargetParameterObj = self._parameterRegistry.getByIndex(lParameterIndex)
        lPrevParameterObj = self._parameterRegistry.getByIndex(lPrevParameterIndex)

        return {
            "frameSequence": lFrames,  # [T, C, H, W]
            "intentEmbedding": lIntentObj.embedding,  # [D_intent]
            "previousActionEmbedding": lPrevActionObj.embedding,  # [D_action]
            "previousParameterEmbedding": lPrevParameterObj.embedding,  # [D_parameter]
            "targetActionEmbedding": lTargetActionObj.embedding,  # [D_action]
            "targetParameterEmbedding": lTargetParameterObj.embedding,  # [D_parameter]
            "targetActionIndex": torch.tensor(lActionIndex, dtype=torch.long),
            "targetParameterIndex": torch.tensor(lParameterIndex, dtype=torch.long),
        }

    def _extractFrameWindow(self, targetPts: int, seedIndex: int, attempt: int) -> Tensor:
        neededTotalFrames = self._sequenceLength * self._frameStride

        # Factor the retry attempt into the random seed to shift the pre/post ratio on each try
        g = torch.Generator()
        g.manual_seed(seedIndex + targetPts + (attempt * 997))
        preRatio = (
            float(torch.rand(1, generator=g).item()) * 0.3 + 0.6
        )  # Range: [0.6, 0.9]

        numPreFrames = int(self._sequenceLength * preRatio)
        numPostFrames = self._sequenceLength - numPreFrames

        preCount = numPreFrames * self._frameStride
        postCount = numPostFrames * self._frameStride

        rawFramesList: list[Tensor] = []

        with av.open(str(self._videoPath), mode="r") as lContainer:
            lStream = lContainer.streams.video[0]
            lContainer.seek(targetPts, stream=lStream)

            for lPacket in lContainer:
                if lPacket.stream != lStream:
                    continue

                for lFrame in lPacket.decode():
                    lRgbFrame = lFrame.to_rgb().to_ndarray()
                    lTensor = torch.tensor(lRgbFrame).permute(2, 0, 1).float() / 255.0
                    lTransformed = self._transform(lTensor)

                    rawFramesList.append(lTransformed)

                    if len(rawFramesList) >= (preCount + postCount):
                        break

                if len(rawFramesList) >= (preCount + postCount):
                    break

        while len(rawFramesList) < (preCount + postCount):
            if rawFramesList:
                rawFramesList.append(rawFramesList[-1].clone())
            else:
                rawFramesList.append(torch.zeros(3, 224, 224))

        selectedFrames = rawFramesList[: (preCount + postCount) : self._frameStride]

        while len(selectedFrames) < self._sequenceLength:
            if selectedFrames:
                selectedFrames.insert(0, selectedFrames[0].clone())
            else:
                selectedFrames.append(torch.zeros(3, 224, 224))
        selectedFrames = selectedFrames[: self._sequenceLength]

        return torch.stack(selectedFrames, dim=0)
