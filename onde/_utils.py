from __future__ import annotations
from typing import Any, Callable, Set
import threading

_local = threading.local()

def _get_stack() -> list["ReactiveNode"]:
    if not hasattr(_local, "stack"):
        _local.stack = []
    return _local.stack

class CycleError(RuntimeError):
    pass
class ReactiveNode:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: Set["ReactiveNode"] = set()

    def depend(self) -> None:
        stack = _get_stack()
        if not stack:
            return
        current = stack[-1]
        nodes = sorted([self, current], key=id)
        with nodes[0]._lock, nodes[1]._lock:
            self._subscribers.add(current)
            current._dependencies.add(self)

    def notify(self) -> None:
        with self._lock:
            subs = list(self._subscribers)
        for sub in subs:
            sub.invalidate()

    def notify(self) -> None:
        with self._lock:
            subs = list(self._subscribers)
        for sub in subs:
            sub.invalidate()

class ComputedValue(ReactiveNode):
    def __init__(self, fn: Callable[[], Any]) -> None:
        super().__init__()
        self.fn = fn
        self._dirty = True
        self._cached_value: Any = None
        self._dependencies: Set[ReactiveNode] = set()
        self._computing = False

    def invalidate(self) -> None:
        with self._lock:
            if self._dirty:
                return
            self._dirty = True
        self.notify()

    def _cleanup_dependencies(self) -> None:
        for dep in self._dependencies:
            with dep._lock:
                dep._subscribers.discard(self)
        self._dependencies.clear()

    def get(self) -> Any:
        self.depend()

        with self._lock:
            if not self._dirty:
                return self._cached_value
            if self._computing:
                raise CycleError(
                    f"\033[31mError\033[0m -> Cycle in computed: {self.fn.__name__}"
                )
            self._computing = True
            self._cleanup_dependencies()

        stack = _get_stack()
        stack.append(self)
        try:
            value = self.fn()
        finally:
            stack.pop()
            with self._lock:
                self._cached_value = value if "value" in dir() else self._cached_value
                self._dirty = False
                self._computing = False

        return value

    def __call__(self) -> Any:
        return self.get()