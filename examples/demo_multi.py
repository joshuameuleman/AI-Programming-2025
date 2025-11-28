"""Automatische demo: meerdere rondes tonen NPC geheugen en telling.

Dit script draait een korte serie rondes zonder interactie zodat je kunt
zien hoe de `NPC` kaarten onthoudt en hoe running/true count veranderen.
"""
import os
import sys

# Zorg dat project root in imports werkt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import create_deck, shuffle, draw, register_draw_observer, unregister_draw_observer
from src.ai.npc import NPC
import argparse


def format_card(card):
    return f"{card['rank']} of {card.get('suit','?')}"


def run_demo(num_decks: int = 6, rounds: int = 5):
    deck = create_deck(num_decks)
    shuffle(deck)
    npc = NPC(bet_unit=1)
    npc.start_shoe(num_decks)
    # Register NPC as observer so it automatically sees every drawn card
    register_draw_observer(npc.observe_card)

    print(f"Start shoe: {num_decks} decks ({len(deck)} kaarten). Rounds: {rounds}\n")

    try:
        for r in range(1, rounds + 1):
            if len(deck) < 10:
                print("Weer reshuffle nodig — niet genoeg kaarten om door te gaan.")
                break

            print(f"--- Ronde {r} ---")
            # Deel basis handen
            player = [draw(deck), draw(deck)]
            dealer = [draw(deck), draw(deck)]

            # NPC will have observed all draws automatically via observer

            print("Zichtbare kaarten (na deal):")
            for c in player:
                print("  Speler:", format_card(c))
            print("  Dealer upcard:", format_card(dealer[0]))

            print(f"Running count (zichtbaar): {npc.running_count()}")
            print(f"True count (est): {npc.true_count():.2f}")
            print(f"Aanbevolen inzet (units): {npc.recommended_bet()}\n")

            # Reveal dealer hole card at end of round (NPC observed when drawn)
            print("Dealer hole kaart wordt onthuld:", format_card(dealer[1]))
            print(f"Running count (na onthulling): {npc.running_count()}")
            print(f"True count (est): {npc.true_count():.2f}")
            print(f"Totaal geziene kaarten: {len(npc.counting.seen)}")
            print(f"Kaarten resterend in deck: {len(deck)}\n")
    finally:
        unregister_draw_observer(npc.observe_card)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo: NPC counting across multiple rounds")
    parser.add_argument("--decks", type=int, default=6, help="Aantal decks in de shoe (default: 6)")
    parser.add_argument("--rounds", type=int, default=5, help="Aantal rondes om te simuleren (default: 5)")
    args = parser.parse_args()
    run_demo(num_decks=args.decks, rounds=args.rounds)
