"""
Interactieve Blackjack GUI met tkinter.

- Hergebruikt bestaande game-logica (Deck, Dealer, Hand, NPC counting).
- Toont luxe kaartafbeeldingen uit `src/gui/full_art_luxe_kaarten` (fallback naar tekst als niet beschikbaar).
- Ondersteunt hit/stand/double voor één hand per speler (geen split/insurance).

Start vanuit project-root:
    python -m src.gui.blackjack_gui
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any

from src.game import Game
from src.dealer import Dealer
from src.hand import Hand, parse_card, value
from src.ai.npc import NPC
from src import deck
from .card import CardWidget


class BlackjackGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack GUI")
        try:
            # windowed fullscreen (maximized window)
            self.state("zoomed")
        except Exception:
            self.geometry("1280x800")

        # Core game state
        self.game = Game()
        self.dealer: Dealer = Dealer()
        self.npc = NPC()
        self.human_hand = Hand()
        self.npc_hand = Hand()
        self.dealer_cards_raw: List[Dict[str, Any]] = []
        self.human_cards_raw: List[Dict[str, Any]] = []
        self.npc_cards_raw: List[Dict[str, Any]] = []
        self.round_active = False
        self.player_done = False

        # Bankroll / bets
        self.human_bankroll = 100.0
        self.npc_bankroll = 100.0
        self.human_bet = float(self.game.min_bet)
        self.npc_bet = float(self.game.min_bet)

        # register NPC observer once
        deck.register_draw_observer(self.npc.observe_card)
        self.npc.start_shoe(self.game.num_decks)
        self.game.start_shoe()

        self._build_ui()
        self._update_status()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # UI helpers
    def _build_ui(self):
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Segoe UI", 11))
        self.style.configure("TLabel", font=("Segoe UI", 11))

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=6)

        self.status_var = tk.StringVar(value="Welkom! Druk op 'Nieuwe ronde'.")
        ttk.Label(top, textvariable=self.status_var).pack(side="left")

        # Dealer area
        dealer_frame = ttk.LabelFrame(self, text="Dealer")
        dealer_frame.pack(fill="x", padx=10, pady=6)
        self.dealer_cards_frame = ttk.Frame(dealer_frame)
        self.dealer_cards_frame.pack(fill="x", padx=6, pady=4)

        # Player area
        player_frame = ttk.LabelFrame(self, text="Jij")
        player_frame.pack(fill="x", padx=10, pady=6)
        info_row = ttk.Frame(player_frame)
        info_row.pack(fill="x", padx=6, pady=2)
        self.bankroll_var = tk.StringVar()
        ttk.Label(info_row, textvariable=self.bankroll_var).pack(side="left")
        ttk.Label(info_row, text="Inzet:").pack(side="left", padx=(10, 2))
        self.bet_var = tk.StringVar(value=str(int(self.game.min_bet)))
        self.bet_entry = ttk.Entry(info_row, textvariable=self.bet_var, width=7)
        self.bet_entry.pack(side="left")

        self.player_cards_frame = ttk.Frame(player_frame)
        self.player_cards_frame.pack(fill="x", padx=6, pady=4)

        # NPC area (kaarten verborgen tot speler klaar is)
        npc_frame = ttk.LabelFrame(self, text="NPC")
        npc_frame.pack(fill="x", padx=10, pady=6)
        self.npc_cards_frame = ttk.Frame(npc_frame)
        self.npc_cards_frame.pack(fill="x", padx=6, pady=4)

        # Controls
        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=10, pady=8)

        self.new_round_btn = ttk.Button(controls, text="Nieuwe ronde", command=self.start_round)
        self.new_round_btn.pack(side="left")

        self.hit_btn = ttk.Button(controls, text="Hit", command=self.on_hit, state="disabled")
        self.hit_btn.pack(side="left", padx=4)
        self.stand_btn = ttk.Button(controls, text="Stand", command=self.on_stand, state="disabled")
        self.stand_btn.pack(side="left", padx=4)
        self.double_btn = ttk.Button(controls, text="Double", command=self.on_double, state="disabled")
        self.double_btn.pack(side="left", padx=4)

        self.reveal_btn = ttk.Button(controls, text="Toon dealer", command=self._reveal, state="disabled")
        self.reveal_btn.pack(side="left", padx=(20, 4))

    def _clear_cards(self):
        for f in (self.dealer_cards_frame, self.player_cards_frame, self.npc_cards_frame):
            for child in f.winfo_children():
                child.destroy()

    def _render_cards(self, frame, cards: List[Dict[str, Any]], hide_second: bool = False):
        for idx, card in enumerate(cards):
            hidden = hide_second and idx == 1
            CardWidget(frame, card, hidden=hidden).pack(side="left", padx=3)

    def _update_status(self):
        self.bankroll_var.set(f"Bankroll: {self.human_bankroll:.1f}")

    def _set_buttons(self, active: bool):
        state = "normal" if active else "disabled"
        self.hit_btn.config(state=state)
        self.stand_btn.config(state=state)
        self.double_btn.config(state=state)
        self.reveal_btn.config(state="normal" if not active else "disabled")

    def start_round(self):
        if self.round_active:
            return
        if self.human_bankroll < self.game.min_bet:
            messagebox.showinfo("Einde", "Bankroll is leeg.")
            return

        # reshuffle if needed
        if self.game.should_reshuffle():
            self.game.start_shoe()
            self.npc.start_shoe(self.game.num_decks)
            self.status_var.set("Nieuwe shoe geschud.")

        # reset per-round state
        self.player_done = False
        self.round_active = True
        self.human_hand = Hand()
        self.npc_hand = Hand()
        self.dealer = Dealer()
        self.dealer_cards_raw = []
        self.human_cards_raw = []
        self.npc_cards_raw = []

        try:
            bet_val = int(self.bet_var.get())
        except Exception:
            bet_val = self.game.min_bet
        bet_val = max(self.game.min_bet, bet_val)
        bet_val = min(int(self.human_bankroll), bet_val)
        if bet_val <= 0:
            bet_val = self.game.min_bet
        self.human_bet = float(bet_val)

        # npc bet
        npc_bet = max(self.game.min_bet, int(self.npc.recommended_bet()))
        npc_bet = min(int(self.npc_bankroll), npc_bet)
        self.npc_bet = float(npc_bet)
        self.show_npc_cards = True

        # deal initial cards
        for _ in range(2):
            self._deal_to("human")
            self._deal_to("npc")
            self._deal_to("dealer")

        self.status_var.set("Kies je actie: hit/stand/double.")
        self._set_buttons(True)
        self._refresh_board(hide_dealer_hole=True)
        self._update_status()

        if self.human_hand.is_blackjack():
            self.status_var.set("Blackjack! Wacht op dealer.")
            self.player_done = True
            self.after(200, self._finish_round_after_player)

    def _deal_to(self, who: str):
        card = self.game.deal_card()
        rank = parse_card(card)
        if who == "human":
            self.human_cards_raw.append(card)
            self.human_hand.add(rank)
        elif who == "npc":
            self.npc_cards_raw.append(card)
            self.npc_hand.add(rank)
        else:
            self.dealer_cards_raw.append(card)
            self.dealer.receive_card(card)
        return card

    def on_hit(self):
        if not self.round_active or self.player_done:
            return
        self._deal_to("human")
        self._refresh_board(hide_dealer_hole=True)
        if self.human_hand.is_bust():
            self.status_var.set("Busted! Dealer speelt af.")
            self.player_done = True
            self.after(200, self._finish_round_after_player)

    def on_stand(self):
        if not self.round_active or self.player_done:
            return
        self.player_done = True
        self.status_var.set("Speler staat. NPC en dealer spelen.")
        self._finish_round_after_player()

    def on_double(self):
        if not self.round_active or self.player_done:
            return
        if len(self.human_hand.cards) != 2:
            return
        if self.human_bankroll < self.human_bet * 2:
            messagebox.showinfo("Niet genoeg bankroll", "Onvoldoende bankroll om te verdubbelen.")
            return
        self.human_bet *= 2
        self._deal_to("human")
        self._refresh_board(hide_dealer_hole=True)
        self.player_done = True
        self.status_var.set("Double uitgevoerd. NPC en dealer spelen.")
        self.after(200, self._finish_round_after_player)

    def _npc_turn(self):
        dealer_upcard = self.dealer_cards_raw[0] if self.dealer_cards_raw else None
        actions = []
        while True:
            action = self.npc.choose_action(self.npc_hand.cards, dealer_upcard)
            actions.append(action)
            if action == "hit":
                self._deal_to("npc")
                if self.npc_hand.is_bust():
                    break
                continue
            if action == "double":
                self.npc_bet = min(self.npc_bet * 2, self.npc_bankroll)
                self._deal_to("npc")
                break
            break
        return ",".join(actions)

    def _dealer_turn(self):
        while True:
            total, usable = value(self.dealer.hand.cards)
            if total < 17:
                self._deal_to("dealer")
                continue
            if total == 17 and not self.dealer.stand_on_soft_17 and usable:
                self._deal_to("dealer")
                continue
            break

    def _finish_round_after_player(self):
        if not self.round_active:
            return
        npc_actions = self._npc_turn()
        self.status_var.set(f"NPC: {npc_actions or 'stand'}. Dealer speelt...")
        self._dealer_turn()
        self._settle()
        self._refresh_board(hide_dealer_hole=False)
        self._set_buttons(False)
        self.round_active = False

    def _settle_hand(self, hand: Hand, bet: float, dealer_blackjack: bool, dealer_value: int) -> float:
        hand_blackjack = hand.is_blackjack()
        hand_bust = hand.is_bust()
        if hand_blackjack and not dealer_blackjack:
            return 1.5 * bet
        if hand_bust:
            return -bet
        if dealer_blackjack and hand_blackjack:
            return 0.0
        if dealer_blackjack and not hand_blackjack:
            return -bet
        if dealer_value > 21:
            return bet
        player_total = hand.best_value()
        if player_total > dealer_value:
            return bet
        if player_total == dealer_value:
            return 0.0
        return -bet

    def _settle(self):
        dealer_blackjack = self.dealer.is_blackjack()
        dealer_value = self.dealer.best_value()

        player_net = self._settle_hand(self.human_hand, self.human_bet, dealer_blackjack, dealer_value)
        npc_net = self._settle_hand(self.npc_hand, self.npc_bet, dealer_blackjack, dealer_value)

        self.human_bankroll += player_net
        self.npc_bankroll += npc_net

        summary = f"Jij: {player_net:+.1f} | Dealer={dealer_value}"
        self.status_var.set(summary)
        self._update_status()

    def _refresh_board(self, hide_dealer_hole: bool):
        self._clear_cards()
        self._render_cards(self.dealer_cards_frame, self.dealer_cards_raw, hide_second=hide_dealer_hole)
        self._render_cards(self.player_cards_frame, self.human_cards_raw, hide_second=False)
        self._render_cards(self.npc_cards_frame, self.npc_cards_raw, hide_second=False)

    def _reveal(self):
        if self.round_active:
            return
        self._refresh_board(hide_dealer_hole=False)

    def _on_close(self):
        try:
            deck.unregister_draw_observer(self.npc.observe_card)
        except Exception:
            pass
        self.destroy()


def main():
    app = BlackjackGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
