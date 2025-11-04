# AI Programming - Blackjack AI

Beschrijving
---------
In dit project bouwen we een AI die het kaartspel Blackjack speelt. De focus ligt op het implementeren van een beslissingsstrategie die bepaalt welke actie de AI neemt: kaart vragen (hit), passen (stand), dubbelen (double down) of splitsen (split).

Doelen
-------
- Basis: Implementeer de "basic strategy" — een wiskundig onderbouwde set regels die de beste kans op winst geeft op basis van je kaart(en) en de open kaart van de dealer.
- Gevorderd (optioneel): Implementeer kaarttellen om de inzet dynamisch aan te passen afhankelijk van welke kaarten al gespeeld zijn.

Belangrijkste features
----------------------
- Kaartrepresentatie en deck-shuffling
- Spelershanden en dealer-logica
- Basic strategy engine die beslissingen maakt op basis van player-hand + dealer-upcard
- (Optie) Kaarttelsysteem en inzetlogica gebaseerd op de telling

Installatie
----------
Voor dit project zijn er geen verplichte externe dependencies in de README zelf; volg de projectconfiguratie in de repository voor specifieke taal- of pakketvereisten. Algemeen:

1. Clone de repository

   git clone <repository-url>

2. Open de repository in je favoriete IDE (bijv. VS Code).

3. Controleer of er een dependency-manifest is (bijv. `requirements.txt`, `pyproject.toml`, `package.json`) en installeer afhankelijkheden volgens de gebruikte taal.

Gebruik
------
De exacte commando's hangen af van de implementatietaal. Voorbeeld-wensen die je kunt verwachten of toevoegen:

- `python -m blackjack.simulator` — start een simulatie waarbij de AI meerdere rondes speelt en statistieken uitrolt.
- `node ./src/runner.js` — (voor Node.js) start een AI-runner.

Strategy toelichting
--------------------
1. Basic strategy
   - De AI volgt een vaste set regels gebaseerd op de totale waarde van de hand en of de hand "soft" (ace) of "hard" is, en de dealer's upcard.
   - Voorbeelden: Bij een hard 16 tegen dealer 7 -> hit; bij een soft 18 tegen dealer 6 -> double wanneer toegestaan.

2. Kaarttellen (gevorderd)
   - Een kaarttelsysteem (zoals Hi-Lo) houdt bij welke kaarten al zijn gespeeld en geeft een lopende telling.
   - Op basis van de telling kan de AI kiezen om de inzet te verhogen wanneer het deck 'hot' is (meer hoge kaarten beschikbaar), of te verlagen wanneer het deck 'cold' is.

Projectstructuur (suggestie)
---------------------------
- `README.md` — dit bestand
- `src/` — hoofdcode (AI, simulator, utils)
  - `ai/strategy.py` of `ai/strategy.js` — implementatie van basic strategy
  - `ai/counting.py` — optionele kaarttel-implementatie
  - `simulator/` — code om spellen te draaien en statistieken te verzamelen
- `tests/` — unit- en integratie-tests
- `examples/` — korte scripts die laten zien hoe de AI te gebruiken

Bijdragen
---------
Feedback, bugfixes en verbetering van de strategie zijn welkom. Volg deze stappen om bij te dragen:

1. Fork de repository.
2. Maak een feature branch (`git checkout -b feature/naam`).
3. Voeg tests toe voor nieuwe functionaliteit.
4. Open een pull request met een heldere beschrijving van je wijziging.

Licentie
--------
Voeg een licentie toe (bijv. MIT) indien gewenst. Als er geen licentie bestaat, neem contact op met de repository-eigenaar.

Contact / Vragen
-----------------
Voor vragen kun je een issue openen in de repository of de eigenaar contacteren.

---

Korte checklist (hulp voor ontwikkelaars)
- [x] Projectdoel en strategie-uitleg
- [ ] Voorbeeld runner / simulator
- [ ] Unit tests voor strategy
- [ ] (Optioneel) Kaarttellen en inzetlogica
