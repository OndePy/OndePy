from __future__ import annotations
from collections import deque
from typing import Callable, Optional, Set
import threading
import _utils

_queue_lock = threading.Lock()
_flush_lock = threading.Lock()
_EFFECT_QUEUE: deque["Effect"] = deque()

class Effect(_utils.ReactiveNode):
    def __init__(self, fn: Callable[[], Optional[Callable[[], None]]]) -> None:
        super().__init__()
        self.fn = fn
        self._dependencies: Set[_utils.ReactiveNode] = set()
        self._cleanup: Optional[Callable[[], None]] = None
        self._dirty = True
        self._scheduled = False
        self._running = False
        self._disposed = False
        self._schedule()

    def invalidate(self) -> None:
        with self._lock:
            if self._disposed or self._dirty:
                return
            self._dirty = True
        self._schedule()

    def _schedule(self) -> None:
        with self._lock:
            if self._disposed or self._scheduled:
                return
            self._scheduled = True
        with _queue_lock:
            _EFFECT_QUEUE.append(self)

    def _cleanup_dependencies(self) -> None:
        for dep in self._dependencies:
            with dep._lock:
                dep._subscribers.discard(self)
        self._dependencies.clear()

    def _run_cleanup(self) -> None:
        with self._lock:
            cleanup = self._cleanup
            self._cleanup = None
        if cleanup is not None:
            cleanup()

    def run(self) -> None:
        with self._lock:
            if self._disposed:
                return
            if self._running:
                raise _utils.CycleError(f"Cycle détecté dans effect: {self.fn.__name__}")
            if not self._dirty:
                self._scheduled = False
                return
            self._scheduled = False
            self._dirty = False
            self._running = True

        self._run_cleanup()

        with self._lock:
            self._cleanup_dependencies()

        stack = _utils._get_stack()
        stack.append(self)
        try:
            result = self.fn()
            if result is not None and not callable(result):
                raise TypeError(
                    f"Un effect doit retourner None ou une fonction de cleanup, "
                    f"reçu: {type(result).__name__}"
                )
            with self._lock:
                self._cleanup = result
        finally:
            stack.pop()
            with self._lock:
                self._running = False

    def dispose(self) -> None:
        with self._lock:
            if self._disposed:
                return
            self._disposed = True
        self._run_cleanup()
        with self._lock:
            self._cleanup_dependencies()


def flush_effects() -> None:
    if not _flush_lock.acquire(blocking=False):
        return

    try:
        iterations = 0
        max_iterations = 1000

        while True:
            with _queue_lock:
                if not _EFFECT_QUEUE:
                    break
                eff = _EFFECT_QUEUE.popleft()

            iterations += 1
            if iterations > max_iterations:
                raise RuntimeError("Trop de réexécutions d'effets. Boucle probable.")

            eff.run()
    finally:
        _flush_lock.release()


def effect(fn: Callable[[], Optional[Callable[[], None]]]) -> Effect:
    eff = Effect(fn)
    flush_effects()
    return eff