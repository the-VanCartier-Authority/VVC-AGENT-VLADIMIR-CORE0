from __future__ import annotations
import os
import json
import time
from collections import Counter
from event_bus import EventBus
from state import GameState

TIME_BUDGET_SECONDS = 1.80
MAX_COPIES = 4
FALLBACK_DECK = (
    [721] * 4 + [722] * 4 + [723] * 4 + [1145] * 4 + [1227] * 4 + [1235] * 4
    + [3] * 4 + [1] * 4 + [2] * 4 + [4] * 4 + [5] * 4 + [6] * 4
    + [8] * 4 + [9] * 4 + [10] * 4
)
CARD_CATALOG: dict[str, dict] = {}

def _load_catalog(paths: tuple[str, ...] | None = None) -> dict[str, dict]:
    """Load SDK-exported card metadata when the notebook has generated it."""
    candidate_paths = paths if paths is not None else (
        os.path.join(os.path.dirname(__file__), "card_catalog.json"),
        "/kaggle_simulations/agent/card_catalog.json",
    )
    for path in candidate_paths:
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, TypeError):
            continue
    return {}

CARD_CATALOG = _load_catalog()
OPTION_LABELS = {
    0: "number", 1: "yes", 2: "no", 3: "card", 4: "tool_card",
    5: "energy_card", 6: "energy", 7: "play", 8: "attach",
    9: "evolve", 10: "ability", 11: "discard", 12: "retreat",
    13: "attack", 14: "end", 15: "skill", 16: "special_condition",
}

def _legal_deck(deck: list[int]) -> bool:
    return len(deck) == 60 and all(n <= MAX_COPIES for n in Counter(deck).values())

def read_deck_csv(event_bus: EventBus | None = None) -> list[int]:
    path = os.path.join(os.path.dirname(__file__), "deck.csv")
    if not os.path.exists(path):
        path = "/kaggle_simulations/agent/deck.csv"
    try:
        with open(path, encoding="utf-8") as handle:
            deck = [int(line.strip()) for line in handle if line.strip()]
        if not _legal_deck(deck):
            raise ValueError(f"illegal deck: {len(deck)} cards or more than four copies")
        return deck
    except (OSError, ValueError) as exc:
        (event_bus or EventBus()).publish("deck_error", str(exc))
        return list(FALLBACK_DECK)

def _text(value) -> str:
    return str(value).lower()

def _number(value, names: tuple[str, ...]) -> float:
    if isinstance(value, dict):
        for name in names:
            x = value.get(name)
            if isinstance(x, (int, float)):
                return float(x)
    return 0.0

def _catalog_card(option: dict, game_state: GameState) -> dict:
    if not isinstance(option, dict):
        return {}
    for key in ("cardId", "card_id", "id", "card"):
        value = option.get(key)
        if isinstance(value, dict):
            value = value.get("cardId", value.get("id"))
        if value is not None:
            return CARD_CATALOG.get(str(value), {})
    resolved = game_state.card_from_option(option)
    for key in ("cardId", "card_id", "id"):
        if resolved.get(key) is not None:
            return CARD_CATALOG.get(str(resolved[key]), {})
    return {}

def _catalog_text(card: dict, *keys: str) -> str:
    return " ".join(str(card.get(key, "")) for key in keys).lower()

def _catalog_float(card: dict, *keys: str) -> float:
    for key in keys:
        try:
            return float(card.get(key, 0) or 0)
        except (TypeError, ValueError):
            continue
    return 0.0

def _option_score(option: dict, index: int, game_state: GameState) -> float:
    """Interpretable, schema-tolerant score for a legal option."""
    option_type = option.get("type") if isinstance(option, dict) else None
    label = OPTION_LABELS.get(getattr(option_type, "value", option_type), "")
    text = f"{label} {_text(option)}"
    me = game_state.me()
    opp = game_state.opponent()
    active = game_state.active(me)
    opp_active = game_state.active(opp)
    score = 0.0
    card = _catalog_card(option, game_state)
    active_status = any(bool(active.get(k)) for k in ("poisoned", "burned", "asleep", "paralyzed", "confused"))
    if label == "attack": score += 8.0
    elif label == "play": score += 3.0
    elif label == "attach": score += 3.0
    elif label == "evolve": score += 5.0
    elif label == "retreat": score += 8.0 if active_status else 2.0
    elif label == "end": score -= 5.0
    if any(k in text for k in ("attack", "damage", "knockout", "ko")):
        score += 8.0
        if active_status: score -= 10.0
    if any(k in text for k in ("draw", "search", "fetch", "look", "tutor")): score += 4.0
    if any(k in text for k in ("evolve", "evolution")): score += 5.0
    if any(k in text for k in ("bench", "basic", "setup")): score += 3.0
    if any(k in text for k in ("energy", "attach")): score += 3.0
    stage = _catalog_text(card, "basic", "stage", "Stage (Pokémon)/Type (Energy and Trainer)")
    if (card.get("basic") or "basic" in stage) and len(game_state.bench(me)) < 5: score += 1.5
    if card.get("stage1") or card.get("stage2") or "stage 1" in stage or "stage 2" in stage:
        score += 2.0 if any(k in text for k in ("evolve", "evolution", "play")) else 0.0
    if _catalog_float(card, "hp", "HP") and active and _catalog_float(card, "hp", "HP") > _number(active, ("hp", "HP")): score += 0.5
    retreat = _catalog_float(card, "retreatCost", "Retreat")
    if retreat is not None and active_status and any(k in text for k in ("retreat", "switch")): score += max(0.0, 3.0 - retreat)
    if any(k in text for k in ("discard", "shuffle", "mill")): score -= 1.0
    if any(k in text for k in ("retreat", "switch")): score += 8.0 if active_status else (2.0 if active else 0.0)
    if any(k in text for k in ("heal", "cure", "remove status")):
        status = any(bool(active.get(k)) for k in ("poisoned", "burned", "asleep", "paralyzed", "confused"))
        score += 7.0 if status else 0.5
    bench_count = len(game_state.bench(me))
    bench_max = _number(me, ("benchMax", "bench_max")) or 5
    if bench_count < bench_max and any(k in text for k in ("bench", "basic")): score += 2.0
    if len(game_state.hand(me)) <= 2 and any(k in text for k in ("draw", "search", "fetch")): score += 2.0
    if not active and any(k in text for k in ("basic", "active", "play")): score += 6.0
    if not opp_active and any(k in text for k in ("attack", "damage")): score -= 2.0
    score += min(_number(option, ("damage", "damageAmount")) / 20.0, 5.0)
    score += min(_number(option, ("draw", "drawCount")), 3.0)
    if any(k in text for k in ("pass", "end turn", "decline", "cancel")): score -= 5.0
    return score - index * 1e-6

def choose_actions(game_state: GameState) -> list[int]:
    options = game_state.select.get("option") or []
    max_count = int(game_state.select.get("maxCount", 0) or 0)
    if max_count <= 0 or not options: return []
    ranked = sorted(range(len(options)), key=lambda i: _option_score(options[i], i, game_state), reverse=True)
    return ranked[:max_count]

def agent(obs_dict: dict) -> list[int]:
    started = time.perf_counter()
    events = EventBus()
    if obs_dict.get("select") is None: return read_deck_csv(events)
    game_state = GameState()
    try:
        game_state.update_from_dict(obs_dict)
        result = choose_actions(game_state)
        options = game_state.select.get("option") or []
        max_count = int(game_state.select.get("maxCount", 0) or 0)
        if len(result) != max_count or any(i < 0 or i >= len(options) for i in result):
            result = list(range(min(max_count, len(options))))
        if time.perf_counter() - started > TIME_BUDGET_SECONDS:
            events.publish("timeout_warning", "decision exceeded time budget")
        return result
    except Exception as exc:
        events.publish("agent_error", repr(exc))
        options = (obs_dict.get("select") or {}).get("option") or []
        max_count = int((obs_dict.get("select") or {}).get("maxCount", 0) or 0)
        return list(range(min(max_count, len(options))))
