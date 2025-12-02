"""
# Gemaakt door Joshua Meuleman

Dealer implementation with standard policy: hit until 17.

This dealer stores cards in a `Hand` and uses `game.deal_card()` for draws so
draw-observers (NPC) are notified.
"""
from typing import Any

from .hand import Hand, parse_card


class Dealer:
    def __init__(self, stand_on_soft_17: bool = True):
        self.hand = Hand()
        self.stand_on_soft_17 = stand_on_soft_17

    def receive_card(self, card: Any):
        # normalize and add rank
        r = parse_card(card)
        self.hand.add(r)

    def upcard(self):
        # return the first card (raw rank)
        return self.hand.cards[0] if self.hand.cards else None

    def is_blackjack(self) -> bool:
        return self.hand.is_blackjack()

    def best_value(self) -> int:
        return self.hand.best_value()

    def play(self, game: Any):
        # Dealer draws using game.deal_card() so observers are notified.
        # Hit until 17; soft 17 handling based on `stand_on_soft_17`.
        while True:
            total, usable = self.hand.values(), False
            # reuse Hand.value helper: compute total and usable
            from .hand import value as hand_value
            total_val, usable = hand_value(self.hand.cards)
            if total_val < 17:
                card = game.deal_card()
                self.receive_card(card)
                continue
            if total_val == 17 and not self.stand_on_soft_17 and usable:
                # hit on soft 17
                card = game.deal_card()
                self.receive_card(card)
                continue
            break


# Gemaakt door Joshua Meuleman
