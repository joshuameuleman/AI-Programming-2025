"""Voorbeeld-runner (demo): toont het delen van een enkele ronde en gebruikt basic strategy.

Dit script draait géén training of model-learning; het demonstreert alleen deck-creatie,
het delen van kaarten en het kiezen van een actie via `basic_strategy`.
"""
from src.deck import create_deck, shuffle, draw
from src.ai.counting import choose_action


def ask_num_decks() -> int:
    s = input("Hoeveel decks wil je gebruiken? (bijv. 6 of 10) [1]: ")
    if not s.strip():
        return 1
    try:
        n = int(s)
        if n < 1:
            print("Aantal decks moet positief zijn. Gebruik 1.")
            return 1
        return n
    except ValueError:
        print("Ongeldige invoer, 1 deck wordt gebruikt.")
        return 1


def format_card(card):
    # kaart is dict {'rank','suit'}
    return f"{card['rank']} of {card['suit']}"


def main():
    num_decks = ask_num_decks()
    deck = create_deck(num_decks)
    shuffle(deck)
    print(f"Deck aangemaakt met {len(deck)} kaarten ({num_decks} decks).\n")

    # Deel een simpele ronde: speler 2 kaarten, dealer 1 upcard
    player = [draw(deck), draw(deck)]
    dealer = [draw(deck), draw(deck)]

    print("Speler hand:")
    for c in player:
        print(" -", format_card(c))
    print("Dealer upcard:")
    print(" -", format_card(dealer[0]))

    action = choose_action(player, dealer[0])
    print(f"\nBasic strategy kiest: {action}")


if __name__ == "__main__":
    main()
"""Voorbeeld-runner: vraagt gebruiker hoeveel decks en toont deck-grootte."""
from src.deck import create_deck, shuffle
from src.ai.learner import Learner


def ask_num_decks() -> int:
    s = input("Hoeveel decks wil je gebruiken? (bijv. 6 of 10) [1]: ")
    if not s.strip():
        return 1
    try:
        n = int(s)
        if n < 1:
            print("Aantal decks moet positief zijn. Gebruik 1.")
            return 1
        return n
    except ValueError:
        print("Ongeldige invoer, 1 deck wordt gebruikt.")
        return 1


def main():
    num_decks = ask_num_decks()
    deck = create_deck(num_decks)
    shuffle(deck)
    print(f"Deck aangemaakt met {len(deck)} kaarten ({num_decks} decks).")
    

    # Starter learner (stub)
    learner = Learner()
    print("Learner geïnitialiseerd (stub). Klaar om training te implementeren.")


if __name__ == "__main__":
    main()
