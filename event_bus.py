import os
import sys
from typing import Callable
class EventBus:
    """Small optional event bus; production logging is disabled by default."""
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = {}
        self._debug = os.environ.get("VLADIMIR_DEBUG", "0") == "1"
    def subscribe(self, event_name: str, callback: Callable) -> None:
        self._subscribers.setdefault(event_name, []).append(callback)
    def publish(self, event_name: str, payload=None) -> None:
        if self._debug and not self._subscribers.get(event_name):
            print(f"[Event] {event_name}: {payload}", file=sys.stderr)
        for callback in self._subscribers.get(event_name, []):
            try: callback(payload)
            except Exception as exc:
                if self._debug: print(f"[EventBus] {event_name}: {exc}", file=sys.stderr)
