
# Werkbaar stappenplan — Blackjack AI (focus: geen modeltraining, teller + search)

Doel van dit document
---------------------
Dit stappenplan is aangepast naar jullie voorkeur: we voeren geen modeltraining (geen langdurige RL-trainingsruns) uit in de MVP. In plaats daarvan focussen we op:

- betrouwbare simulator- en handlogica,
- een Hi‑Lo kaartteller voor state‑estimation en bet-sizing,
- een lichte zoek/prototypinglaag (Monte Carlo rollouts / expectimax) voor actie-evaluatie,
- duidelijke demos en tests.

Waarom deze keuze
-----------------
- Training met Reinforced Learning is niet volgens de opdracht
- Teller + search levert snel meetbare winst (betting + betere actie-evaluatie) en is eenvoudiger te demonstreren en te verifiëren.

Scope voor MVP (week 1)
- Werkende simulator en hand-helpers
- Hi‑Lo teller en demonstratie van running/true count
- Monte Carlo rollout prototype dat teller-informatie gebruikt om acties te evalueren
- Demo-script (geen training) en minimale tests

Sprint indeling (actiegericht)
--------------------------------

Sprint A — Setup & basis (0.25–0.5 dag)
- Tasks:
  - Repo-structuur (indien nog niet gedaan): `src/`, `src/ai/`, `tests/`, `examples/`.
  - `requirements.txt` met optionele GUI deps in `requirements-gui.txt`.
  - Acceptatie: `pip install -r requirements.txt` werkt.

Sprint B — Core models & helpers (0.5–1 dag)
- Tasks:
  - `src/deck.py`: create_deck(num_decks), shuffle, draw (reeds aanwezig).
  - `src/hand.py`: value(hand), is_blackjack, is_bust, is_soft (reeds aanwezig).
  - Unit-tests voor hand/logica.

Sprint C — Basic strategy + demo (0.5 dag)
- Tasks:
  - `src/ai/basic_strategy.py` (bestaande stub) uitbreiden met meer regels of houd het eenvoudig.
  - `examples/demo.py` (reeds aanwezig) gebruikt basic strategy voor één of enkele rondes.

Sprint D — Hi‑Lo Teller (0.5 dag)  <-- PRIORITEIT MVP
- Tasks:
  - Implementeer `src/ai/counting.py` met:
    - `Counting` class: reset(), update(card), running_count(), true_count(remaining_decks_estimate)`
    - eenvoudige CLI/demo printing van running/true count tijdens voorbeeld-rondes
  - Acceptatie: demo toont lopende telling tijdens het delen van kaarten; `true_count` berekent gedeeld door geschatte resterende decks.

Sprint E — Search prototype: Monte Carlo rollouts (1 dag)
- Tasks:
  - `src/ai/search.py` met een functie `evaluate_actions(player_hand, dealer_upcard, deck_snapshot, n_rollouts)`.
  - Rollouts gebruiken de actuele deck-samenstelling (of gesamplede resterende kaarten) en de teller om sampling te biasen.
  - Acceptatie: prototype vergelijkt expected reward voor `hit` vs `stand` over N rollouts en geeft de hoogste terug.

Sprint F — Integratie demo + evaluatie (0.5 dag)
- Tasks:
  - Verbind teller en search met `examples/demo.py` zodat demo de teller toont en (optioneel) search-actie kiest.
  - Simpele vergelijking: basic strategy vs basic+search (over enkele honderden eval-rondes) om EV-verschil te tonen.

Sprint G — Tests & docs (0.5 dag)
- Tasks:
  - Tests: `tests/test_hand.py`, `tests/test_counting.py`, `tests/test_search_smoke.py`.
  - Documenteer in `README.md` en `docs/` hoe je demo runt en wat de limitations zijn.

Optionele uitbreidingen (later, niet MVP)
- GUI voor visualisatie van teller en realtime stats.
- Ruimere search-optimalisaties: caching, parallel rollouts.
- Tabulaire RL als vervolgproject (als jullie alsnog willen trainen).

Concreet: bestanden en prioriteiten
---------------------------------
- hoog (MVP):
  - `src/ai/counting.py` (Hi‑Lo)
  - `src/ai/search.py` (Monte Carlo rollouts)
  - `examples/demo.py` (no-training demo)
- medium:
  - tests en docs
- laag (later):
  - GUI, uitgebreide search, RL training

Directe next actions (kies 1)
----------------------------
1) Ik implementeer onmiddellijk de Hi‑Lo teller (`src/ai/counting.py`) en werk `examples/demo.py` bij om running/true count te tonen tijdens een demo-ronde. (Aanbevolen)
2) Ik schrijf de design-notitie voor search + sampling (expectimax vs MCTS) als markdown in `docs/search_design.md` voor we code gaan schrijven.
3) Ik bouw direct een eenvoudige Monte Carlo rollout prototype dat de teller gebruikt om deck-sampling te biasen.

Checklist (MVP)
- [x] `src/deck.py` aanwezig
- [x] `src/hand.py` aanwezig
- [x] `src/ai/basic_strategy.py` aanwezig
- [x] `examples/demo.py` aanwezig (geen training)
- [ ] `src/ai/counting.py` (Hi‑Lo) — implementeren
- [ ] `src/ai/search.py` (Monte Carlo prototype) — implementeren
- [ ] tests voor hand/counting/search
- [ ] documentatie: `docs/search_design.md` en demo instructies

Acceptatiecriteria MVP
- Demo draait lokaal, toont running/true count en basic strategy action.
- Teller werkt correct op sample decks (handmatige verificatie).
- Search prototype kan korte rollouts uitvoeren en produceert an action-evaluation.

---

Als je akkoord bent met dit bijgewerkte plan, start ik direct met optie 1: implementatie van de Hi‑Lo teller en demo-integratie. Zeg "start teller" en ik begin met de code (en markeer de todo-items bij).

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
- [x] Core modellen
  - [x] `src/deck.py` — create_deck, shuffle, draw, num_decks
  - [x] `src/hand.py` — value, usable_ace, is_blackjack, is_bust
- [ ] Game loop & rules
  - [ ] `src/game.py` — play_round(policy, rules)
- [ ] Basic strategy
  - [ ] `src/ai/basic_strategy.py` — choose_action
  save/load
  - [ ] `examples/train.py` — training loop en evaluation
- [ ] Tests
  - [ ] `tests/test_hand.py`
  - [ ] `tests/test_basic_strategy.py`
  - [ ] `tests/test_learner.py`

- [ ] Graphical Window
    - [ ] Win/Loss Ratio
    - [ ] Kaarten weergeven mogelijks met A-2-...-K samen met suits
    

