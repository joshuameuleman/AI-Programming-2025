# Gemaakt door Joshua Meuleman

"""Hi-Lo counting module.

Counting class that maintains a running count and a record of seen cards.
Uses Hi-Lo system: 2-6 => +1, 7-9 => 0, 10-A => -1.
"""
from typing import List, Dict, Any
import json

from ..hand import parse_card


class Counting:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._running = 0
        self.seen: List[Dict[str, Any]] = []

    def _hi_lo_value(self, rank: str) -> int:
        # ranks provided as strings like '2','10','A','K','Queen'
        if rank in ("2", "3", "4", "5", "6"):
            return 1
        if rank in ("7", "8", "9"):
            return 0
        # 10,J,Q,K,A -> -1
        return -1

    def update(self, card: Any) -> None:
        """Update running count with a card (dict or string supported)."""
        rank = parse_card(card)
        v = self._hi_lo_value(rank)
        self._running += v
        # store a compact record
        if isinstance(card, dict):
            self.seen.append({"rank": rank})
        else:
            self.seen.append({"rank": rank})

    def running_count(self) -> int:
        return self._running

    def true_count(self, remaining_decks_estimate: float) -> float:
        """Return true count = running_count / remaining_decks_estimate.

        remaining_decks_estimate should be > 0 (e.g., len(deck)/52).
        """
        if remaining_decks_estimate <= 0:
            return float(self._running)
        return self._running / remaining_decks_estimate

    def save(self, path: str) -> None:
        data = {"running": self._running, "seen": self.seen}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._running = int(data.get("running", 0))
        self.seen = data.get("seen", [])

    # Gemaakt door Joshua Meuleman
