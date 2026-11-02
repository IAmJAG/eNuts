## Overview & Design Context

Package defaults and backbone helpers used by `PolicyOptions` and `DCPolicyCore`.

* **Design Decision / Deviation Notes:** Feature width is tied to the backbone class, not a free option.

---

## Classes

None.

---

## Functions

### `getFeatureDimension`
- **Arguments:** `module` (`nn.Module`) — MobileNet V3 or ResNet.
- **Returns:** `int` — `last_channel` or `fc.in_features`.
- **Behavior:** Raises on any other type.

### `buildBackbone`
- **Arguments:** `module` (`nn.Module`).
- **Returns:** `nn.Module` — features + pool + flatten, without the classifier.
- **Behavior:** MobileNet V3 uses `features` + `AdaptiveAvgPool2d(1)` + `Flatten`. ResNet uses conv/layers + `avgpool` + `Flatten`.

---

## Constants & Globals

### `G_DEFAULT_EMBEDDING_DIMENSION`
- **Type:** `int`
- **Value / Description:** `128`.

### `G_DEFAULT_FEATURE_DIMENSION`
- **Type:** `int`
- **Value / Description:** `576` (MobileNet V3 Small).

### `G_DEFAULT_FREEZE_BACKBONE`
- **Type:** `bool`
- **Value / Description:** `True`.

### `G_DEFAULT_SPATIAL_OUTPUT_DIMENSION`
- **Type:** `int`
- **Value / Description:** `4`.

### `G_DEFAULT_IMAGE_RESIZE`
- **Type:** `int`
- **Value / Description:** `224` (`frameSize`).

### `G_DEFAULT_STACK_SIZE`
- **Type:** `int`
- **Value / Description:** `4`.

### `G_NORMALIZE_MEAN` / `G_NORMALIZE_STD`
- **Type:** `List[float]`
- **Value / Description:** ImageNet mean and std.

## Sample Usage

```python
from torchvision.models import mobilenet_v3_small
from fluxCore.policy.__utilities import buildBackbone, getFeatureDimension

module = mobilenet_v3_small()
print(getFeatureDimension(module))
backbone = buildBackbone(module)
```
