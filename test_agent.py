from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import py_compile
import tempfile

import main
from event_bus import EventBus
from main import agent
from state import GameState
from core import EventBus as CoreEventBus, GameState as CoreGameState
from core.event_bus import EventBus as NestedEventBus
from core.state import GameState as NestedGameState

root = Path(__file__).parent
for name in (
    "event_bus.py",
    "state.py",
    "main.py",
    "core/__init__.py",
    "core/event_bus.py",
    "core/state.py",
):
    py_compile.compile(str(root / name), doraise=True)

# The legacy `core.*` import paths must resolve to the canonical root classes.
assert CoreGameState is GameState
assert NestedGameState is GameState
assert CoreEventBus is EventBus
assert NestedEventBus is EventBus

with open(root / "deck.csv", encoding="utf-8") as handle:
    deck = [int(line.strip()) for line in handle if line.strip()]
assert len(deck) == 60, len(deck)
assert max(Counter(deck).values()) <= 4
assert main._legal_deck(deck)

# Preserve baseline deterministic rankings and the agent input/output contract.
assert agent({"select": {"option": [{"attack": True}, {"pass": True}], "maxCount": 1}}) == [0]
assert agent({"select": {"option": [{"pass": True}, {"draw": 2}], "maxCount": 1}}) == [1]
assert agent({"select": {"option": [], "maxCount": 0}}) == []
assert len(agent({})) == 60
numeric = {
    "current": {"yourIndex": 0, "players": [{"hand": [{"cardId": 1}], "active": [], "bench": []}, {}]},
    "select": {"option": [{"type": 14}, {"type": 13, "attackId": 1}], "maxCount": 1},
}
assert agent(numeric) == [1]
status_observation = {
    "current": {
        "yourIndex": 1,
        "turn": 4,
        "players": [{"active": {"hp": 100}}, {"active": {"paralyzed": True}, "bench": []}],
    },
    "select": {"option": [{"retreat": True}, {"attack": True}], "maxCount": 1},
}
assert agent(status_observation) == [0]
stateless_observation = {"select": {"option": [{"retreat": True}, {"attack": True}], "maxCount": 1}}
assert agent(stateless_observation) == [1]
assert agent(stateless_observation) == [1]
with ThreadPoolExecutor(max_workers=2) as pool:
    assert list(pool.map(agent, [status_observation, stateless_observation])) == [[0], [1]]

# Catalog loader behavior is tested with explicit missing and synthetic test-only data.
with tempfile.TemporaryDirectory() as directory:
    temp_root = Path(directory)
    assert main._load_catalog((str(temp_root / "missing.json"),)) == {}
    test_card = {"name": "Synthetic test-only card", "hp": 60}
    catalog_path = temp_root / "synthetic_catalog.json"
    catalog_path.write_text(json.dumps({"synthetic-test-card": test_card}), encoding="utf-8")
    loaded_catalog = main._load_catalog((str(catalog_path),))
    assert loaded_catalog == {"synthetic-test-card": test_card}

    original_catalog = main.CARD_CATALOG
    try:
        main.CARD_CATALOG = loaded_catalog
        game_state = GameState()
        game_state.update_from_dict({"current": {"yourIndex": 0, "players": [{"hand": [{"cardId": "synthetic-test-card"}]}]}})
        assert main._catalog_card({"area": "hand", "index": 0}, game_state) == test_card
    finally:
        main.CARD_CATALOG = original_catalog

print("all checks passed")
