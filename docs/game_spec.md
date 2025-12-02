# Gemaakt door Joshua Meuleman

# Blackjack Game Specification and Public API

Doel: Een eenvoudige, testbare implementatie van Blackjack (single-player vs dealer) waarop de deterministic NPC kan worden aangesloten. Deze spec beschrijft regels en de publieke API van de core game library.

1) Spelregels (kort)
- Doel: speler dichter bij 21 dan dealer zonder >21 (bust).
- Kaarten: A,2-10,J,Q,K. Aces tellen als 1 of 11, naar beste voordeel voor hand.
- Dealerregels: hit tot soft 17 (configureerbaar). Standaard: dealer blijft op soft-17 (stand-on-soft-17 = False betekent hit on soft 17). Gebruik klassieke regels tenzij expliciet anders geconfigureerd.
- Blackjack (A + 10-value) betaalt 3:2 (configurabel). Als zowel dealer als speler blackjack hebben => push.
- Split/Double/Insurance: MVP ondersteunt `double` en ondersteunt eenvoudige `split` niet in eerste iteratie. Focus op hit/stand/double.

2) Shoe / reshuffle beleid
- Shoe grootte: N decks (configurabel) — NPC moet geïnformeerd worden over het aantal decks met `Game.start_shoe(num_decks)`.
- Reshuffle: optie `reshuffle_at_percent` (bijv. 0.25 betekent schudden bij 25% kaarten over). Standaard: reshuffle na elk rondje uit (configurable).

3) Inzetregels
- Minimale inzet: `min_bet` en `unit` (units voor NPC-berekening). Betting units zijn integers; NPC vertaalt true count naar units.

4) Publieke API (klassen + methoden)

- class `Game`
  - constructor: `Game(num_decks:int=6, min_bet:int=1, reshuffle_at_percent:float=0.25)`
  - `start_shoe()` — initialiseert en schudt shoe; notificeer AI/NPC over start (bijv. NPC.start_shoe(num_decks)).
  - `play_round(players: List[Player]) -> dict` — speelt één volledige ronde (deal, players act, dealer act, settle) en retourneert een samenvatting met resultaten per speler.
  - `deal_card()` — interne helper die `src.deck.draw()` gebruikt; moet draw-observers toelaten.
  - `should_reshuffle() -> bool` — boolean voor shoe-lifecycle.

- class `Player` (abstract/base)
  - `id` attribuut
  - `start_round()` — reset per-round state
  - `get_bet() -> int` — vraag de speler om een inzet (NPC of human wrapper implementatie)
  - `play_hand(dealer_upcard, game) -> Action` — beslis actie: 'hit', 'stand', 'double'
  - `receive_card(card)` — update interne hand(s)
  - `settle(result)` — ontvang uitkomst (win/lose/push) voor logging

- class `Dealer`
  - `play()` — automatiseert dealer behavior volgens rules (hit until 17 / soft17 behavior)

- class `Hand`
  - `add(card)`
  - `value()` -> best value <=21 or lowest bust value
  - `is_blackjack()`, `is_bust()`

5) Events / Observers
- `src.deck` exposeert `register_draw_observer(fn)` en `unregister_draw_observer(fn)`; Game moet NPC registreren als observer wanneer `play_round` start (of Game.start_shoe) zodat NPC `observe_card(card)` ontvangt op elke draw.

6) Testing
- Unit-tests moeten de deterministische game-loop valideren:
  - dealing werkt, hand-waardes correct (Aces), dealer regels gedrag
  - bondig integratietest: `Game.play_round` met een stub-NPC die eenvoudige acties uitvoert.

# Gemaakt door Joshua Meuleman
