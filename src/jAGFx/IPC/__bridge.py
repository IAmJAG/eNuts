# ==================================================================================
from __future__ import annotations

# ==================================================================================
from time import monotonic_ns
from typing import Awaitable, Callable, Dict, Mapping, Type
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.services import AsyncService

# ==================================================================================
from ..types.interface.communication import iBridge, iEndpoint, iMessage

# ==================================================================================
MessageProcessor = Callable[[iMessage], Awaitable[None] | None]

# ==================================================================================
class Bridge(iBridge):
    """Process-local base for entity binding (real or proxy role).

    Owns its correlation lifecycle completely:

    - Active Message Timeout Tracker (AMTT) + active processors
    - Dormant Message Timeout Tracker (DMTT) + dormant processors
    - Terminal policy (immediate full cleanup)
    - Active → dormant → permanent expiry via AsyncService timeout loops

    Type handlers are resolved via MRO (most-specific first) with an exact-type
    cache. Subclasses populate messageHandlers and implement domain behavior.
    """

    # Default timeouts (nanoseconds)
    C_DEFAULT_ACTIVE_TIMEOUT_NS: int = 30_000_000_000                       # 30 s
    C_DEFAULT_DORMANT_TIMEOUT_NS: int = C_DEFAULT_ACTIVE_TIMEOUT_NS * 3     # 60 s
    C_MAX_SERVICE_THROTTLE_S: float = 30.0                                  # cap when idle

    def __init__(self) -> None:
        self._bridgeId: UUID = uuid4()
        self._endpoint: iEndpoint = None

        self._amtt: Dict[UUID, int] = {}
        self._dmtt: Dict[UUID, int] = {}
        self._processors: Dict[UUID, MessageProcessor] = {}
        self._dprocessors: Dict[UUID, MessageProcessor] = {}

        self._messageHandlers: Dict[Type[iMessage], MessageProcessor] = {}
        self._handlerCache: Dict[Type[iMessage], MessageProcessor | None] = {}

        self._lastActiveTickNs: int = 0
        self._lastDormantTickNs: int = 0

        self._activeTimeoutService = AsyncService(
            work=self._activeTimeoutWork,
            name=f"Bridge[{self._bridgeId}].activeTimeout",
            throttle=0.0,
        )

        self._dormantTimeoutService = AsyncService(
            work=self._dormantTimeoutWork,
            name=f"Bridge[{self._bridgeId}].dormantTimeout",
            throttle=0.0,
        )

    # ------------------------------------------------------------------
    # Identity / handlers
    # ------------------------------------------------------------------
    @property
    def bridgeId(self) -> UUID:
        return self._bridgeId

    @property
    def messageHandlers(self) -> Mapping[Type[iMessage], MessageProcessor]:
        return self._messageHandlers

    @property
    def endpoint(self) -> iEndpoint | None:
        return self._endpoint

    def _invalidateHandlerCache(self) -> None:
        self._handlerCache.clear()

    def _resolveHandler(self, message: iMessage) -> MessageProcessor | None:
        exact = type(message)
        if exact in self._handlerCache:
            return self._handlerCache[exact]

        for cls in exact.__mro__:
            handler = self._messageHandlers.get(cls)
            if handler is not None:
                self._handlerCache[exact] = handler
                return handler

        self._handlerCache[exact] = None
        return None

    # ------------------------------------------------------------------
    # Endpoint attachment
    # ------------------------------------------------------------------
    def attachEndpoint(self, endpoint: iEndpoint) -> None:
        self._endpoint = endpoint
        self._lastActiveTickNs = monotonic_ns()
        self._lastDormantTickNs = monotonic_ns()

        if not self._activeTimeoutService.isRunning:
            self._activeTimeoutService.start()

        if not self._dormantTimeoutService.isRunning:
            self._dormantTimeoutService.start()

    def detachEndpoint(self) -> None:
        if self._activeTimeoutService.isRunning:
            self._activeTimeoutService.stop()

        if self._dormantTimeoutService.isRunning:
            self._dormantTimeoutService.stop()

        self._endpoint = None
        self._amtt.clear()
        self._dmtt.clear()
        self._processors.clear()
        self._dprocessors.clear()
        self._handlerCache.clear()

    # ------------------------------------------------------------------
    # Correlation registration / validation
    # ------------------------------------------------------------------
    def registerProcessor(
        self, correlationId: UUID, 
        processor: MessageProcessor, *, activeTimeoutNs: int  = C_DEFAULT_ACTIVE_TIMEOUT_NS
    ) -> None:
        
        if correlationId in self._amtt or correlationId in self._dmtt:
            raise ValueError(f"Correlation '{correlationId}' is already registered")

        timeoutNs = (
            activeTimeoutNs
            if activeTimeoutNs is not None
            else self.C_DEFAULT_ACTIVE_TIMEOUT_NS
        )
        if timeoutNs <= 0:
            raise ValueError("activeTimeoutNs must be positive")

        self._amtt[correlationId] = timeoutNs
        self._processors[correlationId] = processor
        self._activeTimeoutService.wake()

    def unregisterProcessor(self, correlationId: UUID) -> None:
        self._applyTerminalPolicy(correlationId)

    def hasProcessor(self, correlationId: UUID) -> bool:
        return correlationId in self._processors or correlationId in self._dprocessors

    def hasCorrelation(self, correlationId: UUID) -> bool:
        return correlationId in self._amtt or correlationId in self._dmtt

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    async def handleMessage(self, message: iMessage) -> None:
        cid = message.correlationId

        try:
            processor = self._processors.get(cid) or self._dprocessors.get(cid)
            if processor is not None:
                result = processor(message)
                if result is not None:
                    await result
                if message.isTerminal:
                    self._applyTerminalPolicy(cid)
                return

            handler = self._resolveHandler(message)
            if handler is None:
                return

            result = handler(message)
            if result is not None:
                await result

            if message.isTerminal and self.hasCorrelation(cid):
                self._applyTerminalPolicy(cid)

        except Exception as ex:
            self._onHandlerError(ex, message)

    def _onHandlerError(self, ex: BaseException, message: iMessage) -> None:
        # Log when project logger is wired; do not auto-terminal.
        _ = (ex, message, self._bridgeId)

    async def send(self, message: iMessage) -> None:
        if self._endpoint is None:
            raise RuntimeError("Bridge has no attached Endpoint")

        if message.ownerId is None:
            try:
                message.ownerId = self._bridgeId  # type: ignore[attr-defined]
            except Exception:
                pass

        await self._endpoint.send(message)

    # ------------------------------------------------------------------
    # Lifecycle policies
    # ------------------------------------------------------------------
    def _applyTerminalPolicy(self, correlationId: UUID) -> None:
        self._amtt.pop(correlationId, None)
        self._dmtt.pop(correlationId, None)
        self._processors.pop(correlationId, None)
        self._dprocessors.pop(correlationId, None)
        self._activeTimeoutService.wake()
        self._dormantTimeoutService.wake()

    def _moveToDormant(self, correlationId: UUID) -> None:
        remaining = self._amtt.pop(correlationId, None)
        processor = self._processors.pop(correlationId, None)
        if remaining is None and processor is None:
            return

        self._dmtt[correlationId] = self.C_DEFAULT_DORMANT_TIMEOUT_NS
        if processor is not None:
            self._dprocessors[correlationId] = processor

        self._dormantTimeoutService.wake()

    def _expirePermanently(self, correlationId: UUID) -> None:
        self._dmtt.pop(correlationId, None)
        self._dprocessors.pop(correlationId, None)
        self._amtt.pop(correlationId, None)
        self._processors.pop(correlationId, None)

    # ------------------------------------------------------------------
    # Timeout service work
    # ------------------------------------------------------------------
    async def _activeTimeoutWork(self) -> None:
        now = monotonic_ns()
        elapsed = now - self._lastActiveTickNs
        self._lastActiveTickNs = now
        if elapsed < 0:
            elapsed = 0

        expired: list[UUID] = []
        minRemaining = 0

        for cid, remaining in list(self._amtt.items()):
            newRemaining = remaining - elapsed
            if newRemaining <= 0:
                expired.append(cid)
            else:
                self._amtt[cid] = newRemaining
                if minRemaining == 0 or newRemaining < minRemaining:
                    minRemaining = newRemaining

        for cid in expired:
            self._moveToDormant(cid)

        if minRemaining > 0:
            self._activeTimeoutService.throttle = min(
                minRemaining / 1e9, self.C_MAX_SERVICE_THROTTLE_S
            )
        else:
            self._activeTimeoutService.throttle = self.C_MAX_SERVICE_THROTTLE_S

    async def _dormantTimeoutWork(self) -> None:
        now = monotonic_ns()
        elapsed = now - self._lastDormantTickNs
        self._lastDormantTickNs = now
        if elapsed < 0:
            elapsed = 0

        expired: list[UUID] = []
        minRemaining = 0

        for cid, remaining in list(self._dmtt.items()):
            newRemaining = remaining - elapsed
            if newRemaining <= 0:
                expired.append(cid)
            else:
                self._dmtt[cid] = newRemaining
                if minRemaining == 0 or newRemaining < minRemaining:
                    minRemaining = newRemaining

        for cid in expired:
            self._expirePermanently(cid)

        if minRemaining > 0:
            self._dormantTimeoutService.throttle = min(
                minRemaining / 1e9, self.C_MAX_SERVICE_THROTTLE_S
            )
        else:
            self._dormantTimeoutService.throttle = self.C_MAX_SERVICE_THROTTLE_S


# ==================================================================================
__all__ = ["Bridge"]
