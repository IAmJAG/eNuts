# Hybrid Discrete–Continuous Policy — Implementation Document

**Status:** Initial implementation specification  
**Source of truth:** The Revised Policy Design and Policy Term Store. This document translates their agreed decisions into implementation guidance. It does not supersede them.

**Document structure** (planned sections):

1. Architecture and component responsibilities *(this section)*
2. Class and module design
3. Public APIs and method contracts
4. Data structures and tensor contracts
5. L1 implementation
6. L2 implementation
7. Vocabulary and encoding implementation
8. Intent Hierarchy and action-specific Executors
9. Step orchestration and execution lifecycle
10. State management and reset behavior
11. Error handling and validation
12. Testing strategy
13. Deferred implementation decisions

---

# Section 1 — Architecture and Component Responsibilities

## 1.1 Purpose

This section establishes the implementation-level architecture of the eNuts Policy. It identifies the major components, their responsibilities, and the data flow between them.

The policy is organized around two cooperating layers:

- **L1 — History / Context Buffer**
- **L2 — Policy Core**

The policy's action execution is performed by action-specific **Executor** implementations. The complete interaction cycle is orchestrated by `step()`; `step()` is not assumed to be a method of L2 or of any other particular class.

The implementation will use the technology choices already agreed in the Revised Policy Design. This section references those choices but does not redefine them.

## 1.2 Architectural overview

```text
                    Current observation and context
                 (image, active intent, previously
                   executed action and parameters)
                                  |
                                  v
                 +--------------------------------+
                 | L1: History / Context Buffer   |
                 |                                |
                 | - Prepare image                |
                 | - Encode intent/action/params  |
                 | - Maintain circular history   |
                 | - Pad warm-up history          |
                 | - Materialize Layout 3 stacks  |
                 +--------------------------------+
                                  |
                                  | Layout 3:
                                  | intent_stack
                                  | image_stack
                                  | action_stack
                                  | parameter_stack
                                  v
                 +--------------------------------+
                 | L2: Policy Core                |
                 |                                |
                 | - Process temporal context     |
                 | - Apply optional recurrent     |
                 |   state                        |
                 | - Predict discrete action      |
                 | - Predict action parameters    |
                 +--------------------------------+
                                  |
                                  | Predicted action
                                  | and parameters
                                  v
                 +--------------------------------+
                 | Action-specific Executor       |
                 |                                |
                 | - Accept action and parameters |
                 | - Carry out the action         |
                 | - Apply action-specific effects|
                 +--------------------------------+
                                  |
                                  v
                        Environment / caller
                                  |
                                  | Next observation
                                  | with the executed
                                  | action and parameters
                                  +---------------------> next step
```

`step()` coordinates the interaction cycle represented by this flow: it accepts the current input, updates or obtains L1 history, calls L2's `forward()`, receives the predicted action and parameters, and invokes the Executor associated with the predicted action. The next observation starts the next step.

## 1.3 Component responsibilities

### 1.3.1 L1 — History / Context Buffer

**Primary responsibility:** Maintain observation-aligned history and provide L2 with the fixed-length tensor input defined by Layout 3.

L1 is always stateful. It owns the persistent circular buffer (the **buffer state**) and maintains it across accepted input steps, independently of L2's recurrent-state setting.

L1 is responsible for:

1. **Accepting the current step's inputs**
   - Current image.
   - Active intent.
   - Previously executed action accompanying the current observation, or its pad value.
   - Previously executed parameters accompanying the current observation, or their pad/empty representation.

2. **Preparing image data**
   - Applying the image transform pipeline required by the model.
   - Storing each prepared image in the buffer in its final-ready form.
   - Avoiding a second image-preparation pass when the history is materialized for L2.

3. **Encoding discrete and structured context**
   - Encoding intent and action data using the vocabulary representation.
   - Encoding structured parameters into the fixed-width representation required by `parameter_stack`.
   - Excluding descriptive vocabulary fields from computation.

4. **Maintaining circular history**
   - Keeping a history with capacity `stackSize`.
   - Adding each accepted slot.
   - Dropping the oldest slot when the buffer is full.
   - Padding missing warm-up slots with empty/zero tensors so the emitted history always has length `stackSize`.

5. **Producing the L1-to-L2 input**
   - Materializing the four Layout 3 tensor stacks.
   - Preserving the temporal alignment of each slot.

Each conceptual history slot contains:

```text
(intent_t, image_t_prepared, previous_action_t, previous_parameters_t)
```

The action and parameters in a slot are previously executed controls accompanying that slot's current observation. They are not the action predicted after observing that image, nor are they necessarily the controls that caused the image to be produced.

**L1 does not predict the next action and does not execute actions.**

### 1.3.2 L2 — Policy Core

**Primary responsibility:** Consume the Layout 3 history from L1 and predict the next action and its parameters.

L2 is responsible for:

1. **Receiving the Layout 3 input**
   - `intent_stack`
   - `image_stack`
   - `action_stack`
   - `parameter_stack`

2. **Processing historical context**
   - Using visual, intent, previously executed action, and previously executed parameter context.
   - Performing temporal processing over the supplied history within a forward pass.
   - Treating the active intent as the primary intent conditioning signal while retaining per-slot intent history.

3. **Managing optional recurrent state**
   - Supporting the agreed statefulness switch, Off by default.
   - Maintaining recurrent state across separate forward passes only when enabled.
   - Providing a `stateReset()` method for clearing its recurrent state.
   - Keeping recurrent state distinct from L1's buffer state.

4. **Producing the hybrid policy output**
   - Predicting the next discrete action.
   - Predicting the parameters associated with that action, including continuous-valued parameters where applicable.

L2's `forward()` performs model processing and prediction. It does not, by definition, orchestrate the complete interaction cycle or carry out the predicted action.

**L2 does not own L1's circular history and does not perform action execution.**

### 1.3.3 Action-specific Executors

**Primary responsibility:** Carry out a predicted action using that action's predicted parameters.

An Executor accepts an action and its parameters and performs the corresponding execution behavior. Each action may have its own Executor implementation.

Executor responsibilities are action-specific. The generic Executor concept does not imply that every Executor manages the Intent Hierarchy or controls L2 state.

The Executor associated with `intent_end` has the specifically agreed additional role of applying the relevant `pop`, `push`, or `replace` operation to the Intent Hierarchy. At root-intent completion or replacement boundaries, that Executor invokes L2's `stateReset()` method when L2 recurrent state is enabled.

**Executors do not replace L2 prediction:** they execute the action that L2 has already predicted.

### 1.3.4 Step orchestration

**Primary responsibility:** Coordinate one complete policy interaction cycle.

The `step()` operation:

1. Accepts the current observation and associated context.
2. Updates or obtains the required L1 history.
3. Calls L2's `forward()` method with the Layout 3 input.
4. Receives the predicted action and parameters.
5. Selects/invokes the Executor associated with that action and carries out execution.

The next observation begins the next step. The implementation location of `step()` remains open: it may be an independent function or belong to another orchestration component. This section does not assign it to the model class.

## 1.4 Component relationships and data contracts

### L1 to L2

The L1-to-L2 boundary is the agreed **Layout 3** tuple:

```python
(
    intent_stack,
    image_stack,
    action_stack,
    parameter_stack,
)
```

Each element is an already-stacked tensor with temporal length `stackSize`. L1 may maintain per-modality arrays internally; tensor-stack materialization occurs at the hand-off to L2.

The implementation must preserve these meanings:

- `intent_stack` is the temporal per-slot intent history.
- `image_stack` contains prepared images.
- `action_stack` contains previously executed actions accompanying the corresponding observations.
- `parameter_stack` contains the encoded previously executed parameters accompanying those actions and observations.

### L2 to Executor

L2 produces the predicted next action and its predicted parameters. The action determines the associated Executor implementation. That Executor receives the action and parameters and carries out the action.

The concrete output data structure and Executor lookup/dispatch API are not specified in this section; they belong in the relevant API and component sections of this implementation document.

### Executor/environment to the next L1 input

After execution, the executed action and its parameters are supplied as the previous-control context accompanying the next observation. The caller or orchestration layer provides these values to L1 on the next step.

This feedback relationship does not change the temporal meaning of the L1 slot: the recorded controls have already been executed before the current observation is received.

## 1.5 State ownership

| State | Owner | Lifecycle |
|---|---|---|
| Buffer state / circular observation history | L1 — History / Context Buffer | Persistent across accepted input steps; always maintained |
| Recurrent state | L2 — Policy Core | Optional; Off by default; persists across forward passes only when enabled |
| Intent Hierarchy | Ownership is not assigned by the design; the `intent_end` Executor interacts with it | Updated according to `intent_end` action parameters |
| Training state | Training process/checkpoint | Maintained as required for training and resumable checkpoints |

The table identifies the agreed state concepts and their established ownership. It does not prescribe a concrete class or storage mechanism for the Intent Hierarchy or training state.

## 1.6 Agreed technology context

The implementation must use the technology decisions recorded in the Revised Policy Design:

| Area | Selected technology / policy | Architectural relevance |
|---|---|---|
| Programming language | Python | Implementation language for policy components and orchestration |
| Deep learning and tensor processing | PyTorch | L2 model, tensor operations, training, inference, and model state dictionaries |
| Image loading and PIL workflows | Pillow | Image loading and operations suited to PIL images |
| Computer vision and image processing | OpenCV | Image-processing operations suited to OpenCV |
| Array processing | NumPy | Numerical processing and `ndarray` workflows |
| Configuration and vocabulary storage | JSON | Human-readable policy configuration and vocabulary data |
| Execution device | CUDA by default, with explicit CPU fallback | Device selection must check CUDA availability and retain CPU support |
| Model persistence | PyTorch `state_dict`-based artifacts | Separate inference and resumable-training checkpoints, with configuration in JSON |

Pillow, OpenCV, NumPy, and PyTorch are complementary. The implementation may convert between PIL images, NumPy arrays, and PyTorch tensors at the appropriate processing boundaries.

This section does not select specific library versions, define image transform operations, set tensor dtypes or dimensions, or specify device-selection APIs. Those details are addressed in later implementation sections.

## 1.7 Explicitly unresolved in this section

The following details must not be inferred from this architecture section:

- Concrete Python class/module decomposition.
- Exact public method signatures and data classes.
- Exact tensor shapes, dimensions, and dtypes.
- Exact image transforms and normalization parameters.
- Exact embedding widths and model backbone dimensions.
- Exact JSON schemas and vocabulary validation rules.
- Concrete Intent Hierarchy storage and detailed `intent_end` execution semantics.
- Executor registration and dispatch mechanism.
- Exact `step()` implementation location.
- Device-selection API, multiple-CUDA-device handling, and override mechanism.
- Library versions and dependency pinning.

These topics are to be specified in the subsequent implementation sections or recorded as deferred decisions where appropriate.

---
