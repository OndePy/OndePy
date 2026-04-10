from __future__ import annotations
from typing import Any, Callable
import _utils

def computed(fn: Callable[[], Any]) -> _utils.ComputedValue:
    return _utils.ComputedValue(fn)