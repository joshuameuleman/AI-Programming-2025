#gemaakt door Joshua Meuleman


"""Hand utilities voor Blackjack.

Bevat functies om kaartranks te parsen, handwaarde te berekenen
en veelvoorkomende helpers zoals is_blackjack en is_bust.
"""
from typing import List, Tuple


def parse_card(card: str) -> str:
    """Return het rank-gedeelte van een kaart-string of dict.

    Ondersteunt twee vormen die we in deze repo kunnen gebruiken:
    - dict met keys 'rank' en 'suit' (bijv. {'rank':'A','suit':'Hearts'})
    - string zoals 'A♠' of '10♥' (in dat geval return alles behalve het laatste teken)
    """
    if isinstance(card, dict):
        return card.get('rank')
    if isinstance(card, str):
        # als kaart als "10" gevolgd door suit kan de rank meerdere tekens zijn
        # hier gaan we ervanuit dat suit één teken is (zoals '♠' of een woord-suit kan voorkomen)
        # als suit een woord is (bijv. 'Hearts') dan is de input vaak een dict; fallback hieronder
        if len(card) <= 2:
            return card[:-1] if len(card) > 1 else card
        # fallback: probeer splitsen op space of ' of '
        if ' of ' in card:
            return card.split(' of ')[0]
        return card[:-1]
    raise TypeError("Unsupported card type: expected dict or str")


def card_value(rank: str) -> int:
    """Geef de minimale waarde van een rank terug (A = 1, J/Q/K = 10)."""
    if rank is None:
        raise ValueError("rank is None")
    r = str(rank)
    if r in ("J", "Q", "K", "Jack", "Queen", "King"):
        return 10
    if r in ("A", "Ace"):
        return 1
    return int(r)


def value(hand: List[object]) -> Tuple[int, bool]:
    """Bereken de beste waarde voor een hand en of er een usable ace is.

    Retourneert (best_value, usable_ace_bool).
    Usable ace betekent dat één ace als 11 gebruikt wordt zonder te busten.
    """
    ranks = [parse_card(c) for c in hand]
    total = 0
    aces = 0
    for r in ranks:
        v = card_value(r)
        total += v
        if str(r) in ("A", "Ace"):
            aces += 1

    usable_ace = False
    # Probeer één ace als 11 te tellen (extra +10) indien mogelijk
    if aces > 0 and total + 10 <= 21:
        total += 10
        usable_ace = True

    return total, usable_ace


def is_blackjack(hand: List[object]) -> bool:
    v, _ = value(hand)
    return len(hand) == 2 and v == 21


def is_bust(hand: List[object]) -> bool:
    v, _ = value(hand)
    return v > 21


def is_soft(hand: List[object]) -> bool:
    """Return True als hand een usable ace heeft (soft hand)."""
    _, usable = value(hand)
    return usable


def is_pair(hand: List[object]) -> bool:
    """Return True als de hand uit precies twee kaarten bestaat met gelijke rank.

    Voor 10-waardes (10, J, Q, K) worden deze als gelijk behandeld.
    Ondersteunt kaart als dict {'rank','suit'} of string.
    """
    if len(hand) != 2:
        return False
    r1 = parse_card(hand[0])
    r2 = parse_card(hand[1])
    ten_set = {"10", "J", "Q", "K", "Jack", "Queen", "King"}
    if r1 in ten_set and r2 in ten_set:
        return True
    return r1 == r2
#gemaakt door Joshua Meuleman