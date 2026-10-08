# SemanticPredictorPolicy

## Overview

`SemanticPredictorPolicy` is a stateful, embedding-based policy network for sequential UI automation, device control, and visual decision-making.

It receives visual observations over time, combines them with the current intent and previous action, and predicts the semantic embedding of the next action.

Unlike a conventional classifier with a fixed output layer, the policy compares its predicted embedding against an external `ActionRegistry`. This allows the set of available actions to change without changing the network architecture, although newly introduced actions may require additional training.

### Policy inputs

The policy considers three sources of information:

1. **Visual state** — a rolling sequence of recently observed frames.
2. **Current intent** — the goal the policy is trying to accomplish.
3. **Previous action** — the action executed immediately before the current decision.

The output is an embedding representing the predicted next action.

Conceptually:

    Visual History + Current Intent + Previous Action
                            |
                            v
                    Visual Encoder
                            |
                            v
                    Feature Fusion
                            |
                            v
                       LSTM
                            |
                            v
                 Action Projection Head
                            |
                            v
                Predicted Action Embedding
                            |
                            v
                     Action Registry
                            |
                            v
                     Next Action

## Architecture

### Visual encoder

The visual encoder uses pretrained MobileNetV3-Small to extract features from each incoming frame.

The extracted features pass through a trainable projection layer to produce vectors of `FEATURE_DIM`.

The pretrained MobileNet backbone can be frozen to reduce training cost while allowing the projection and policy layers to learn.

### Stateful visual history

The policy maintains a rolling buffer of encoded frames internally.

The caller adds one frame at a time:

    policy.addFrame(frame)

The policy retains at most `MAX_SEQUENCE_LENGTH` frame features. When the buffer is full, the oldest feature is automatically discarded.

This avoids requiring the caller to reconstruct and resend the entire visual sequence for every prediction.

The buffer is runtime state and is not included in model checkpoints.

### Intent embedding

The intent describes the goal of the current task.

Examples:

- `open_settings`
- `enable_wifi`
- `install_application`
- `return_to_home`

The `IntentRegistry` resolves an intent identifier to its embedding and associated metadata.

Only the current intent embedding is passed into the policy. The complete intent registry is not a network input.

### Previous-action embedding

The previous action represents the most recent action executed by the automation system.

Examples:

- `tap_settings_icon`
- `tap_wifi_toggle`
- `press_back`
- `swipe_down`

The `ActionRegistry` resolves the previous action identifier to its embedding.

At the beginning of a new task, use a dedicated `<START>` action embedding to indicate that no ordinary action has yet been executed.

### Action projection and resolution

The projection head maps the LSTM output to `ACTION_EMBEDDING_DIM`.

The resulting vector is normalized and compared against the embeddings of registered actions using cosine similarity.

The action with the highest score is the top-ranked candidate:

    predictedEmbedding = policy(intentEmbedding, previousActionEmbedding)

    scores = policy.actionScores(
        predictedEmbedding,
        actionRegistryEmbeddings,
    )

    actionIndex = scores.argmax(dim=-1)

The selected registry entry is then passed to the appropriate action executor.

The policy predicts an action representation, not necessarily its complete execution parameters. For example, a `tap` action may require a separate parameter-prediction component to determine the target coordinates.

## Configuration

The constructor accepts an optional dictionary that overrides the default configuration.

| Option | Default | Description |
|---|---:|---|
| `FEATURE_DIM` | 512 | Dimension of each encoded frame |
| `INTENT_EMBEDDING_DIM` | 128 | Dimension of intent vectors |
| `ACTION_EMBEDDING_DIM` | 128 | Dimension of action vectors |
| `HIDDEN_DIM` | 256 | LSTM hidden-state dimension |
| `LAYERS` | 2 | Number of LSTM layers |
| `DROPOUT` | 0.2 | LSTM dropout when multiple layers are used |
| `INTERMEDIATE_HIDDEN_LAYER` | 256 | Hidden dimension of the action projection head |
| `TEMPERATURE` | 0.07 | Temperature used to scale similarity scores |
| `MAX_SEQUENCE_LENGTH` | 16 | Maximum number of retained frame features |
| `FREEZE_BACKBONE` | `True` | Whether to freeze pretrained MobileNet parameters |

Example:

    model = SemanticPredictorPolicy(
        options={
            "FEATURE_DIM": 512,
            "INTENT_EMBEDDING_DIM": 128,
            "ACTION_EMBEDDING_DIM": 128,
            "MAX_SEQUENCE_LENGTH": 16,
            "FREEZE_BACKBONE": True,
        }
    )

The intent and action embedding dimensions may be configured independently. The dimensions supplied by the registries must match the corresponding configuration.

## Public API

### `__init__(options=None)`

Initializes the visual encoder, feature projection, LSTM, action projection head, and runtime frame buffer.

### `addFrame(frame)`

Encodes and appends one frame to the current visual history.

Accepted input shapes:

- `[C, H, W]`
- `[1, C, H, W]`

Only one frame is accepted per call.

This method is intended for inference and requires the model to be in evaluation mode.

### `reset()`

Clears the retained frame history.

Call this when starting a new episode, situation, or independent visual sequence.

The caller should also reset its previous-action context to `<START>` when appropriate.

### `frameCount`

Returns the number of frame features currently retained.

### `getFrameFeatures()`

Returns the encoded frame history as a tensor with shape:

    [1, T, FEATURE_DIM]

Raises an error if the buffer is empty.

### `forward(intentEmbedding, previousActionEmbedding)`

Predicts the next action embedding from the internally accumulated visual history.

Input shapes:

- `intentEmbedding`: `[D_intent]` or `[B, D_intent]`
- `previousActionEmbedding`: `[D_action]` or `[B, D_action]`

Output shape:

    [B, ACTION_EMBEDDING_DIM]

At least one frame must have been added before calling this method.

### `forwardSequence(frameSequence, intentEmbedding, previousActionEmbedding)`

Provides the training interface for explicit image sequences.

Accepted frame-sequence shapes:

- `[T, C, H, W]`
- `[B, T, C, H, W]`

Returns the predicted next-action embedding.

Use this method for training from videos, annotated image sequences, or replay-buffer samples.

### `actionScores(predictedActionEmbedding, actionRegistryEmbeddings)`

Computes temperature-scaled cosine similarity between predicted embeddings and registered action embeddings.

Input shapes:

- Predicted embeddings: `[B, D_action]`
- Registry embeddings: `[N, D_action]`

Output shape:

    [B, N]

Higher scores indicate better embedding matches. Scores are relative similarities, not calibrated probabilities.

### `predictAction(intentEmbedding, previousActionEmbedding, actionRegistryEmbeddings)`

Runs inference using the accumulated frame history and calculates scores for all registered actions.

Returns:

    predictedEmbedding, scores

The caller resolves the best score to an action registry entry.

### `embeddingLoss(predictedEmbedding, targetActionEmbedding)`

Computes cosine-distance loss between predicted and target action embeddings.

Use this loss when the training sample identifies the target action embedding.

### `registryLoss(predictedEmbedding, actionRegistryEmbeddings, targetActionIndex)`

Computes cross-entropy loss over registered action candidates.

Use this when each training sample has a known target action index and the registry embeddings are consistent with the training targets.

If a situation has multiple valid next actions, a single-target cross-entropy objective may be inappropriate. Consider a multi-positive or ranking-based objective instead.

### `saveCheckpoint(path, optimizer=None, epoch=None, step=None, extra=None)`

Saves model weights, configuration, and optional training metadata.

The optimizer state is included when an optimizer is provided.

Runtime frame history is not saved.

### `loadCheckpoint(path, device="cpu", optimizer=None)`

Loads a saved model checkpoint.

Returns:

    model, checkpoint

If an optimizer is supplied and the checkpoint contains optimizer state, that state is restored.

Only load checkpoints from trusted sources because the checkpoint loader uses Python's serialized object format.

## Usage example: Live inference

This example assumes that `intentRegistry` and `actionRegistry` are application-level components providing embeddings and action lookup methods.

    import torch

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model, checkpoint = SemanticPredictorPolicy.loadCheckpoint(
        "semantic_policy.pt",
        device=device,
    )

    model.eval()
    model.reset()

    intent = intentRegistry.get("open_settings")
    previousAction = actionRegistry.get("<START>")

    actionEmbeddings = actionRegistry.getEmbeddings().to(device)

    while running:
        # Capture the newest screen image.
        frame = captureCurrentFrame()

        # Add only the newest frame.
        # The model maintains the visual history internally.
        model.addFrame(frame.to(device))

        # Predict the next action from the accumulated history.
        predictedEmbedding, scores = model.predictAction(
            intent.embedding,
            previousAction.embedding,
            actionEmbeddings,
        )

        # Resolve the highest-scoring candidate.
        actionIndex = scores[0].argmax().item()
        nextAction = actionRegistry.getByIndex(actionIndex)

        # Execute the selected action.
        execute(nextAction)

        # Update the action context for the next decision.
        previousAction = nextAction

The example deliberately does not call `reset()` after each prediction. Doing so would discard the visual history.

The application should decide when an intent is completed, interrupted, or replaced. That lifecycle determines when to clear the visual history and reset the previous-action context.

## Usage example: Training

Training uses explicit sequences so the model can learn from recorded experiences without relying on its live runtime buffer.

Each training sample should contain:

- `frameSequence`
- `intentEmbedding`
- `previousActionEmbedding`
- `targetActionEmbedding`
- Optionally, `targetActionIndex`

Example:

    import torch
    from torch import nn

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model = SemanticPredictorPolicy().to(device)

    optimizer = torch.optim.AdamW(
        [
            parameter
            for parameter in model.parameters()
            if parameter.requires_grad
        ],
        lr=1e-4,
        weight_decay=1e-4,
    )

    model.train()

    for sample in trainingData:
        frames = sample["frameSequence"].to(device)
        intent = sample["intentEmbedding"].to(device)
        previousAction = sample["previousActionEmbedding"].to(device)
        targetEmbedding = sample["targetActionEmbedding"].to(device)

        predictedEmbedding = model.forwardSequence(
            frames,
            intent,
            previousAction,
        )

        loss = model.embeddingLoss(
            predictedEmbedding,
            targetEmbedding,
        )

        if "targetActionIndex" in sample:
            actionEmbeddings = actionRegistry.getEmbeddings().to(device)

            loss = loss + 0.5 * model.registryLoss(
                predictedEmbedding,
                actionEmbeddings,
                sample["targetActionIndex"].to(device),
            )

        optimizer.zero_grad()
        loss.backward()

        nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=1.0,
        )

        optimizer.step()

The target action embedding and target registry index must refer to the same intended action. For a changing registry, make sure that training labels and registry indices are resolved against the correct registry version.

## Saving and loading checkpoints

Save the model after training:

    model.saveCheckpoint(
        "semantic_policy.pt",
        optimizer=optimizer,
        epoch=epoch,
        step=step,
    )

Load it later:

    model, checkpoint = SemanticPredictorPolicy.loadCheckpoint(
        "semantic_policy.pt",
        device=device,
    )

    model.eval()

Checkpoints store the trained model parameters and options, not the active task or current visual history. After loading, call `reset()` before starting a new interaction.

For reproducible inference, also version the intent/action embedding model and registry definitions in checkpoint metadata. A change to the embedding-generation method can make previously trained policy outputs incompatible with the current registries.

## Image preprocessing

MobileNetV3-Small pretrained weights expect image preprocessing consistent with their associated torchvision weights.

Use the corresponding transform pipeline for RGB images, including the expected resizing, scaling, and normalization.

The frame tensor passed to `addFrame()` should already be preprocessed. Do not apply normalization twice.

For example, use the transform associated with:

    models.MobileNet_V3_Small_Weights.DEFAULT.transforms()

Adapt the pipeline to the capture and batching format used by the application.

## Training data sources

Different data sources can be converted into a common experience format.

### Annotated video

Extract frame sequences around decision points and annotate the intended next action.

### Live interaction and replay buffer

Record the visual history, active intent, previous action, and validated next action for each experience.

### Curated image sequences

Use a sequence of related screenshots to represent a situation, together with the intent, previous action, and target next action.

The common supervised training representation is:

    (
        frameSequence,
        intentEmbedding,
        previousActionEmbedding,
        targetActionEmbedding
    )

This provides a common input/output contract regardless of how the experience was collected.

## Design considerations

### Dynamic registries do not guarantee zero-shot behavior

A new action can be added to the registry without adding a new output neuron. However, the policy may not reliably select that action until it has learned how the action relates to visual states, intents, and previous actions.

### Action parameters are separate from action selection

The policy chooses a semantic action candidate. Actions requiring coordinates, text, duration, or other parameters need an executor or parameter-prediction mechanism.

### Frame history is bounded

Only the most recent `MAX_SEQUENCE_LENGTH` encoded frames are retained. This is a rolling window, not an unlimited history of every observation.

### The current implementation recomputes the LSTM

Each prediction runs the LSTM over the retained feature sequence. The visual encoder does not need to reprocess older frames, but the LSTM does recompute their temporal representations.

Incremental LSTM hidden-state updates could improve efficiency, but require careful handling of rolling-window eviction, intent changes, previous-action context, and training/inference consistency.

### Intent and previous action are repeated across the window

The current implementation supplies the current intent and previous-action embeddings at every timestep in the retained sequence. It does not preserve the historical intent or historical action associated with each individual frame.

This is a deliberate simplification. If the task requires modeling historical actions or changing intents within a sequence, the training representation and temporal model should be extended accordingly.

## Summary

`SemanticPredictorPolicy` is a stateful, visual, semantic policy network.

- Add new observations using `addFrame()`.
- Clear visual history using `reset()`.
- Predict the next action using the current intent and previous action.
- Resolve the predicted embedding through the Action Registry.
- Train using explicit frame sequences and target action embeddings.
- Save and restore model weights with checkpoint methods.

The intended separation is that the **policy learns how to choose an action**, while the **registries define the available intents and actions and resolve their semantic representations**.