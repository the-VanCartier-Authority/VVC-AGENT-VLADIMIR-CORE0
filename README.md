# Vladimir Core0

Vladimir Core0 is a deterministic, risk-aware hierarchical agent for the Pokémon Trading Card Game AI Battle Challenge. The agent ranks legal actions supplied by the simulator instead of generating illegal actions. It prioritizes survival, tactical progress, resource access, evolution, energy attachment, bench development, and recovery from negative status conditions.

## Repository contents

| File | Purpose |
|---|---|
| `main.py` | Agent entry point and deterministic option-ranking policy |
| `state.py` | Visible-game-state normalization and card resolution |
| `event_bus.py` | Optional debug event bus; silent by default |
| `deck.csv` | Legal 60-card deck represented by simulator card IDs |
| `card_catalog.json` | Optional generated metadata; absent from this repository commit, so no official catalog coverage is claimed |
| `test_agent.py` | Local syntax, import compatibility, deck, synthetic catalog, isolation, determinism, and ranking checks |
| `WRITEUP.md` | Strategy-category report source |

## Strategy

The policy uses the official simulator option types. It recognizes `PLAY=7`, `ATTACH=8`, `EVOLVE=9`, `RETREAT=12`, `ATTACK=13`, and `END=14`. When an option references a card, the agent resolves it using `area`, `index`, and `playerIndex`, then consults `card_catalog.json` only if that optional artifact is present. This repository commit does not contain the catalog; the tests use an explicitly synthetic fixture and do not verify coverage of the reported 1,267 official cards.

The policy is deterministic. Equal scores are resolved by stable option order. It does not use random selection. If an unexpected observation causes an internal exception, the fallback returns valid available option indices to preserve the simulator contract.

## Local validation

```bash
python3 -m py_compile event_bus.py state.py main.py core/__init__.py core/state.py core/event_bus.py
python3 test_agent.py
```

Expected result: `all checks passed`.

## Kaggle provenance

The source in this repository is the preserved Vladimir Core0 source package used for the Kaggle v5 workflow. The public Kaggle notebook is `jafs696/vladimir-core0`. The simulation submission and Strategy-category Writeup are separate Kaggle deliverables.

## Reproduction

1. Obtain the official competition `EN Card Data.csv` under the applicable competition terms.
2. Build `card_catalog.json` with a reviewed, versioned generator that maps rows by `Card ID`; the generator is not included in this repository.
3. Record source provenance and a digest, then place the generated catalog beside `main.py`. Without it, card metadata lookup returns an empty result.
4. Run `python3 test_agent.py`; its synthetic catalog fixture is not official game data.
5. Package `main.py` and `deck.csv` at the top level for a simulation submission.

Do not commit API keys, passwords, `kaggle.json`, cookies, or private account data.
