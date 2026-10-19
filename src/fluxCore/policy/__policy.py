# ==================================================================================
from typing import Any

# ==================================================================================
import torch
import torch.nn as nn
from torch import Tensor

# ==================================================================================
from ..types.interface.policy import iPolicy

# ==================================================================================
C_ACTION_KEYS: tuple[str, ...] = ("down", "up", "move", "inject")
C_NUM_ACTIONS: int = len(C_ACTION_KEYS)

# CNN result (feature map) shape — not the input resolution
C_FEATURE_HEIGHT: int = 24
C_FEATURE_WIDTH: int = 24
C_FEATURE_CHANNELS: int = 3
C_FEATURE_DIM: int = C_FEATURE_HEIGHT * C_FEATURE_WIDTH * C_FEATURE_CHANNELS  # 1728


# ==================================================================================
class Policy(nn.Module, iPolicy):
    """Minimal policy: one image -> one discrete action key.

    The backbone produces a fixed 24x24x3 feature map (the CNN result).
    Input images may be any spatial size; they are only lightly normalized
    and then processed by the network which is responsible for reaching
    the 24x24x3 representation.
    """

    def __init__(self, device: str | torch.device = "cuda") -> None:
        super().__init__()

        if isinstance(device, str):
            if device.lower().startswith("cuda") and not torch.cuda.is_available():
                device = "cpu"
            self._device = torch.device(device)
        else:
            self._device = device

        # Backbone ends with a 24x24x3 feature map (AdaptiveAvgPool guarantees spatial size)
        self._backbone = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),  # /2
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),  # /4
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, C_FEATURE_CHANNELS, kernel_size=1, stride=1, padding=0),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((C_FEATURE_HEIGHT, C_FEATURE_WIDTH)),  # -> [B, 3, 24, 24]
        )

        self._head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(C_FEATURE_DIM, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, C_NUM_ACTIONS),
        )

        self.to(self._device)

    # ------------------------------------------------------------------
    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def actionKeys(self) -> tuple[str, ...]:
        return C_ACTION_KEYS

    # ------------------------------------------------------------------
    def _preprocess(self, image: Tensor) -> Tensor:
        """Accept [C,H,W] or [B,C,H,W]; return float32 batch on model device.

        Does **not** force a fixed spatial size — the backbone is responsible
        for producing the 24x24x3 CNN result.
        """
        if image.dim() == 3:
            image = image.unsqueeze(0)
        if image.dim() != 4:
            raise ValueError("image must have shape [C,H,W] or [B,C,H,W]")

        image = image.to(device=self._device, dtype=torch.float32)

        if image.shape[1] == 1:
            image = image.repeat(1, 3, 1, 1)
        elif image.shape[1] != 3:
            raise ValueError("Expected 1 or 3 channel image")

        # Simple [0, 1] scale when values look like 0-255
        if image.max() > 1.5:
            image = image / 255.0

        return image

    def extractFeatures(self, image: Tensor) -> Tensor:
        """Return the CNN result feature map of shape [B, 3, 24, 24]."""
        x = self._preprocess(image)
        return self._backbone(x)

    def forward(self, image: Tensor) -> Tensor:
        """Return raw logits of shape [B, num_actions]."""
        features = self.extractFeatures(image)  # [B, 3, 24, 24]
        logits = self._head(features)
        return logits

    @torch.no_grad()
    def predict(self, image: Tensor) -> str:
        """Return the action key with highest logit."""
        wasTraining = self.training
        try:
            self.eval()
            logits = self.forward(image)
            index = int(torch.argmax(logits[0]).item())
            return C_ACTION_KEYS[index]
        finally:
            if wasTraining:
                self.train()

    def reset(self) -> None:
        """No internal state in the minimal policy; provided for interface stability."""
        pass
