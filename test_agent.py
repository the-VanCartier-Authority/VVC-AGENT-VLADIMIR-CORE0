from collections import Counter
from pathlib import Path
import py_compile
root = Path(__file__).parent
for name in ('event_bus.py', 'state.py', 'main.py'):
    py_compile.compile(str(root / name), doraise=True)
with open(root / 'deck.csv', encoding='utf-8') as handle:
    deck = [int(line.strip()) for line in handle if line.strip()]
assert len(deck) == 60, len(deck)
assert max(Counter(deck).values()) <= 4
from main import agent
assert agent({'select': {'option': [{'attack': True}, {'pass': True}], 'maxCount': 1}}) == [0]
assert agent({'select': {'option': [{'pass': True}, {'draw': 2}], 'maxCount': 1}}) == [1]
assert agent({'select': {'option': [], 'maxCount': 0}}) == []
assert len(agent({})) == 60
numeric = {
    'current': {'yourIndex': 0, 'players': [{'hand': [{'cardId': 1}], 'active': [], 'bench': []}, {}]},
    'select': {'option': [{'type': 14}, {'type': 13, 'attackId': 1}], 'maxCount': 1},
}
assert agent(numeric) == [1]
obs = {
    'current': {
        'yourIndex': 1,
        'turn': 4,
        'players': [{'active': {'hp': 100}}, {'active': {'paralyzed': True}, 'bench': []}],
    },
    'select': {'option': [{'retreat': True}, {'attack': True}], 'maxCount': 1},
}
assert agent(obs) == [0]
print('all checks passed')
