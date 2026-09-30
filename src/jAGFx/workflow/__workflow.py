# ==================================================================================
# src/jAGFx/workflow/__workflow.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from functools import wraps
from typing import Callable, TypeVar, overload

# ==================================================================================
_T = TypeVar("_T", bound=type)
_WORKFLOW_PREFIX = "_w"
_WORKFLOW_METADATA = "__jagfx_workflow__"
_WORKFLOW_GUARD = "__jagfx_workflow_active__"
_WORKFLOW_INIT_WRAPPED = "__jagfx_workflow_init_wrapped__"
_WORKFLOW_SUBCLASS_WRAPPED = "__jagfx_workflow_subclass_wrapped__"

# ==================================================================================
def _workflow_method_name(name: str) -> str:
    if not name or name.startswith(_WORKFLOW_PREFIX):
        raise ValueError(f"Workflow name {name!r} must be a non-empty name without the {_WORKFLOW_PREFIX!r} prefix.")

    return f"{_WORKFLOW_PREFIX}{name}"

# ==================================================================================
def _discover_workflows(cls: type) -> tuple[str, ...]:
    """Discover workflow methods defined directly on ``cls``."""
    return tuple(
        name
        for name, value in cls.__dict__.items()
        if name.startswith(_WORKFLOW_PREFIX) and callable(value)
    )

# ==================================================================================
def _run_workflow(instance: object) -> None:
    names = getattr(type(instance), _WORKFLOW_METADATA, None)
    if names is None:
        return

    for name in names:
        method = getattr(instance, name, None)
        if not callable(method):
            raise AttributeError(
                f"Workflow method {name!r} was not found on {type(instance).__name__}."
            )
        method()

# ==================================================================================
def _wrap_init(cls: type, original_init: Callable) -> None:
    if getattr(original_init, _WORKFLOW_INIT_WRAPPED, False): return

    @wraps(original_init)
    def wrapped_init(self, *init_args, **init_kwargs):
        outermost = not getattr(self, _WORKFLOW_GUARD, False)
        if outermost: setattr(self, _WORKFLOW_GUARD, True)

        try:
            original_init(self, *init_args, **init_kwargs)

        except BaseException:
            if outermost: delattr(self, _WORKFLOW_GUARD)
            raise

        if outermost:
            try:
                _run_workflow(self)

            finally:
                delattr(self, _WORKFLOW_GUARD)

    setattr(wrapped_init, _WORKFLOW_INIT_WRAPPED, True)
    cls.__init__ = wrapped_init

# ==================================================================================
def _prepare_subclass(cls: type) -> None:
    """Install the workflow construction boundary on a new subclass."""

    original_init = cls.__dict__.get("__init__")

    if original_init is None:
        def generated_init(self, *init_args, **init_kwargs):
            super(cls, self).__init__(*init_args, **init_kwargs)

        _wrap_init(cls, generated_init)
    else:
        _wrap_init(cls, original_init)

    original_hook = cls.__dict__.get("__init_subclass__")
    if original_hook is None:
        return

    if isinstance(original_hook, classmethod):
        original_hook_function = original_hook.__func__
    else:
        original_hook_function = original_hook

    if getattr(original_hook_function, _WORKFLOW_SUBCLASS_WRAPPED, False):
        return

    @wraps(original_hook_function)
    def wrapped_hook(subclass, **kwargs):
        original_hook_function(subclass, **kwargs)
        _prepare_subclass(subclass)

    setattr(wrapped_hook, _WORKFLOW_SUBCLASS_WRAPPED, True)
    cls.__init_subclass__ = classmethod(wrapped_hook)

# ==================================================================================
def _install_subclass_hook(cls: type) -> None:
    """Install propagation for a workflow root that has no inherited hook."""

    original_hook = cls.__dict__.get("__init_subclass__")

    if original_hook is not None:
        if isinstance(original_hook, classmethod):
            original_hook_function = original_hook.__func__
        else:
            original_hook_function = original_hook

        if getattr(original_hook_function, _WORKFLOW_SUBCLASS_WRAPPED, False):
            return

        @wraps(original_hook_function)
        def wrapped_hook(subclass, **kwargs):
            original_hook_function(subclass, **kwargs)
            _prepare_subclass(subclass)
    else:
        @wraps(object.__init_subclass__)
        def wrapped_hook(subclass, **kwargs):
            super(cls, subclass).__init_subclass__(**kwargs)
            _prepare_subclass(subclass)

    setattr(wrapped_hook, _WORKFLOW_SUBCLASS_WRAPPED, True)
    cls.__init_subclass__ = classmethod(wrapped_hook)


# ==================================================================================
@overload
def workflow(cls: _T) -> _T: ...

@overload
def workflow(*names: str) -> Callable[[_T], _T]: ...

# ==================================================================================
def workflow(*args):
    """Decorate a class with an automatic post-construction workflow.

    ``@workflow`` discovers ``_w...`` methods defined directly on the decorated
    class. ``@workflow("InitializeUI", "InitializeState")`` explicitly defines
    the execution order. Workflow metadata is inherited normally by subclasses;
    a subclass decorated with ``@workflow`` replaces that metadata rather than
    merging with its base class.

    The construction boundary is propagated through ``__init_subclass__`` so a
    subclass workflow runs only after that subclass's own ``__init__`` returns.
    The QObject metaclass is therefore left untouched.
    """

    if len(args) == 1 and isinstance(args[0], type):
        cls = args[0]
        names: tuple[str, ...] | None = None

    else:
        if not all(isinstance(name, str) for name in args):
            raise TypeError("Workflow names must be strings.")

        names = tuple(_workflow_method_name(name) for name in args)
        if len(names) != len(set(names)):
            raise ValueError("Workflow names must be unique.")
        cls = None

    def decorate(target: _T) -> _T:
        workflow_names = names if names is not None else _discover_workflows(target)
        setattr(target, _WORKFLOW_METADATA, workflow_names)

        if "__init_subclass__" not in target.__dict__:
            _install_subclass_hook(target)

        else:
            _prepare_subclass(target)

        if "__init__" in target.__dict__:
            _wrap_init(target, target.__dict__["__init__"])

        else:
            def generated_init(self, *init_args, **init_kwargs):
                super(target, self).__init__(*init_args, **init_kwargs)

            _wrap_init(target, generated_init)

        return target

    if cls is not None:
        return decorate(cls)

    return decorate
