## Overview

**Source of truth:** `DCPolicy` — `src/fluxCore/policy/__dcPolicy.py`

Canonical documentation (mirrors source tree):

- `.docs/fluxCore/policy/policy.md`
- `.docs/fluxCore/policy/requirement.md`
- `.docs/fluxCore/policy/implementation.md`

## Summary

Discrete–continuous policy: raw image → transform + carousel → action + argument.

```python
from fluxCore.policy import DCPolicy, PolicyOptions, Vocabulary

policy = DCPolicy(options, device="cuda")
action, argument = policy.predict(image)  # raw ndarray or Tensor
```
