# Vladimir Core0

Vladimir Core0 is a deterministic, risk-aware hierarchical agent for the Pokémon Trading Card Game AI Battle Challenge. The agent ranks legal actions supplied by the simulator instead of generating illegal actions. It prioritizes survival, tactical progress, resource access, evolution, energy attachment, bench development, and recovery from negative status conditions.

## Repository contents

| File | Purpose |
|---|---|
| `main.py` | Agent entry point and deterministic option-ranking policy |
| `state.py` | Visible-game-state normalization and card resolution |
| `event_bus.py` | Optional debug event bus; silent by default |
| `deck.csv` | Legal 60-card deck represented by simulator card IDs |
| `card_catalog.json` | Official card metadata generated from the competition CSV |
| `test_agent.py` | Local syntax, deck, fallback, and numeric-option tests |
| `WRITEUP.md` | Strategy-category report source |

## Strategy

The policy uses the official simulator option types. It recognizes `PLAY=7`, `ATTACH=8`, `EVOLVE=9`, `RETREAT=12`, `ATTACK=13`, and `END=14`. When an option references a card, the agent resolves it using `area`, `index`, and `playerIndex`, then consults the official catalogue of 1,267 cards.

The policy is deterministic. Equal scores are resolved by stable option order. It does not use random selection. If an unexpected observation causes an internal exception, the fallback returns valid available option indices to preserve the simulator contract.

## Local validation

```bash
python3 -m py_compile event_bus.py state.py main.py
python3 test_agent.py
```

Expected result: `all checks passed`.

## Kaggle provenance

The source in this repository is the preserved Vladimir Core0 source package used for the Kaggle v5 workflow. The public Kaggle notebook is `jafs696/vladimir-core0`. The simulation submission and Strategy-category Writeup are separate Kaggle deliverables.

## Reproduction

1. Place the official competition `EN Card Data.csv` beside a generator script.
2. Generate `card_catalog.json` by mapping rows by `Card ID`.
3. Place the catalogue beside `main.py`.
4. Run `python3 test_agent.py`.
5. Package `main.py` and `deck.csv` at the top level for a simulation submission.

Do not commit API keys, passwords, `kaggle.json`, cookies, or private account data.
