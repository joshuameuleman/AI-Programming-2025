# Gemaakt door Joshua Meuleman
"""NPC (AI) module: combines counting and basic strategy into a single agent.

Deze `NPC` klasse onderhoudt eigen geheugen van geziene kaarten via de
`Counting` module, kent het aantal decks bij het starten van de shoe en
geeft deterministische bet‑sizing en actieadvies op basis van basic strategy.

Belangrijk: dit is volledig algorithmisch — er is géén machine learning.
"""
from typing import Any, Optional

from .counting import Counting
from .basic_strategy import choose_action


class NPC:
    """Deterministic NPC that uses Hi-Lo counting and basic strategy.

    Usage:
    - call `start_shoe(num_decks)` when a new shoe begins
    - call `observe_card(card)` for every card that becomes visible
    - call `recommended_bet()` or `running_count()/true_count()` to inspect
    - call `choose_action(player_hand, dealer_upcard)` for an action
    """

    def __init__(self, bet_unit: int = 1, deviations: Optional[dict] = None):
        self.counting = Counting()
        self.bet_unit = int(bet_unit)
        self.deviations = deviations or {}
        self.original_deck_cards: Optional[int] = None

    def start_shoe(self, num_decks: int) -> None:
        """Initialize shoe size (number of decks) and reset memory."""
        self.original_deck_cards = int(num_decks) * 52
        self.counting.reset()

    def observe_card(self, card: Any) -> None:
        """Record a seen card into internal counting memory."""
        self.counting.update(card)

    def remaining_decks_estimate(self) -> float:
        """Estimate remaining decks from original shoe size and seen cards.

        Returns a float >= 0.1 to avoid division by zero in true count.
        """
        if not self.original_deck_cards:
            return 1.0
        seen = len(self.counting.seen)
        remaining_cards = max(0, self.original_deck_cards - seen)
        return max(0.1, remaining_cards / 52.0)

    def running_count(self) -> int:
        return self.counting.running_count()

    def true_count(self) -> float:
        return self.counting.true_count(self.remaining_decks_estimate())

    def recommended_bet(self) -> int:
        """Simple deterministic bet sizing based on true count.

        - TC <= 1 : 1 unit
        - 1 < TC < 3 : 2 units
        - TC >= 3 : 4 units
        """
        tc = self.true_count()
        if tc <= 1:
            return self.bet_unit
        if 1 < tc < 3:
            return self.bet_unit * 2
        return self.bet_unit * 4

    def choose_action(self, player_hand: Any, dealer_upcard: Any) -> str:
        """Return basic strategy action. `true_count` available for deviations later."""
        return choose_action(player_hand, dealer_upcard)

# Gemaakt door Joshua Meuleman
