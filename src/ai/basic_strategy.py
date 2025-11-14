#gemaakt door Robbe Lambrechts
"""Basic strategy implementation (simplified).

Deze module geeft een functionele, deterministic basic strategy terug voor
de acties: 'hit', 'stand', 'double', 'split'. Het is een vereenvoudigde en
uitgebreide set regels die genoeg is voor demonstraties en unit-tests.

Opzet:
- Ondersteunt kaartrepresentatie als dict {'rank','suit'} of als string.
- Ondersteunt beslissingen voor hard totals, soft totals (usable ace) en pairs.
- Regels zijn niet alle casino-varianten volledig dekkend — pas regels aan naar behoefte.
"""
from typing import List

from ..hand import parse_card, value, card_value, is_pair


def choose_action(player_hand: List[object], dealer_upcard: object, rules: dict = None) -> str:
	"""Kies een actie volgens een vereenvoudigde basic strategy.

	player_hand: lijst van kaarten (dicts of strings)
	dealer_upcard: kaart (dict of str)
	rules: optioneel dict voor casino opties (niet gebruikt in deze simplificatie)

	Retourneert één van: 'hit', 'stand', 'double', 'split'
	"""
	# Compute hand value and whether it's soft
	total, usable = value(player_hand)
	dealer_rank = parse_card(dealer_upcard)
	# normalize dealer upcard value for comparisons (Ace high)
	if dealer_rank in ("A", "Ace"):
		d = 11
	else:
		d = card_value(dealer_rank)

	# Check pair rules first (simple)
	if is_pair(player_hand):
		r = parse_card(player_hand[0])
		# always split Aces and 8s
		if r in ("A", "Ace"):
			return "split"
		if r == "8":
			return "split"
		# never split 5s or 10s
		if r == "5":
			# treat as hard 10
			total = 10
			usable = False
		if r in ("10", "J", "Q", "K", "Jack", "Queen", "King"):
			return "stand"
		# split 2s/3s against dealer 2-7
		if r in ("2", "3"):
			if 2 <= d <= 7:
				return "split"
			else:
				return "hit"
		# split 6s against dealer 2-6
		if r == "6":
			if 2 <= d <= 6:
				return "split"
			else:
				return "hit"
		# split 7s against dealer 2-7
		if r == "7":
			if 2 <= d <= 7:
				return "split"
			else:
				return "hit"
		# split 9s against dealer 2-6,8,9
		if r == "9":
			if (2 <= d <= 6) or d in (8, 9):
				return "split"
			else:
				return "stand"

	# Soft hands (usable ace)
	if usable:
		# common simplified soft rules
		# soft totals: treat Ace as 11 where possible
		if total >= 19:
			return "stand"
		if total == 18:
			if 2 <= d <= 6:
				return "double"
			if d in (7, 8):
				return "stand"
			return "hit"
		if total <= 17:
			if 4 <= d <= 6:
				return "double"
			return "hit"

	# Hard hands
	# Simplified hard strategy table
	if total >= 17:
		return "stand"
	if 13 <= total <= 16:
		if 2 <= d <= 6:
			return "stand"
		else:
			return "hit"
	if total == 12:
		if 4 <= d <= 6:
			return "stand"
		else:
			return "hit"
	if total <= 11:
		# 11 or less: double on 10/11 commonly; simplified: double on 11,10 vs dealer low
		if total == 11:
			return "double"
		if total == 10 and d <= 9:
			return "double"
		if total == 9 and 3 <= d <= 6:
			return "double"
		return "hit"
#gemaakt door Robbe Lambrechts

