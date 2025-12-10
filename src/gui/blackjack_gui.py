#gemaakt door Joshua Meuleman

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from src.game import Game
from src.dealer import Dealer
from src.hand import Hand, parse_card
from src.ai.npc import NPC
from src.gui.card import CardWidget
from src import deck


class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack AI")
        self.root.state("zoomed")  # fullscreen-like on Windows
        self.root.configure(bg="#1a1a1a")
        
        # Game state
        self.game = Game()
        self.game.start_shoe()
        self.dealer = Dealer()
        self.npc = NPC()
        self.npc.start_shoe(self.game.num_decks)
        deck.register_draw_observer(self.npc.observe_card)
        
        # Player state
        self.human_hand = None
        self.dealer_hand = None
        self.npc_hand = None
        self.human_bet = 0
        self.npc_bet = 0
        self.game_over = True
        self.human_money = 100
        self.npc_money = 100
        
        # Build UI
        self._build_ui()
        self._load_playmat()
        
    def _load_playmat(self):
        """Load playmat and prepare for responsive scaling."""
        playmat_path = os.path.join(
            os.path.dirname(__file__),
            "playmats",
            "black&gold.png"
        )

        self.playmat_original = None
        if os.path.exists(playmat_path):
            try:
                self.playmat_original = Image.open(playmat_path)
            except Exception as e:
                print(f"Error loading playmat: {e}")

        if self.playmat_original:
            self._resize_playmat(initial=True)
            # update image on canvas resize
            self.canvas.bind("<Configure>", self._resize_playmat)

    def _resize_playmat(self, event=None, initial=False):
        if not self.playmat_original:
            return
        # Determine target size from canvas
        if event is not None and not initial:
            w, h = event.width, event.height
        else:
            w = self.canvas.winfo_width() or self.playmat_original.width
            h = self.canvas.winfo_height() or self.playmat_original.height
        if w < 50 or h < 50:
            return
        try:
            img = self.playmat_original.resize((w, h), Image.Resampling.LANCZOS)
        except Exception:
            img = self.playmat_original
        self.playmat_photo = ImageTk.PhotoImage(img)
        if hasattr(self, "_playmat_image_id"):
            self.canvas.itemconfigure(self._playmat_image_id, image=self.playmat_photo)
        else:
            self._playmat_image_id = self.canvas.create_image(0, 0, image=self.playmat_photo, anchor="nw")
        # Reposition card zones relative to current canvas size to avoid clipping
        self._reposition_card_zones(w, h)

    def _reposition_card_zones(self, w, h):
        # Ratios based on original 1600x900 layout: dealer (0.5,0.13), player (0.375,1), npc (0.625,0.8)
        dealer_x, dealer_y = 0.5 * w, 0.13 * h
        player_x, player_y = 0.375 * w, 0.6 * h
        npc_x, npc_y = 0.625 * w, 0.6 * h
        if hasattr(self, "dealer_window"):
            self.canvas.coords(self.dealer_window, dealer_x, dealer_y)
        if hasattr(self, "player_window"):
            self.canvas.coords(self.player_window, player_x, player_y)
        if hasattr(self, "npc_window"):
            self.canvas.coords(self.npc_window, npc_x, npc_y)
    
    def _build_ui(self):
        """Build the main UI with canvas and card positions"""
        # Main canvas with playmat background
        self.canvas = tk.Canvas(
            self.root,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Card containers with labels
        self.dealer_container = tk.Frame(self.canvas, bg="#1a1a1a")
        dealer_label = tk.Label(self.dealer_container, text="Dealer", bg="#1a1a1a", fg="white", font=("Arial", 12, "bold"))
        dealer_label.pack()
        self.dealer_frame = tk.Frame(self.dealer_container, bg="#1a1a1a")
        self.dealer_frame.pack()
        self.dealer_window = self.canvas.create_window(800, 120, window=self.dealer_container, anchor="n")

        self.player_container = tk.Frame(self.canvas, bg="#1a1a1a")
        player_label = tk.Label(self.player_container, text="Jij", bg="#1a1a1a", fg="white", font=("Arial", 12, "bold"))
        player_label.pack()
        self.player_frame = tk.Frame(self.player_container, bg="#1a1a1a")
        self.player_frame.pack()
        self.player_window = self.canvas.create_window(600, 720, window=self.player_container, anchor="n")

        self.npc_container = tk.Frame(self.canvas, bg="#1a1a1a")
        npc_label = tk.Label(self.npc_container, text="AI", bg="#1a1a1a", fg="white", font=("Arial", 12, "bold"))
        npc_label.pack()
        self.npc_frame = tk.Frame(self.npc_container, bg="#1a1a1a")
        self.npc_frame.pack()
        self.npc_window = self.canvas.create_window(1000, 720, window=self.npc_container, anchor="n")

        # Bottom control panel below the playmat (outside canvas)
        bottom_panel = tk.Frame(self.root, bg="#111111")
        bottom_panel.pack(side=tk.BOTTOM, fill=tk.X)

        # Betting and info stacked center
        info_frame = tk.Frame(bottom_panel, bg="#1a1a1a")
        info_frame.pack(pady=4)
        bet_label = tk.Label(info_frame, text="Bedrag:", bg="#1a1a1a", fg="white", font=("Arial", 10))
        bet_label.pack(side=tk.LEFT, padx=6)
        self.bet_display = tk.Label(
            info_frame,
            text=f"Jouw inzet: €{self.human_bet} | NPC inzet: €{self.npc_bet}",
            bg="#1a1a1a",
            fg="#FFD700",
            font=("Arial", 12, "bold")
        )
        self.bet_display.pack(side=tk.LEFT, padx=6)

        money_frame = tk.Frame(bottom_panel, bg="#1a1a1a")
        money_frame.pack(pady=4)
        self.money_display = tk.Label(
            money_frame,
            text=f"Jouw geld: €{self.human_money} | NPC geld: €{self.npc_money}",
            bg="#1a1a1a",
            fg="#90EE90",
            font=("Arial", 11)
        )
        self.money_display.pack()

        bet_buttons_frame = tk.Frame(bottom_panel, bg="#1a1a1a")
        bet_buttons_frame.pack(pady=6)
        for amount in [1, 2, 5, 10, 20, 50]:
            btn = tk.Button(
                bet_buttons_frame,
                text=f"€{amount}",
                command=lambda a=amount: self.set_bet(a),
                bg="#4CAF50",
                fg="black",
                font=("Arial", 11, "bold"),
                width=6,
                height=1
            )
            btn.pack(side=tk.LEFT, padx=4)

        buttons_frame = tk.Frame(bottom_panel, bg="#1a1a1a")
        buttons_frame.pack(pady=8)

        self.new_round_btn = tk.Button(
            buttons_frame,
            text="Nieuwe Ronde",
            command=self.start_round,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 12, "bold"),
            width=12,
            height=1,
            state=tk.DISABLED
        )
        self.new_round_btn.pack(side=tk.LEFT, padx=6)

        self.hit_btn = tk.Button(
            buttons_frame,
            text="HIT",
            command=self.on_hit,
            bg="#2196F3",
            fg="black",
            font=("Arial", 12, "bold"),
            width=10,
            height=1,
            state=tk.DISABLED
        )
        self.hit_btn.pack(side=tk.LEFT, padx=6)

        self.stand_btn = tk.Button(
            buttons_frame,
            text="STAND",
            command=self.on_stand,
            bg="#FF9800",
            fg="black",
            font=("Arial", 12, "bold"),
            width=10,
            height=1,
            state=tk.DISABLED
        )
        self.stand_btn.pack(side=tk.LEFT, padx=6)

        self.double_btn = tk.Button(
            buttons_frame,
            text="DOUBLE",
            command=self.on_double,
            bg="#F44336",
            fg="black",
            font=("Arial", 12, "bold"),
            width=10,
            height=1,
            state=tk.DISABLED
        )
        self.double_btn.pack(side=tk.LEFT, padx=6)

        self.reveal_btn = tk.Button(
            buttons_frame,
            text="Toon Dealer",
            command=self.on_reveal_dealer,
            bg="#9C27B0",
            fg="black",
            font=("Arial", 12, "bold"),
            width=12,
            height=1,
            state=tk.DISABLED
        )
        self.reveal_btn.pack(side=tk.LEFT, padx=6)
    
    def set_bet(self, amount):
        """Set a fixed bet amount (not increment)"""
        if self.game_over:  # Only allow betting when no round is active
            self.human_bet = amount
            self.npc_bet = self.npc.recommended_bet()
            self._update_bet_display()
            # Auto-start the game after bet is placed
            self.start_round()
        else:
            messagebox.showwarning("Waarschuwing", "Er is al een spel bezig!")
    
    def _update_bet_display(self):
        """Update the bet display label"""
        self.bet_display.config(
            text=f"Jouw inzet: €{self.human_bet} | NPC inzet: €{self.npc_bet}"
        )
    
    def _update_money_display(self):
        """Update the money display label"""
        self.money_display.config(
            text=f"Jouw geld: €{self.human_money} | NPC geld: €{self.npc_money}"
        )
    
    def start_round(self):
        """Start a new round of blackjack"""
        if self.human_bet <= 0:
            messagebox.showwarning("Waarschuwing", "Zet eerst een bedrag in!")
            return
        
        if self.human_bet > self.human_money or self.npc_bet > self.npc_money:
            messagebox.showerror("Fout", "Onvoldoende geld!")
            self.human_bet = 0
            self.npc_bet = 0
            return
        
        # Reset game state
        self.game_over = False
        self.game = Game()
        self.game.start_shoe()
        self.npc.start_shoe(self.game.num_decks)
        deck.register_draw_observer(self.npc.observe_card)
        
        # Deduct bets
        self.human_money -= self.human_bet
        self.npc_money -= self.npc_bet
        self._update_money_display()
        
        # Deal initial cards
        self.human_hand = Hand()
        self.dealer_hand = Hand()
        self.npc_hand = Hand()
        
        for _ in range(2):
            c1 = deck.draw(self.game.shoe)
            c2 = deck.draw(self.game.shoe)
            c3 = deck.draw(self.game.shoe)
            self.human_hand.add(c1)
            self.dealer_hand.add(c2)
            self.npc_hand.add(c3)
        
        # Update UI
        self._refresh_board()
        
        # Enable action buttons
        self.hit_btn.config(state=tk.NORMAL)
        self.stand_btn.config(state=tk.NORMAL)
        self.double_btn.config(state=tk.NORMAL)
        self.new_round_btn.config(state=tk.DISABLED)
        
        # Check for blackjacks
        if self.human_hand.is_blackjack():
            self.on_stand()
        elif self.npc_hand.is_blackjack():
            self.on_stand()
    
    def on_hit(self):
        """Player hits"""
        if not self.game_over:
            c = deck.draw(self.game.shoe)
            self.human_hand.add(c)
            self._refresh_board()
            
            if self.human_hand.is_bust():
                self._finish_round_after_player()
    
    def on_stand(self):
        """Player stands"""
        if not self.game_over:
            self.hit_btn.config(state=tk.DISABLED)
            self.stand_btn.config(state=tk.DISABLED)
            self.double_btn.config(state=tk.DISABLED)
            self._finish_round()
    
    def on_double(self):
        """Player doubles down"""
        if not self.game_over and len(self.human_hand.cards) == 2:
            self.human_bet *= 2
            self.human_money -= self.human_bet // 2
            self._update_bet_display()
            self._update_money_display()
            
            c = deck.draw(self.game.shoe)
            self.human_hand.add(c)
            self._refresh_board()
            
            if self.human_hand.is_bust():
                self._finish_round_after_player()
            else:
                self.on_stand()
    
    def on_reveal_dealer(self):
        """Reveal dealer's hidden card and finish the round"""
        self.reveal_btn.config(state=tk.DISABLED)
        self._finish_round()
    
    def _finish_round_after_player(self):
        """Called when player is done (stand/bust)"""
        # Always reveal/finish immediately (dealer auto shown)
        self.hit_btn.config(state=tk.DISABLED)
        self.stand_btn.config(state=tk.DISABLED)
        self.double_btn.config(state=tk.DISABLED)
        self._finish_round()
    
    def _finish_round(self):
        """Finish the round: dealer plays, settle bets"""
        # Dealer plays out their hand
        while self.dealer_hand.best_value() < 17:
            c = deck.draw(self.game.shoe)
            self.dealer_hand.add(c)
        
        # NPC plays out their hand (simplified)
        while self.npc_hand.best_value() < 17:
            c = deck.draw(self.game.shoe)
            self.npc_hand.add(c)
        
        # Settle bets
        self._settle()
        
        # End of round
        self.game_over = True
        self.hit_btn.config(state=tk.DISABLED)
        self.stand_btn.config(state=tk.DISABLED)
        self.double_btn.config(state=tk.DISABLED)
        self.reveal_btn.config(state=tk.DISABLED)
        self.new_round_btn.config(state=tk.NORMAL)
        
        self._refresh_board()
    
    def _settle(self):
        """Settle all bets"""
        # Player vs Dealer
        player_value = self.human_hand.best_value()
        dealer_value = self.dealer_hand.best_value()
        
        if player_value > 21:
            # Player bust - loses bet (already deducted)
            pass
        elif dealer_value > 21:
            # Dealer bust - player wins
            if self.human_hand.is_blackjack():
                self.human_money += int(self.human_bet * 2.5)  # 3:2 payout (1 + 1.5)
            else:
                self.human_money += self.human_bet * 2
        elif player_value > dealer_value:
            # Player wins
            if self.human_hand.is_blackjack():
                self.human_money += int(self.human_bet * 2.5)  # 3:2 payout
            else:
                self.human_money += self.human_bet * 2
        elif player_value == dealer_value:
            # Push (tie)
            self.human_money += self.human_bet
        # else: dealer_value > player_value - player loses (already deducted)
        
        # NPC vs Dealer (simplified)
        npc_value = self.npc_hand.best_value()
        
        if npc_value > 21:
            pass
        elif dealer_value > 21:
            if self.npc_hand.is_blackjack():
                self.npc_money += int(self.npc_bet * 2.5)
            else:
                self.npc_money += self.npc_bet * 2
        elif npc_value > dealer_value:
            if self.npc_hand.is_blackjack():
                self.npc_money += int(self.npc_bet * 2.5)
            else:
                self.npc_money += self.npc_bet * 2
        elif npc_value == dealer_value:
            self.npc_money += self.npc_bet
        
        self._update_money_display()
    
    def _refresh_board(self):
        """Refresh all card displays"""
        # Clear existing cards
        for widget in self.dealer_frame.winfo_children():
            widget.destroy()
        for widget in self.player_frame.winfo_children():
            widget.destroy()
        for widget in self.npc_frame.winfo_children():
            widget.destroy()
        
        # Render cards
        self._render_cards(self.dealer_hand, self.dealer_frame)
        self._render_cards(self.human_hand, self.player_frame)
        self._render_cards(self.npc_hand, self.npc_frame)
    
    def _render_cards(self, hand, frame):
        """Render cards for a given hand in a frame"""
        if hand is None:
            return
        
        for card in hand.cards:
            card_widget = CardWidget(frame, card)
            card_widget.pack(side=tk.LEFT, padx=5)


def run_gui():
    """Run the Blackjack GUI"""
    root = tk.Tk()
    gui = BlackjackGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()

#gemaakt door Joshua Meuleman