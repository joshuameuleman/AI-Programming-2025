from src.hand import value, is_blackjack, is_bust, is_soft


def test_soft_hand():
	hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': '7', 'suit': 'Clubs'}]
	v, usable = value(hand)
	assert v == 18
	assert usable is True


def test_blackjack():
	hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': 'K', 'suit': 'Clubs'}]
	assert is_blackjack(hand)


def test_bust():
	hand = [{'rank': '10', 'suit': 'Spades'}, {'rank': '9', 'suit': 'Hearts'}, {'rank': '5', 'suit': 'Diamonds'}]
	assert is_bust(hand)


def test_is_soft_true():
	hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': '6', 'suit': 'Clubs'}]
	assert is_soft(hand) is True


def test_is_soft_false():
	hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': 'K', 'suit': 'Clubs'}, {'rank': '2', 'suit': 'Clubs'}]
	assert is_soft(hand) is False

