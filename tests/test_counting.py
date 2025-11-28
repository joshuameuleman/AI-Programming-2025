#gemaakt door Joshua Meuleman


from src.ai.counting import Counting


def make_card(rank):
    return {"rank": str(rank), "suit": "Hearts"}


def test_running_count_positive():
    c = Counting()
    seq = [make_card(r) for r in (2, 3, 4, 5, 6)]
    for card in seq:
        c.update(card)
    assert c.running_count() == 5


def test_running_count_negative():
    c = Counting()
    seq = [make_card(r) for r in (10, 'J', 'Q', 'K', 'A')]
    for card in seq:
        c.update(card)
    assert c.running_count() == -5


def test_true_count():
    c = Counting()
    seq = [make_card(r) for r in (2, 3, 4, 5, 6)]
    for card in seq:
        c.update(card)
    # running = 5, remaining decks estimate 2.5 -> true = 2.0
    tc = c.true_count(2.5)
    assert abs(tc - 2.0) < 1e-6

#gemaakt door Joshua Meuleman
