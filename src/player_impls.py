"""
# Gemaakt door Joshua Meuleman

Concrete player implementations used by the CLI demo:
- HumanPlayer: interactive on CLI (bet, hit, stand, double, split (single)).
- NPCPlayer: adapter for existing `src.ai.npc.NPC`.

"""
from typing import Any, List, Optional
from .hand import Hand, parse_card
from .player import Player
from .ai.npc import NPC
from .ai.basic_strategy import choose_action


class HumanPlayer(Player):
    def __init__(self, id: str):
        super().__init__(id)
        self.hands: List[Hand] = []
        self.current_bets: List[int] = []
        self.bankroll: float = 100.0

    def start_round(self):
        self.hands = [Hand()]
        self.current_bets = [0]

    def get_bet(self) -> int:
        while True:
            try:
                v = input(f"Enter bet amount for {self.id} (min 1): ")
                bet = int(v.strip())
                if bet >= 1:
                    # ensure bankroll has enough
                    if bet > self.bankroll:
                        print("Insufficient bankroll, using full bankroll instead")
                        bet = int(self.bankroll)
                    self.current_bets[0] = bet
                    return bet
            except Exception:
                pass
            print("Invalid bet — enter integer >= 1")

    def receive_card(self, card: Any):
        rank = parse_card(card)
        # always append to the first hand if multiple hands exist during dealing
        if not self.hands:
            self.hands = [Hand()]
        self.hands[0].add(rank)

    def play_hand(self, dealer_upcard: Any, game: Any) -> str:
        dealer_rank = parse_card(dealer_upcard)
        # handle possible split decision if initial two cards same rank
        first_hand = self.hands[0]
        if len(first_hand.cards) == 2 and first_hand.cards[0] == first_hand.cards[1]:
            ans = input("You have a pair — split? (y/n): ")
            if ans.strip().lower().startswith("y"):
                # perform single split: create second hand
                card1 = first_hand.cards.pop()
                card2 = first_hand.cards.pop()
                h1 = Hand()
                h2 = Hand()
                h1.add(card1)
                h2.add(card2)
                self.hands = [h1, h2]
                # equal bet for second hand
                self.current_bets = [self.current_bets[0], self.current_bets[0]]

        # Play each hand sequentially
        results = []
        for idx, hand in enumerate(self.hands):
            while True:
                print(f"Hand {idx+1}: {hand.cards} (value={hand.best_value()})")
                if hand.is_bust():
                    print("Busted!")
                    results.append("bust")
                    break
                opts = ["hit", "stand", "double"]
                choice = input(f"Choose action for hand {idx+1} ({'/'.join(opts)}): ")
                c = choice.strip().lower()
                if c == "hit":
                    card = game.deal_card()
                    rank = parse_card(card)
                    hand.add(rank)
                    continue
                if c == "double":
                    # take one card then stop
                    card = game.deal_card()
                    rank = parse_card(card)
                    hand.add(rank)
                    # double the bet for this hand
                    try:
                        self.current_bets[idx] = int(self.current_bets[idx] * 2)
                    except Exception:
                        pass
                    results.append("double")
                    break
                if c == "stand":
                    results.append("stand")
                    break
                print("Unknown action")

        return ";".join(results)

    def settle(self, result: Any):
        # result expected: dict with hand-level results and net changes
        print(f"Settlement for {self.id}: {result}")
        net = result.get("net", 0) if isinstance(result, dict) else 0
        try:
            self.bankroll += float(net)
        except Exception:
            pass


class NPCPlayer(Player):
    def __init__(self, id: str, npc_agent: Optional[NPC] = None):
        super().__init__(id)
        self.npc = npc_agent or NPC()
        self.hands: List[Hand] = []
        self.current_bets: List[int] = []
        self.bankroll: float = 100.0

    def start_round(self):
        self.hands = [Hand()]
        self.current_bets = [0]

    def get_bet(self) -> int:
        b = self.npc.recommended_bet()
        # ensure not exceeding bankroll
        if b > self.bankroll:
            b = int(self.bankroll)
        self.current_bets[0] = int(b)
        return int(b)

    def receive_card(self, card: Any):
        rank = parse_card(card)
        if not self.hands:
            self.hands = [Hand()]
        self.hands[0].add(rank)

    def play_hand(self, dealer_upcard: Any, game: Any) -> str:
        # use NPC.choose_action repeatedly until stand/bust/double
        actions = []
        # play each hand and track actions
        for idx, hand in enumerate(self.hands):
            while True:
                action = self.npc.choose_action(hand, dealer_upcard)
                actions.append(action)
                if action == "hit":
                    card = game.deal_card()
                    rank = parse_card(card)
                    hand.add(rank)
                    if hand.is_bust():
                        break
                    continue
                if action == "double":
                    # double this hand's bet
                    try:
                        self.current_bets[idx] = int(self.current_bets[idx] * 2)
                    except Exception:
                        pass
                    card = game.deal_card()
                    rank = parse_card(card)
                    hand.add(rank)
                    break
                if action == "stand":
                    break
                break
        return ",".join(actions)

    def settle(self, result: Any):
        # result expected to be a dict that includes 'net'
        net = result.get("net", 0) if isinstance(result, dict) else 0
        try:
            self.bankroll += float(net)
        except Exception:
            pass


class BaselinePlayer(Player):
    """A non-counting baseline that uses basic strategy only and fixed bets.

    Useful for headless simulation and comparison against the counting NPC.
    """
    def __init__(self, id: str, fixed_bet: int = 1):
        super().__init__(id)
        self.hands: List[Hand] = []
        self.current_bets: List[int] = []
        self.bankroll: float = 100.0
        self.fixed_bet = int(fixed_bet)

    def start_round(self):
        self.hands = [Hand()]
        self.current_bets = [self.fixed_bet]

    def get_bet(self) -> int:
        # always bet fixed amount (or remaining bankroll)
        bet = min(int(self.fixed_bet), int(self.bankroll))
        self.current_bets = [bet]
        return bet

    def receive_card(self, card: Any):
        rank = parse_card(card)
        if not self.hands:
            self.hands = [Hand()]
        self.hands[0].add(rank)

    def play_hand(self, dealer_upcard: Any, game: Any) -> str:
        actions = []
        for idx, hand in enumerate(self.hands):
            while True:
                action = choose_action(hand.cards, dealer_upcard)
                actions.append(action)
                if action == "hit":
                    card = game.deal_card()
                    rank = parse_card(card)
                    hand.add(rank)
                    if hand.is_bust():
                        break
                    continue
                if action == "double":
                    try:
                        self.current_bets[idx] = int(self.current_bets[idx] * 2)
                    except Exception:
                        pass
                    card = game.deal_card()
                    rank = parse_card(card)
                    hand.add(rank)
                    break
                if action == "stand":
                    break
                break
        return ",".join(actions)

    def settle(self, result: Any):
        net = result.get("net", 0) if isinstance(result, dict) else 0
        try:
            self.bankroll += float(net)
        except Exception:
            pass


# Gemaakt door Joshua Meuleman
