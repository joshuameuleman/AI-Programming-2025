"""
# Gemaakt door Joshua Meuleman

Core game loop and orchestration for Blackjack.

This module exposes a simple `Game` class that manages a shoe, players and the dealer.
Designed to be testable and to emit card draws via the existing `src.deck` draw-observer API.

"""
from typing import List, Dict, Any
from src import deck as _deck
from src.dealer import Dealer
from src.hand import parse_card


class Game:
    def __init__(self, num_decks: int = 6, min_bet: int = 1, reshuffle_at_percent: float = 0.25):
        self.num_decks = num_decks
        self.min_bet = min_bet
        self.reshuffle_at_percent = reshuffle_at_percent
        self.shoe = None
        self.dealer = None

    def start_shoe(self):
        """Initialize and shuffle the shoe. Notify AI/NPC to start shoe."""
        self.shoe = _deck.create_deck(self.num_decks)
        _deck.shuffle(self.shoe)

    def deal_card(self):
        """Draw a card from the shoe using src.deck.draw()."""
        return _deck.draw(self.shoe)

    def should_reshuffle(self) -> bool:
        """Simple placeholder: reshuffle when remaining cards percentage below threshold."""
        if not self.shoe:
            return True
        remaining = len(self.shoe)
        initial = 52 * self.num_decks
        pct = remaining / float(initial)
        return pct <= self.reshuffle_at_percent

    def play_round(self, players: List[Any]) -> Dict[str, Any]:
        """Play a single round: deal, let players act, dealer acts, settle.

        This is a minimal, synchronous loop intended for unit testing and CLI demos.
        """
        if self.should_reshuffle():
            self.start_shoe()

        summary = {p.id: None for p in players}

        # Start round and ask bets first
        for p in players:
            p.start_round()
            # ask for bet and record it on the player (players expected to set current_bets[0])
            try:
                bet = p.get_bet()
            except Exception:
                bet = 1
            # ensure current_bets present
            try:
                if not hasattr(p, 'current_bets') or not p.current_bets:
                    p.current_bets = [int(bet)]
            except Exception:
                p.current_bets = [int(bet)]

        # Deal two cards to each player and dealer
        for _ in range(2):
            for p in players:
                p.receive_card(self.deal_card())
            # dealer card
            if not self.dealer:
                self.dealer = Dealer()
            self.dealer.receive_card(self.deal_card())

        dealer_upcard = self.dealer.upcard()

        # Players act
        for p in players:
            action = p.play_hand(dealer_upcard, self)
            summary[p.id] = {"action": action}

        # Dealer plays
        self.dealer.play(self)

        # Settlement
        dealer_blackjack = self.dealer.is_blackjack()
        dealer_value = self.dealer.best_value()

        results = {}
        for p in players:
            # compute per-hand settlement
            net_total = 0.0
            per_hand = []
            hands = getattr(p, 'hands', [])
            bets = getattr(p, 'current_bets', [])
            for idx, hand in enumerate(hands):
                bet = bets[idx] if idx < len(bets) else (bets[0] if bets else 1)
                hand_blackjack = hand.is_blackjack()
                hand_bust = hand.is_bust()
                if hand_blackjack and not dealer_blackjack:
                    net = 1.5 * bet
                    outcome = 'blackjack'
                elif hand_bust:
                    net = -bet
                    outcome = 'bust'
                elif dealer_blackjack and hand_blackjack:
                    net = 0.0
                    outcome = 'push'
                elif dealer_blackjack and not hand_blackjack:
                    net = -bet
                    outcome = 'dealer_blackjack'
                else:
                    # normal compare
                    if dealer_value > 21:
                        net = bet
                        outcome = 'dealer_bust_win'
                    else:
                        player_total = hand.best_value()
                        if player_total > dealer_value:
                            net = bet
                            outcome = 'win'
                        elif player_total == dealer_value:
                            net = 0.0
                            outcome = 'push'
                        else:
                            net = -bet
                            outcome = 'lose'
                net_total += net
                per_hand.append({"bet": bet, "outcome": outcome, "net": net})

            # apply net to player's bankroll if present
            try:
                if hasattr(p, 'bankroll'):
                    p.bankroll += float(net_total)
            except Exception:
                pass

            # notify player
            try:
                p.settle({"per_hand": per_hand, "net": net_total, "dealer_value": dealer_value})
            except Exception:
                pass
            results[p.id] = {"per_hand": per_hand, "net": net_total}

        return results


class _DealerPlaceholder:
    """Lightweight dealer placeholder to hold cards until a full Dealer is implemented."""
    def __init__(self):
        self.cards = []

    def receive_card(self, card):
        self.cards.append(card)

    def upcard(self):
        return self.cards[0] if self.cards else None

    def play(self, game: Game):
        # Placeholder: dealer logic will be implemented in src/dealer.py
        return


# Gemaakt door Joshua Meuleman
