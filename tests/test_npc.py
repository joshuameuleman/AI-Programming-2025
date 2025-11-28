#gemaakt door Joshua Meuleman

from src.ai.npc import NPC
from src.ai.basic_strategy import choose_action


def make_card(rank, suit="Hearts"):
    return {"rank": str(rank), "suit": suit}


def test_npc_remembers_seen_cards_and_counts():
    npc = NPC(bet_unit=1)
    npc.start_shoe(6)
    seq = [make_card(r) for r in (2, 3, 4, 5, 6)]
    for c in seq:
        npc.observe_card(c)
    # seen should equal number of observed cards
    assert len(npc.counting.seen) == len(seq)
    # running count should be +5 for 2-6
    assert npc.running_count() == 5
    # recommended bet should be at least 1 (and increase when TC rises)
    bet = npc.recommended_bet()
    assert isinstance(bet, int)


def test_npc_action_matches_basic_strategy():
    npc = NPC()
    player = [make_card("10"), make_card("6")]
    dealer = make_card("6")
    assert npc.choose_action(player, dealer) == choose_action(player, dealer)
#gemaakt door Joshua Meuleman