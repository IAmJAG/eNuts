> **ARCHIVED 2026-10-31 — REFERENCE ONLY**  
> This file is no longer the source of truth. Active documentation will be rewritten under `.docs/fluxCore/policy/`. See `.docs/_archive/fluxCore/policy/README.md`.

---

# Hybrid Discrete-Continuous Policy System Architecture

## 1. Executive Summary

This architecture implements a robust, stateful policy designed for complex UI and game automation workflows. It combines high-level **discrete action classification** against immutable semantic registries with **continuous parameter regression** for precise execution arguments. 

The design addresses three core automation challenges:
1. **Pipeline Latency & Scalability:** Avoids blocking initialization pre-scans by moving visual uniqueness validation and deduplication directly into runtime sampling.
2. **Static Screen & Loop Mitigation:** Prevents deterministic infinite loops on invariant UI states (such as configuration pages) by feeding historical action and parameter context directly into temporal sequence modeling.
3. **Anti-Cheat & Bot-Detection Resilience:** Combines temporal frame striding and bi-directional anchor jitter during training with stochastic multinomial sampling and execution micro-jitter during inference to avoid superhuman timing patterns.

---

## 2. System Data Flow & Architecture Diagram

```
+------------------+     +------------------------+     +-------------------+
|  Video Frames    |     |   Intent & Historical  |     |   Runtime         |
|  [B, T, C, H, W] |     |   Action/Param Context |     |   Visual Cache    |
+--------+---------+     +-----------+------------+     +---------+---------+
         |                           |                            |
         +-------------+-------------+                            |
                       |                                          v
                       v                                +-------------------+
           +-----------------------+                    | Frame Checksum    |
           |  MobileNetV3 + LSTM   |                    | & Retry Loop      |
           |  Sequence Model       |                    +-------------------+
           +-----------+-----------+
                       |
         +-------------+-------------+
         |                           |
         v                           v
+------------------+        +------------------+
| Discrete Action  |        | Continuous Param |
| Head (Cosine     |        | Head (Regression |
| Similarity)      |        | Output)          |
+------------------+        +------------------+
```

---

## 3. Implementation Details & Specifications

### A. Data Engineering (`VADataset` & Pipeline)

* **Instantaneous Initialization:**
  * Loads raw log files directly into memory without performing heavy video-seeking or upfront pre-processing loops.
  * Preserves rapid container startup and low memory footprints.

* **Temporal Horizon Management (`frameStride`):**
  * Applies configurable frame skipping to adjust the model's receptive window across variable video recording frame rates.
  * Normalizes rapid UI transitions into stable temporal feature vectors.

* **Bi-Directional Anchor Jitter:**
  * Randomly shifts the distribution of pre-anchor and post-anchor frames around the target timestamp (e.g., maintaining a dynamic split between 60% and 90% pre-frames).
  * Prevents the network from overfitting to rigid, fixed-step execution timing horizons.

* **Runtime Visual Sequence Deduplication:**
  * Generates cryptographic checksums (MD5) directly from the raw tensor bytes of sampled frame windows inside `__getitem__`.
  * Implements a dynamic retry loop (`maxRetries`) that alters generator seeds to adjust anchor offsets if duplicate frame sequences are encountered.
  * Returns `None` upon reaching retry thresholds, allowing the batch sampler (`customCollateFn`) to strip unviable entries safely without breaking index mapping.

---

### B. Hybrid Policy Network (`SemanticPredictorPolicy`)

* **Visual Backbone:**
  * Uses a pre-trained MobileNetV3-Small convolutional feature extractor coupled with adaptive spatial pooling.
  * Maps raw spatial pixel grids into dense 512-dimensional visual embedding vectors.

* **Temporal Context Fusion:**
  * Utilizes a Recurrent LSTM layer operating on concatenated visual feature vectors, `intentEmbedding`, `previousActionEmbedding`, and `previousParameter` state tensors.
  * Integrates historical context at every step to break spatial ambiguity when screens remain visually identical across sequential actions.

* **Dual Prediction Heads:**
  1. **Discrete Action Head:** Projects hidden states into a target embedding space and computes temperature-scaled cosine similarity against an immutable `ActionRegistry`. Optimized via Cross-Entropy Loss.
  2. **Continuous Parameter Head:** Regresses continuous outputs (e.g., spatial offset coordinates, duration values, or drag vectors) through a multi-layer perceptron (MLP). Optimized via Mean Squared Error (MSE) or Smooth L1 Loss.

---

### C. Anti-Cheat & Humanization Layer

* **Inference Sampling (Stochastic Execution):**
  * Replaces deterministic `argmax` selection with temperature-scaled categorical multinomial sampling during inference.
  * Introduces natural variance into high-probability action paths.

* **Execution Micro-Jitter:**
  * Downstream execution drivers apply Gaussian noise to spatial click/drag coordinates ($x \pm \delta_x, y \pm \delta_y$).
  * Wraps macro execution in randomized human reaction delays ($120\text{ms} \pm 30\text{ms}$) to break robotic clock-cycle predictability.
