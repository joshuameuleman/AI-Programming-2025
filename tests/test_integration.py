#gemaakt door Joshua Meuleman
from src.deck import create_deck, draw
from src.ai.npc import NPC


def test_integration_round_counts_and_bet():
    deck = create_deck(1)
    # do not shuffle to have deterministic draws for test
    npc = NPC(bet_unit=1)
    npc.start_shoe(1)

    # deal deterministic first four cards
    player = [draw(deck), draw(deck)]
    dealer = [draw(deck), draw(deck)]

    # NPC observes player cards and dealer upcard
    for c in player:
        npc.observe_card(c)
    npc.observe_card(dealer[0])

    assert len(npc.counting.seen) == 3
    # recommended bet returns an integer and true_count is a float
    assert isinstance(npc.recommended_bet(), int)
    assert isinstance(npc.true_count(), float)
# Gemaakt door Joshua Meuleman