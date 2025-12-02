"""
# Gemaakt door Joshua Meuleman

Player base class and simple Human/NPC adapters. Concrete behavior implemented elsewhere.

"""
from typing import Any


class Player:
    def __init__(self, id: str):
        self.id = id

    def start_round(self):
        raise NotImplementedError()

    def get_bet(self) -> int:
        raise NotImplementedError()

    def play_hand(self, dealer_upcard: Any, game: Any) -> str:
        raise NotImplementedError()

    def receive_card(self, card: Any):
        raise NotImplementedError()

    def settle(self, result: Any):
        raise NotImplementedError()


# Gemaakt door Joshua Meuleman
