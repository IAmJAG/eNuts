# ==================================================================================
# Video Action Dataset
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

# ==================================================================================
import av
import torch
from torch import Tensor
from torch.utils.data import Dataset
from torchvision.models import MobileNet_V3_Small_Weights


# ==================================================================================
class VADataset(Dataset):
    def __init__(
        self,
        videoPath: str | Path,
        actionLogPath: str | Path,
        intentRegistry: Any,
        actionRegistry: Any,
        sequenceLength: int = 16,
    ) -> None:
        self._videoPath = Path(videoPath)
        self._intentRegistry = intentRegistry
        self._actionRegistry = actionRegistry
        self._sequenceLength = sequenceLength

        # Load JSONL action records
        self._records: list[dict[str, Any]] = []
        with open(actionLogPath, "r", encoding="utf-8") as lFile:
            for lLine in lFile:
                if lLine.strip():
                    self._records.append(json.loads(lLine))

        # Image preprocessing transform matching MobileNetV3-Small requirements[cite: 1]
        self._transform = MobileNet_V3_Small_Weights.DEFAULT.transforms()

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> dict[str, Tensor]:
        lRecord = self._records[index]
        lTargetPts = lRecord["pts"]
        lIntentIndex = lRecord["intentIndex"]
        lActionIndex = lRecord["actionIndex"]

        # Resolve previous action index (default to <START> index or previous record's action)
        if index > 0:
            lPrevActionIndex = self._records[index - 1]["actionIndex"]
        else:
            lPrevActionIndex = self._actionRegistry.getIndex("<START>")

        # Extract frame sequence ending at lTargetPts from the MP4 container
        lFrames = self._extractFrameWindow(lTargetPts)

        # Resolve raw integer indices to embeddings via registries
        lIntentObj = self._intentRegistry.getByIndex(lIntentIndex)
        lTargetActionObj = self._actionRegistry.getByIndex(lActionIndex)
        lPrevActionObj = self._actionRegistry.getByIndex(lPrevActionIndex)

        return {
            "frameSequence": lFrames,                               # [T, C, H, W]
            "intentEmbedding": lIntentObj.embedding,                # [D_intent]
            "previousActionEmbedding": lPrevActionObj.embedding,    # [D_action]
            "targetActionEmbedding": lTargetActionObj.embedding,    # [D_action]
            "targetActionIndex": torch.tensor(lActionIndex, dtype=torch.long),
        }

    def _extractFrameWindow(self, targetPts: int) -> Tensor:
        """
        Seeks through the MP4 container to extract up to sequenceLength frames
        ending at or immediately before targetPts.
        """
        lFramesList: list[Tensor] = []
        
        with av.open(str(self._videoPath), mode="r") as lContainer:
            lStream = lContainer.streams.video[0]
            lTimeBase = lStream.time_base

            # Seek container close to the target pts
            # Note: PyAV seek works best in time_base units or seconds
            lContainer.seek(targetPts, stream=lStream)

            for lPacket in lContainer:
                if lPacket.stream != lStream:
                    continue
                
                for lFrame in lPacket.decode():
                    # Convert decoded VideoFrame to RGB tensor and apply transform
                    lRgbFrame = lFrame.to_rgb().to_ndarray()
                    lTensor = torch.tensor(lRgbFrame).permute(2, 0, 1).float() / 255.0
                    lTransformed = self._transform(lTensor)
                    
                    lFramesList.append(lTransformed)

                    # Stop collecting once we reach our window length constraint
                    if len(lFramesList) >= self._sequenceLength:
                        break
                
                if len(lFramesList) >= self._sequenceLength:
                    break

        # Fallback padding if sequence is shorter than expected
        while len(lFramesList) < self._sequenceLength:
            if lFramesList:
                lFramesList.insert(0, lFramesList[0].clone())
            else:
                # Absolute fallback for empty container windows
                lFramesList.append(torch.zeros(3, 224, 224))

        return torch.stack(lFramesList, dim=0)  # Shape: [T, C, H, W]