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
C_INPUT_HEIGHT: int = 24
C_INPUT_WIDTH: int = 24
C_INPUT_CHANNELS: int = 3


# ==================================================================================
class Policy(nn.Module, iPolicy):
    """Minimal policy: one image -> one discrete action key."""

    def __init__(self, device: str | torch.device = "cuda") -> None:
        super().__init__()

        if isinstance(device, str):
            if device.lower().startswith("cuda") and not torch.cuda.is_available():
                device = "cpu"
            self._device = torch.device(device)
        else:
            self._device = device

        # Tiny CNN suitable for 24x24 input
        self._backbone = nn.Sequential(
            nn.Conv2d(C_INPUT_CHANNELS, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 12x12
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 6x6
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

        self._head = nn.Linear(64, C_NUM_ACTIONS)

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
        """Accept [C,H,W] or [B,C,H,W]; return float32 batch on model device at 24x24."""
        if image.dim() == 3:
            image = image.unsqueeze(0)
        if image.dim() != 4:
            raise ValueError("image must have shape [C,H,W] or [B,C,H,W]")

        image = image.to(device=self._device, dtype=torch.float32)

        # Ensure 3 channels
        if image.shape[1] == 1:
            image = image.repeat(1, 3, 1, 1)
        elif image.shape[1] != 3:
            raise ValueError("Expected 1 or 3 channel image")

        # Resize to internal shape if needed
        if image.shape[2] != C_INPUT_HEIGHT or image.shape[3] != C_INPUT_WIDTH:
            image = nn.functional.interpolate(
                image,
                size=(C_INPUT_HEIGHT, C_INPUT_WIDTH),
                mode="bilinear",
                align_corners=False,
            )

        # Simple [0, 1] clamp if values look like 0-255
        if image.max() > 1.5:
            image = image / 255.0

        return image

    def forward(self, image: Tensor) -> Tensor:
        """Return raw logits of shape [B, num_actions]."""
        x = self._preprocess(image)
        features = self._backbone(x)
        logits = self._head(features)
        return logits

    @torch.no_grad()
    def predict(self, image: Tensor) -> str:
        """Return the action key with highest logit."""
        wasTraining = self.training
        try:
            self.eval()
            logits = self.forward(image)
            # Use first item if batched
            index = int(torch.argmax(logits[0]).item())
            return C_ACTION_KEYS[index]
        finally:
            if wasTraining:
                self.train()

    def reset(self) -> None:
        """No internal state in the minimal policy; provided for interface stability."""
        pass
