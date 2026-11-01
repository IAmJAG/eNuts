# eNuts Policy Design — Term Store

This term store records terminology decisions agreed during review of the current revised policy design document. Entries are cumulative. A term is treated as settled only when explicitly agreed.

## Entry 1 — Observation-aligned previous controls

**Status:** Agreed.

**Canonical definition**

Previously executed controls accompanying the current observation.

**Meaning**

For a history slot at time `t`, the action and parameters are the controls that had already been executed before the current observation was received. They are stored alongside that current observation as context for the policy's present decision.

**Canonical slot representation**

```text
(intent_t, image_t_prepared, previous_action_t, previous_parameters_t)
```

**L1 input terms**

- `image` — current raw frame.
- `intent` — active intent.
- `previous_action` — previously executed action accompanying the current observation (or pad).
- `previous_parameters` — parameters accompanying that previously executed action and the current observation (or pad / empty).

**L1 → L2 tensor channel names**

The canonical Layout 3 channel names are:

```text
(intent_stack, image_stack, action_stack, parameter_stack)
```

`action_stack` and `parameter_stack` contain the encoded history of the previously executed controls represented by `previous_action_t` and `previous_parameters_t`.

**Clarification of the legacy phrase**

The phrase **“action taken from this image”** means the previously executed action recorded alongside the current image as action context. It does not mean:
- the action selected after observing that image; or
- the action that produced that image.

L2 consumes this previous-control context and predicts the **next** action and its parameters.

**Data-flow wording**

The L1 inputs and data-flow sketch should consistently describe the control inputs as **previously executed action** and **previously executed parameters**, and identify them as accompanying the current observation.

**Terminology rule**

Prefer **previously executed controls accompanying the current observation** when describing the combined action-and-parameter pair. Use `previous_action` and `previous_parameters` for the individual L1 inputs. Avoid using **“action taken from this image”** without the clarification above.


## Entry 2 — Parameter terminology and lifecycle

**Status:** Agreed.

**Canonical concept**

**Parameters** are the values associated with an action. The terms below identify those parameters at different stages of the action lifecycle; they do not represent different parameter types.

**Lifecycle terms**

- **Predicted parameters** — parameters produced by L2 for its predicted next action.
- **Action parameters** — parameters associated with an action and interpreted by the executor.
- **Previously executed parameters** — parameters accompanying an already executed action and the current observation in L1 history.

**Canonical tensor channel name**

`parameter_stack` is the Layout 3 channel containing the encoded history of previously executed parameters. Use the fully spelled-out name; do not use `param_stack`.

**Terminology rules**

- Use **predicted parameters** when describing L2's predicted output.
- Use **action parameters** when describing the parameters associated with an action or interpreted by the executor.
- Use **previously executed parameters** when describing the L1 history input and its observation-aligned contents.
- Do not use **arguments** as a substitute for **parameters** in the policy action/parameter lifecycle. This rule does not prohibit the ordinary programming term *argument* when referring to function or method arguments.


## Entry 3 — Intent terminology

**Status:** Agreed.

**Canonical terms**

- **Active intent** — the intent currently governing the policy's decision. Use this term instead of **current intent** for clarity.
- **Root intent** — the first intent pushed; the ultimate, overarching intent above the subsequent intents.
- **Intent history** — the historical sequence of intents associated with observations and decisions.

**Relationship between active intent and root intent**

The active intent may be the root intent or a subsequent intent. The design must explicitly identify whether the active intent is the root intent.

**History terminology**

- Each L1 history slot retains the intent that was active when that slot was written.
- `intent_stack` is the Layout 3 tensor channel containing the per-slot intent history.
- The active intent is the primary conditioning signal (the intent blanket) for the current policy decision.

**`intent_end` terminology**

- `intent_end` is a discrete action reference the policy may emit.
- `pop`, `push`, and `replace` are parameter options associated with the `intent_end` action; they are not separate actions.

**Terminology rules**

- Use **active intent** consistently; replace **current intent** when referring to the intent governing the present decision.
- Use **root intent** for the first, overarching intent.
- Use **intent history** for the historical sequence, and `intent_stack` when referring specifically to the L1 tensor channel.
- Use **Intent Hierarchy** for the hierarchical organization of the root intent and subsequent pushed intents. Do not call this hierarchy `intent_stack`.
- Reserve `intent_stack` for the temporal Layout 3 tensor channel: L1 produces it and L2 receives it.
- `intent_end` parameters (`pop`, `push`, `replace`) specify operations on the Intent Hierarchy.
- An Executor is an action-execution concept; each action may have its own Executor implementation. The Executor associated with `intent_end` may interact with the Intent Hierarchy and invoke L2 reset at root-intent boundaries. Do not generalize this responsibility to every Executor.


## Entry 4 — Buffer state and recurrent state

**Status:** Agreed.

**Canonical distinction**

- **Buffer state** — the persistent history maintained by L1's History / Context Buffer. It consists of the buffered per-modality entries and is supplied to L2 as the fixed-length Layout 3 stacks. L1 always maintains this state across accepted input steps.
- **Recurrent state** — optional internal state maintained by L2 across separate forward passes. It is controlled by L2's statefulness switch, which defaults to Off.
- **Within-pass temporal processing** — L2's processing of the history supplied by the current L1 stacks during a single forward pass. This is distinct from recurrent state and is allowed even when L2's statefulness switch is Off.

**Statefulness terminology**

- **Stateless L2** — L2 does not carry persistent recurrent state across calls. It may still use temporal operators over the L1 history within each forward pass.
- **Stateful L2** — L2 may carry internal recurrent state between forward passes, allowing context beyond the L1 history window.

**Ownership**

- L1 owns the buffer state and circular history bookkeeping.
- L2 owns its optional recurrent state.
- Buffer state and recurrent state are separate concepts with different owners and lifecycles.

**Reset terminology**

L2's reset method clears L2 recurrent state when recurrent state is enabled. When the L2 statefulness switch is Off, reset is a no-op because there is no persistent recurrent state to clear.

**Terminology rules**

- Use **buffer state** when referring to L1's persistent circular history.
- Use **recurrent state** when referring to L2's optional internal state across forward passes.
- Do not call L2 stateless merely because it processes a single history window; temporal processing within a forward pass is not recurrent state.
- Do not conflate L1 buffer state with L2 recurrent state.

## Entry 5 — Temporal `intent_stack`, Intent Hierarchy, and action-specific Executors

**Status:** Agreed.

**Canonical distinction**

- **`intent_stack`** — the temporal history tensor channel in Layout 3. L1 produces this channel from the per-slot intent history; L2 receives it as part of its input. The term refers to this L1-to-L2 temporal tensor, not to the hierarchical organization of pushed intents.
- **Intent Hierarchy** — the hierarchical organization formed by the root intent and subsequent pushed intents. The root intent is the first intent pushed and is the overarching intent. Subsequent intents are organized as steps or sub-intents under that root.

**Executor terminology**

- **Executor** is the general action-execution concept: it accepts an action and that action's parameters and carries out the action.
- Each action may have its own Executor implementation.
- The Executor implementation associated with `intent_end` may apply the action's `pop`, `push`, or `replace` parameter to the Intent Hierarchy.
- At root-intent completion or replacement boundaries, the `intent_end` Executor invokes L2's reset method when L2 recurrent state is enabled. This does not make Intent Hierarchy interaction or L2 reset a universal responsibility of every Executor.

**Terminology rules**

- Use `intent_stack` only for the temporal L1-produced / L2-received tensor channel and its per-slot history.
- Use **Intent Hierarchy** for the root-and-sub-intent organization. Do not call it an intent stack.
- Describe `pop`, `push`, and `replace` as parameter options of the `intent_end` action that specify operations on the Intent Hierarchy.
- Describe action execution in terms of the Executor implementation associated with the particular action.
- Do not attribute Intent Hierarchy ownership or management to a generic Executor; only the relevant action-specific implementation may interact with it.

## Entry 6 — Step, `forward()`, and execution

**Status:** Agreed.

**Canonical definitions**

- **Step** — one complete policy interaction cycle: accept the current observation and associated context; update or obtain the required L1 history; call the model's `forward()` method; receive the predicted action and its parameters; and execute that action through its associated Executor implementation. The next observation begins the next step.
- **`step()`** — the operation that accepts input, calls `forward()`, and executes the resulting action. It represents interaction-cycle orchestration and does not necessarily belong inside the model class; it may be an independent function or another orchestration component.
- **`forward()`** — the model method that processes supplied input and predicts/produces an action and its parameters. It does not, by itself, define the complete interaction cycle and does not necessarily execute the action.
- **Execution** — carrying out the predicted action through its associated Executor implementation.

**Terminology rules**

- Use **step** for the complete policy interaction cycle, not merely for a model forward pass or action execution.
- Use `step()` for the orchestration operation that accepts input, calls `forward()`, and executes the predicted action.
- Use `forward()` for model inference/prediction from supplied input; do not imply that it necessarily executes the action.
- Keep execution distinct from prediction: the associated Executor implementation carries out the predicted action.
- Do not assume that `step()` is a method of the model class. Its implementation location remains open to the surrounding orchestration design.
