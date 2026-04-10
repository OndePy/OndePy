from __future__ import annotations
from typing import Any
import _utils
import effect

class _State(_utils.ReactiveNode):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self._value = value
        self._undoStack: list[Any] = [value]
        self._redoStack: list[Any] = []

    @property
    def value(self) -> Any:
        self.depend()
        with self._lock:
            return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        with self._lock:
            if new_value == self._value:
                return
            self._undoStack.append(self._value)
            self._redoStack.clear()
            self._value = new_value
        self.notify()
        effect.flush_effects()

    def undo(self) -> None:
        with self._lock:
            if not self._undoStack:
                return
            self._redoStack.append(self._value)
            self._value = self._undoStack.pop()
        self.notify()
        effect.flush_effects()

    def redo(self) -> None:
        with self._lock:
            if not self._redoStack:
                return
            self._undoStack.append(self._value)
            self._value = self._redoStack.pop()
        self.notify()
        effect.flush_effects()

    def silent_undo(self) -> None:
        with self._lock:
            if not self._undoStack:
                return
            self._redoStack.append(self._value)
            self._value = self._undoStack.pop()

    def silent_redo(self) -> None:
        with self._lock:
            if not self._redoStack:
                return
            self._undoStack.append(self._value)
            self._value = self._redoStack.pop()


def state(value: Any) -> _State:
    return _State(value)