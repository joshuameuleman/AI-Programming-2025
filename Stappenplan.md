# Werkbaar stappenplan — Blackjack AI (actiegericht)

Doel van dit document
---------------------
Geef een concrete set taken (met bestanden, korte instructies en acceptatiecriteria) zodat ontwikkelaars direct kunnen beginnen met implementeren en testen. Dit plan is afgestemd op een Python-implementatie met tabulaire leercomponent (geen neurale netwerken).

Scope MVP (week 1)
- Werkende simulator die rondes kan uitvoeren
- Basic strategy module die beslissingen neemt
- Tabulaire learner (Q-learning of Monte Carlo) die leert van episodes
- Minimale tests en een voorbeeld-runner om training/evaluatie te starten

Sprint indeling en concrete taken
--------------------------------

Sprint A — Setup & basis (0.5 dag)
- Taak A1: Repo structuur en omgeving
  - Maak mappen: `src/`, `src/ai/`, `tests/`, `examples/`.
  - Voeg `requirements.txt` toe met minimaal `pytest`.
  - Acceptatie: `pip install -r requirements.txt` draait zonder fouten.

Sprint B — Core modellen (1 dag)
- Taak B1: `src/deck.py`
  - Functies: `create_deck(num_decks=1)`, `shuffle(deck)`, `draw(deck)`.
  - Acceptatie: een korte REPL-test kan 52 kaarten teruggeven en `draw` vermindert deck.

- Taak B2: `src/hand.py`
  - Functies: `value(hand)` retourneert (best_value, usable_ace_bool), en helpers `is_blackjack`, `is_bust`.
  - Acceptatie: tests voor soft/hard hands slagen.

Sprint C — Game loop & basic rules (1 dag)
- Taak C1: `src/game.py` (eenvoudige ronde)
  - Implementeer een functie `play_round(policy, rules)` die één ronde draait met gegeven policy (callable that chooses action) en returns reward (float) plus trajectory (states, actions).
  - Regels: standaard blackjack (dealer hits <17), support voor double (vereenvoudigd) en no split initially.
  - Acceptatie: `play_round` retourneert reward in {-1, 0, 1} en geen crashes bij 100 runs.

Sprint D — Basic strategy (0.5 dag)
- Taak D1: `src/ai/basic_strategy.py`
  - Exporteer `choose_action(player_hand, dealer_upcard, rules)` met acties `hit/stand/double`.
  - Acceptatie: voor een set voorbeeldcases kiest functie verwachte actie (unit-tests).

Sprint E — Tabulaire learner (1–2 dagen)
- Taak E1: `src/ai/learner.py` — tabulaire Q-learning (of On-policy Monte Carlo)
  - State definitie: tuple (player_total_bucket, usable_ace, dealer_upcard).
  - Actions: `hit`, `stand`, `double` (split later).
  - Functies: `select_action(state, epsilon)`, `update(trajectory)` en `save(path)`/`load(path)`.
  - Acceptatie: een korte training van 1k episodes wijzigt Q-table (niet-constant) en `save` schrijft JSON.

Sprint F — Simulator & training runner (0.5 dag)
- Taak F1: `examples/train.py`
  - Start training met configuratie (episodes, seed, checkpoints).
  - Periodiek (bv iedere 1k episodes) evalueer policy met epsilon=0 over 500 episodes en log EV.
  - Acceptatie: `python .\examples\train.py` draait en schrijft `policy.json`.

Sprint G — Tests & CI (0.5 dag)
- Taak G1: `tests/test_hand.py`, `tests/test_basic_strategy.py`, `tests/test_learner.py`
  - Minimaal: handwaarde (soft/hard), strategy expected action, learner update smoke test.
  - Voeg GitHub Actions workflow toe `.github/workflows/python.yml` die tests draait op push/PR.

Sprint H — Optionele uitbreidingen (week 2+)
- Kaarttellen module (`src/ai/counting.py`) en inzetaanpassing
- Support voor splits en surrender
- Meer verfijnde state-aggregatie of progressive feature toevoeging

Concreet: bestanden en voorbeelden
---------------------------------
- src/deck.py — deck en draw
- src/hand.py — handvalue en helpers
- src/game.py — playsingle round met policy callback
- src/ai/basic_strategy.py — deterministische basic strategy
- src/ai/learner.py — tabulaire learner en policy opslag
- examples/train.py — starter voor training en evaluation
- tests/* — pytest tests
- requirements.txt — dependencies (pytest)

Direct uitvoerbare commando's (PowerShell / Windows)
-------------------------------------------------
Installeer dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

Run tests:

```powershell
pytest -q
```

Start training (voorbeeld):

```powershell
python .\examples\train.py --episodes 10000 --checkpoint_every 1000
```

Acceptatiecriteria per milestone (kort)
------------------------------------
- MVP: Na training van 10k episodes kan de learner policy laden en produceert de evaluator een EV-rapport.
- Tests: minimaal 3 unit-tests (hand, strategy, learner) slagen in CI.

Directe next steps — wat ik nu kan doen (kies één)
-------------------------------------------------
1) Maak direct scaffolding aan (mappen + lege bestanden + `requirements.txt` + basistest) zodat je lokaal meteen kunt starten.  
2) Begin meteen met implementatie van `src/deck.py` en `src/hand.py` en voer unit-tests uit.  
3) Begin met `src/ai/learner.py` (stub) en een very small training loop (100 episodes) om integratie te valideren.

Aanbeveling: kies optie 1 om snel een werkende ontwikkelomgeving te krijgen, daarna optie 2.

---

Als je akkoord bent, maak ik nu de scaffolding (optie 1): mappen en lege bestanden + `requirements.txt` en een basis `tests/test_hand.py`. Dat duurt ~5–10 minuten.

## Checklist (direct bruikbaar)
Gebruik deze checklist om voortgang te tracken. Vink items aan wanneer ze klaar zijn.

- [x] `README.md` — projectbeschrijving en doelen
- [x] `Stappenplan.md` — actioneel stappenplan (dit bestand)
- [x] Scaffolding: mappen en basisbestanden
  - [x] `src/`
  - [x] `src/ai/`
  - [x] `tests/`
  - [x] `examples/`
  - [x] `requirements.txt` (met `pytest`)
- [ ] Core modellen
  - [ ] `src/deck.py` — create_deck, shuffle, draw
  - [ ] `src/hand.py` — value, usable_ace, is_blackjack, is_bust
- [ ] Game loop & rules
  - [ ] `src/game.py` — play_round(policy, rules)
- [ ] Basic strategy
  - [ ] `src/ai/basic_strategy.py` — choose_action
- [ ] Leercomponent (tabulair)
  - [ ] `src/ai/learner.py` — select_action, update, save/load
  - [ ] `examples/train.py` — training loop en evaluation
- [ ] Tests
  - [ ] `tests/test_hand.py`
  - [ ] `tests/test_basic_strategy.py`
  - [ ] `tests/test_learner.py`

- [ ] Graphical Window
    - [ ] Win/Loss Ratio
    - [ ] Kaarten weergeven mogelijks met A-2-...-K samen met suits
    

