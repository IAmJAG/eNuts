# ==================================================================================
# src/jAGFx/workflow/__workflow.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from functools import wraps
from traceback import format_exc
from typing import Callable, TypeVar, overload

# ==================================================================================
from utilities import createTask, getRunningLoop

# ==================================================================================
_T = TypeVar("_T", bound=type)
_WORKFLOW_PREFIX = "_w"
_ASYNC_PREFIX = "_a"
_WORKFLOW_METADATA = "__jagfx_workflow__"
_WORKFLOW_ASYNC = "__jagfx_workflow_async__"
_WORKFLOW_GUARD = "__jagfx_workflow_active__"
_WORKFLOW_INIT_WRAPPED = "__jagfx_workflow_init_wrapped__"
_WORKFLOW_SUBCLASS_WRAPPED = "__jagfx_workflow_subclass_wrapped__"


# ==================================================================================
def _trace(msg: str) -> None:
    """Best-effort verbose log; never raise from the tracer itself."""
    try:
        debug(f"[workflow] {msg}")
    except Exception:
        pass


# ==================================================================================
def _normalize_workflow_name(name: str) -> str:
    """Normalize an explicit workflow name to a ``_w...`` or ``_a...`` method name."""
    if not name:
        raise ValueError("Workflow name must be a non-empty string.")

    if name.startswith(_WORKFLOW_PREFIX) or name.startswith(_ASYNC_PREFIX):
        if name in (_WORKFLOW_PREFIX, _ASYNC_PREFIX):
            raise ValueError(
                f"Workflow name {name!r} must include a name after the prefix."
            )
        return name

    # Explicit bare names default to the synchronous ``_w`` prefix.
    return f"{_WORKFLOW_PREFIX}{name}"


# ==================================================================================
def _discover_workflows(cls: type) -> tuple[str, ...]:
    """Discover ``_w...`` and ``_a...`` methods defined directly on ``cls``."""
    return tuple(
        name
        for name, value in cls.__dict__.items()
        if (
            (name.startswith(_WORKFLOW_PREFIX) or name.startswith(_ASYNC_PREFIX))
            and callable(value)
        )
    )


# ==================================================================================
def _run_workflow(instance: object) -> None:
    names = getattr(type(instance), _WORKFLOW_METADATA, None)
    if names is None:
        _trace(f"{type(instance).__name__}: no workflow metadata - skip")
        return

    preferAsync: bool = getattr(type(instance), _WORKFLOW_ASYNC, True)
    loop = getRunningLoop() if preferAsync else None

    _trace(
        f"{type(instance).__name__}: run stages={list(names)} "
        f"async_={preferAsync} loop={'yes' if loop is not None else 'no'}"
    )

    for name in names:
        method = getattr(instance, name, None)
        if not callable(method):
            raise AttributeError(
                f"Workflow method {name!r} was not found on {type(instance).__name__}."
            )

        # ``_a...`` methods are scheduled when a loop is available and async_ is True.
        # ``_w...`` methods (and ``_a...`` when no loop / async_=False) run synchronously.
        if name.startswith(_ASYNC_PREFIX) and loop is not None:
            _trace(f"{type(instance).__name__}.{name}: SCHEDULE async")

            async def _runner(m=method, stage=name, clsName=type(instance).__name__):
                _trace(f"{clsName}.{stage}: BEGIN (async task)")
                try:
                    m()
                    _trace(f"{clsName}.{stage}: END (async task)")
                except Exception:
                    _trace(f"{clsName}.{stage}: FAIL (async task)\n{format_exc()}")
                    raise

            createTask(_runner)
        else:
            _trace(f"{type(instance).__name__}.{name}: BEGIN (sync)")
            try:
                method()
                _trace(f"{type(instance).__name__}.{name}: END (sync)")
            except Exception:
                _trace(f"{type(instance).__name__}.{name}: FAIL (sync)\n{format_exc()}")
                raise


# ==================================================================================
def _wrap_init(cls: type, original_init: Callable) -> None:
    if getattr(original_init, _WORKFLOW_INIT_WRAPPED, False):
        return

    @wraps(original_init)
    def wrapped_init(self, *init_args, **init_kwargs):
        outermost = not getattr(self, _WORKFLOW_GUARD, False)
        if outermost:
            setattr(self, _WORKFLOW_GUARD, True)
            _trace(f"{type(self).__name__}.__init__: ENTER outermost")

        try:
            original_init(self, *init_args, **init_kwargs)

        except BaseException:
            if outermost:
                _trace(f"{type(self).__name__}.__init__: FAIL in body\n{format_exc()}")
                delattr(self, _WORKFLOW_GUARD)
            raise

        if outermost:
            try:
                _trace(f"{type(self).__name__}.__init__: body done -> _run_workflow")
                _run_workflow(self)
                _trace(f"{type(self).__name__}.__init__: workflow complete")

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
def workflow(*names: str, async_: bool = True) -> Callable[[_T], _T]: ...


# ==================================================================================
def workflow(*args, async_: bool = True):
    """Decorate a class with an automatic post-construction workflow.

    ``@workflow`` discovers methods defined directly on the decorated class whose
    names start with ``_w`` (synchronous) or ``_a`` (async-capable). Explicit
    names via ``@workflow("InitializeUI", "_aLoadState")`` define execution
    order; bare names default to the ``_w`` prefix, while names already starting
    with ``_w`` / ``_a`` are used as-is.

    Execution rules for each discovered/listed method:

    - ``_w...`` — always invoked synchronously.
    - ``_a...`` — when ``async_=True`` (default) and a running asyncio loop is
      present, the synchronous body is wrapped in a one-liner coroutine and
      scheduled via ``utilities.createTask``; otherwise it is called directly.

    ``async_`` only affects ``_a...`` methods. Workflow metadata is inherited
    normally by subclasses; a subclass decorated with ``@workflow`` replaces
    that metadata rather than merging with its base class.

    The construction boundary is propagated through ``__init_subclass__`` so a
    subclass workflow runs only after that subclass's own ``__init__`` returns.
    The QObject metaclass is therefore left untouched.
    """

    if len(args) == 1 and isinstance(args[0], type):
        cls = args[0]
        names: tuple[str, ...] | None = None

    elif not args:
        cls = None
        names = None

    else:
        if not all(isinstance(name, str) for name in args):
            raise TypeError("Workflow names must be strings.")

        names = tuple(_normalize_workflow_name(name) for name in args)
        if len(names) != len(set(names)):
            raise ValueError("Workflow names must be unique.")
        cls = None

    def decorate(target: _T) -> _T:
        workflow_names = names if names is not None else _discover_workflows(target)
        setattr(target, _WORKFLOW_METADATA, workflow_names)
        setattr(target, _WORKFLOW_ASYNC, async_)

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
