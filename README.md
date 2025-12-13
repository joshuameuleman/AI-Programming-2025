# AI Programming - Blackjack AI

Een Blackjack-implementatie met AI-spelers, basic strategy, (optioneel) kaarttellen en een tkinter-GUI met luxe kaartafbeeldingen.

## Team
- [Joshua Meuleman](https://github.com/joshuameuleman)
- [Robbe Lambrechts](https://github.com/lomopoio)
- [Jamie Jones](https://github.com/JollyJones101)
- [Alberiek Depreytere](https://github.com/AlberiekDepreytere)

## Features
- Spelengine met shoe, dealer, spelershanden en inzetafhandeling.
- Basic strategy beslissingen; NPC telt kaarten en past inzet aan.
- GUI (tkinter) met kaartafbeeldingen en playmat-selectie.
- CLI/demo-scripts in `examples/`.
- Tests voor handwaardes, counting en integratie.

## Vereisten
- Python 3.9+.
- Pillow voor beeldschaling in de GUI (staat in requirements).

## Installatie
1. Clone
   ```bash
   git clone <repository-url>
   cd AI-Programming-2025
   ```
2. Virtuele omgeving (Windows PowerShell)
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-gui.txt
   ```

## GUI starten
Activeer de venv en run:
```bash
python -m src.gui.blackjack_gui
```
- Kies optioneel een playmat bij start.
- Kaartassets: `src/gui/full_art_luxe_kaarten` (hearts/spades), fallback naar tekst indien niet gevonden.

## CLI/demo
- Snelle simulatie: `python examples/simulate.py`
- Meerdere spelers/demo: `python examples/demo_multi.py`
- Eenvoudige CLI-game: `python examples/cli_game.py`

## Tests
```bash
python -m pytest tests
```

## Projectstructuur
- `src/` — game-engine, AI, GUI.
- `examples/` — demo-scripts.
- `tests/` — unit- en integratietests.
- `requirements*.txt` — dependencies (GUI vereist Pillow).

## Bijdragen
Issues en PR’s zijn welkom. Voeg bij voorkeur tests toe voor nieuwe functionaliteit.
