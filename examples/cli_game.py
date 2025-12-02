"""
# Gemaakt door Joshua Meuleman

Simple CLI game where a human plays against the NPC.

Run directly from project root:
    python .\examples\cli_game.py

"""
import sys
from pathlib import Path

# Ensure project root on sys.path for direct execution
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.game import Game
from src.player_impls import HumanPlayer, NPCPlayer
from src import deck


def main():
    print("CLI Blackjack — human vs NPC")
    num_decks = input("Number of decks (default 6): ") or "6"
    try:
        num_decks = int(num_decks)
    except Exception:
        num_decks = 6

    game = Game(num_decks=num_decks)
    # Create players
    human = HumanPlayer("You")
    npc_agent = NPCPlayer("NPC")

    # Inform NPC about shoe and register observer
    game.start_shoe()
    deck.register_draw_observer(npc_agent.npc.observe_card)

    round_no = 0
    try:
        while True:
            round_no += 1
            print(f"--- Round {round_no} ---")
            summary = game.play_round([human, npc_agent])
            print("Round summary:", summary)
            cont = input("Play another round? (y/n): ")
            if not cont.strip().lower().startswith("y"):
                break
    finally:
        deck.unregister_draw_observer(npc_agent.npc.observe_card)
        print("Exiting — observer unregistered")


if __name__ == "__main__":
    main()
