"""
# Gemaakt door Joshua Meuleman

Headless simulator to compare NPC (counting agent) vs a baseline (non-counting)
player. Prints win counts and relative advantage.

Usage:
    python ./examples/simulate.py --rounds 1000 --decks 6

"""
import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.game import Game
from src.player_impls import BaselinePlayer, NPCPlayer
from src import deck


def run_simulation(rounds: int = 1000, num_decks: int = 6):
    game = Game(num_decks=num_decks)
    # create players
    baseline = BaselinePlayer("You", fixed_bet=1)
    npc = NPCPlayer("NPC")

    # start shoe and register observer so NPC sees cards
    game.start_shoe()
    deck.register_draw_observer(npc.npc.observe_card)

    stats = {"rounds": 0, "baseline_wins": 0, "npc_wins": 0, "pushes": 0, "baseline_net": 0.0, "npc_net": 0.0}

    for i in range(rounds):
        res = game.play_round([baseline, npc])
        stats["rounds"] += 1
        bnet = res.get(baseline.id, {}).get("net", 0.0)
        nnet = res.get(npc.id, {}).get("net", 0.0)
        stats["baseline_net"] += float(bnet)
        stats["npc_net"] += float(nnet)

        # decide win by net>0
        if bnet > 0 and nnet <= 0:
            stats["baseline_wins"] += 1
        elif nnet > 0 and bnet <= 0:
            stats["npc_wins"] += 1
        elif bnet > 0 and nnet > 0:
            # both won: count both
            stats["baseline_wins"] += 1
            stats["npc_wins"] += 1
        else:
            stats["pushes"] += 1

    deck.unregister_draw_observer(npc.npc.observe_card)

    # compute comparative metrics
    b_w = stats["baseline_wins"]
    n_w = stats["npc_wins"]
    if b_w == 0:
        adv_pct = float('inf') if n_w > 0 else 0.0
    else:
        adv_pct = (n_w - b_w) / float(b_w) * 100.0

    print("Simulation finished")
    print(f"Rounds: {stats['rounds']}")
    print(f"Baseline wins: {b_w}")
    print(f"NPC wins: {n_w}")
    if adv_pct == float('inf'):
        print("NPC won wins while baseline had zero wins (infinite relative improvement)")
    else:
        print(f"NPC won {adv_pct:.2f}% more wins than the baseline (relative to baseline wins)")
    print(f"Baseline net total: {stats['baseline_net']:.2f}")
    print(f"NPC net total: {stats['npc_net']:.2f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=1000)
    parser.add_argument("--decks", type=int, default=6)
    args = parser.parse_args()
    run_simulation(rounds=args.rounds, num_decks=args.decks)


if __name__ == "__main__":
    main()
