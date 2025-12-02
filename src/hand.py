"""
# Gemaakt door Joshua Meuleman

Minimal `Hand` representation for Blackjack. Provides value calculation with Aces.

"""
from typing import List, Tuple


class Hand:
    def __init__(self):
        self.cards: List[str] = []

    def add(self, card: str):
        self.cards.append(card)

    def values(self) -> List[int]:
        """Return all possible hand values considering Aces as 1 or 11."""
        values = [0]
        for c in self.cards:
            if c in ("J", "Q", "K"):
                add = 10
            elif c == "A":
                # Ace as 1 or 11
                new = []
                for v in values:
                    new.append(v + 1)
                    new.append(v + 11)
                values = new
                continue
            else:
                add = int(c)
            values = [v + add for v in values]
        return sorted(set(values))

    def best_value(self) -> int:
        vals = [v for v in self.values() if v <= 21]
        if vals:
            return max(vals)
        return min(self.values()) if self.values() else 0

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.best_value() == 21

    def is_bust(self) -> bool:
        return all(v > 21 for v in self.values())


# Utility: parse card dict or string into normalized rank
def parse_card(card) -> str:
    """Normalize a card (dict with 'rank' or a rank string) to short rank.

    Examples:
    - {'rank':'Jack'} -> 'J'
    - {'rank':'10'} -> '10'
    - 'Ace' -> 'A'
    - 'K' -> 'K'
    """
    if isinstance(card, dict):
        rank = card.get("rank")
    else:
        rank = card
    if not isinstance(rank, str):
        rank = str(rank)
    rank = rank.strip()
    mapping = {
        "Jack": "J",
        "Queen": "Q",
        "King": "K",
        "Ace": "A",
        "J": "J",
        "Q": "Q",
        "K": "K",
        "A": "A",
    }
    # numeric ranks like '2','10' should pass through
    return mapping.get(rank, rank)


# Gemaakt door Joshua Meuleman


def card_value(rank: str) -> int:
    """Return numeric card value for comparisons (Ace counted as 11)."""
    r = parse_card(rank)
    if r == "A":
        return 11
    if r in ("J", "Q", "K"):
        return 10
    try:
        return int(r)
    except Exception:
        return 0


def value(cards) -> Tuple[int, bool]:
    """Compute total and whether hand is soft (usable ace).

    cards: list of card dicts or strings
    Returns: (total, usable_ace)
    """
    ranks = [parse_card(c) for c in cards]
    total = 0
    aces = 0
    for r in ranks:
        if r == "A":
            aces += 1
            total += 1
        elif r in ("J", "Q", "K"):
            total += 10
        else:
            try:
                total += int(r)
            except Exception:
                total += 0
    usable = False
    # upgrade one ace from 1 to 11 if it doesn't bust
    if aces and total + 10 <= 21:
        total += 10
        usable = True
    return total, usable


def is_pair(cards) -> bool:
    if not cards or len(cards) < 2:
        return False
    return parse_card(cards[0]) == parse_card(cards[1])
