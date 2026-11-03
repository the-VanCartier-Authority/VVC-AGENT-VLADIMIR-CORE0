"""Compatibility namespace for the canonical root-level agent modules."""

from .event_bus import EventBus
from .state import GameState

__all__ = ["EventBus", "GameState"]
