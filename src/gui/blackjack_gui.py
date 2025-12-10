#gemaakt door Joshua Meuleman

import tkinter as tk
from tkinter import messagebox, simpledialog
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
        # Ask once for number of decks before first play
        try:
            decks = simpledialog.askinteger(
                "Aantal decks",
                "Hoeveel decks wil je gebruiken?",
                parent=self.root,
                minvalue=1,
                maxvalue=12,
                initialvalue=self.game.num_decks,
            )
            if decks is None:
                decks = self.game.num_decks
            self.game.num_decks = int(decks)
        except Exception:
            # fallback to default if dialog fails
            pass

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
        # Ask the player which playmat to use, then load it
        try:
            self._choose_playmat()
        except Exception:
            # if chooser fails, continue with default
            self.playmat_choice = None
        self._load_playmat()
        
    def _load_playmat(self):
        """Load playmat and prepare for responsive scaling."""
        playmats_dir = os.path.join(os.path.dirname(__file__), "playmats")
        # If a playmat was chosen use that, otherwise fall back to default
        if hasattr(self, 'playmat_choice') and self.playmat_choice:
            playmat_path = os.path.join(playmats_dir, self.playmat_choice)
        else:
            playmat_path = os.path.join(playmats_dir, "black&gold.png")

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

    def _choose_playmat(self):
        """Show a modal dialog listing available playmat images and let the user choose one.

        Displays a thumbnail preview that updates when the selection changes.
        """
        playmats_dir = os.path.join(os.path.dirname(__file__), "playmats")
        try:
            files = [f for f in os.listdir(playmats_dir) if os.path.isfile(os.path.join(playmats_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        except Exception:
            files = []

        if not files:
            self.playmat_choice = None
            return

        # If there's only one, choose it silently
        if len(files) == 1:
            self.playmat_choice = files[0]
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Kies playmat")
        dlg.transient(self.root)
        dlg.grab_set()

        container = tk.Frame(dlg)
        container.pack(padx=12, pady=12)

        list_frame = tk.Frame(container)
        list_frame.pack(side=tk.LEFT, fill=tk.Y)

        lbl = tk.Label(list_frame, text="Kies een playmat:", font=("Arial", 12))
        lbl.pack(anchor="w")

        listbox = tk.Listbox(list_frame, height=min(10, len(files)), selectmode=tk.SINGLE)
        for f in files:
            listbox.insert(tk.END, f)
        listbox.pack(padx=(0, 12), pady=6)
        listbox.select_set(0)

        # Preview area
        preview_frame = tk.Frame(container, bd=1, relief=tk.SUNKEN, width=320, height=200)
        preview_frame.pack(side=tk.LEFT, padx=(6, 0))
        preview_frame.pack_propagate(False)
        preview_label = tk.Label(preview_frame)
        preview_label.pack(expand=True)

        # Helper to load and show thumbnail
        def show_preview_for(index):
            try:
                fname = files[index]
                path = os.path.join(playmats_dir, fname)
                img = Image.open(path)
                # Resize preserving aspect ratio to fit preview size
                max_w, max_h = 320 - 8, 200 - 8
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                # store reference on dialog to avoid GC
                dlg._preview_photo = photo
                preview_label.config(image=photo)
            except Exception:
                preview_label.config(image='')

        # Initial preview
        show_preview_for(0)

        # Update preview when selection changes
        def on_select(evt):
            sel = listbox.curselection()
            if not sel:
                return
            show_preview_for(sel[0])

        listbox.bind('<<ListboxSelect>>', on_select)

        btn_frame = tk.Frame(dlg)
        btn_frame.pack(pady=(6, 6))

        def _on_ok():
            sel = listbox.curselection()
            if sel:
                self.playmat_choice = files[sel[0]]
            else:
                self.playmat_choice = files[0]
            dlg.destroy()

        def _on_cancel():
            self.playmat_choice = None
            dlg.destroy()

        ok_btn = tk.Button(btn_frame, text="OK", width=10, command=_on_ok)
        ok_btn.pack(side=tk.LEFT, padx=6)
        cancel_btn = tk.Button(btn_frame, text="Annuleer", width=10, command=_on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=6)

        # Center dialog over root
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (dlg.winfo_reqwidth() // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (dlg.winfo_reqheight() // 2)
        try:
            dlg.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self.root.wait_window(dlg)

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
        # Placeholder for player's bet chip image (shown when player clicks a chip)
        self.player_bet_label = tk.Label(self.player_container, bg="#1a1a1a")
        self.player_bet_label.pack(pady=(6, 0))
        self.player_window = self.canvas.create_window(600, 720, window=self.player_container, anchor="n")

        self.npc_container = tk.Frame(self.canvas, bg="#1a1a1a")
        npc_label = tk.Label(self.npc_container, text="AI", bg="#1a1a1a", fg="white", font=("Arial", 12, "bold"))
        npc_label.pack()
        self.npc_frame = tk.Frame(self.npc_container, bg="#1a1a1a")
        self.npc_frame.pack()
        # Placeholder for NPC's bet chip image
        self.npc_bet_label = tk.Label(self.npc_container, bg="#1a1a1a")
        self.npc_bet_label.pack(pady=(6, 0))
        self.npc_window = self.canvas.create_window(1000, 720, window=self.npc_container, anchor="n")

        # Bottom control panel below the playmat (outside canvas)
        bottom_panel = tk.Frame(self.root, bg="#111111")
        bottom_panel.pack(side=tk.BOTTOM, fill=tk.X)

        # Result banner (replaces modal popup) - initially hidden
        self.result_banner = tk.Label(
            bottom_panel,
            text="",
            bg="#111111",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=6
        )
        self.result_banner.pack(side=tk.TOP, fill=tk.X)

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
        self.chip_images = {}
        chip_defs = [1, 2, 5, 10, 20, 50]
        for amount in chip_defs:
            chip_path = os.path.join(os.path.dirname(__file__), "chips", f"{amount}_Euro.png")
            img = None
            if os.path.isfile(chip_path):
                try:
                    chip_img = Image.open(chip_path).resize((60, 60), Image.Resampling.LANCZOS)
                    img = ImageTk.PhotoImage(chip_img)
                    self.chip_images[amount] = img
                except Exception:
                    img = None
            if img:
                btn = tk.Button(
                    bet_buttons_frame,
                    image=img,
                    command=lambda a=amount: self.set_bet(a),
                    bg="#1a1a1a",
                    activebackground="#1a1a1a",
                    bd=0,
                    highlightthickness=0,
                    width=60,
                    height=60
                )
            else:
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
            btn.pack(side=tk.LEFT, padx=6)

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

        # Reveal button removed per user request; not created
    
    def set_bet(self, amount):
        """Set a fixed bet amount (not increment)"""
        if self.game_over:  # Only allow betting when no round is active
            self.human_bet = amount
            self.npc_bet = self.npc.recommended_bet()
            self._update_bet_display()
            # Show chip images for player and NPC bets
            try:
                self._show_bet_chips(self.human_bet, self.npc_bet)
            except Exception:
                pass
            # Auto-start the game after bet is placed
            self.start_round()
        else:
            messagebox.showwarning("Waarschuwing", "Er is al een spel bezig!")

    def _show_bet_chips(self, human_amount, npc_amount):
        """Display chip images (or text) next to player and NPC based on bet amounts."""
        # Player chip
        img = self.chip_images.get(human_amount)
        if img:
            self.player_bet_label.config(image=img, text='')
            self.player_bet_label._img = img
        else:
            self.player_bet_label.config(image='', text=f"€{human_amount}", fg="#FFD700", font=("Arial", 10, "bold"))

        # NPC chip
        img2 = self.chip_images.get(npc_amount)
        if img2:
            self.npc_bet_label.config(image=img2, text='')
            self.npc_bet_label._img = img2
        else:
            self.npc_bet_label.config(image='', text=f"€{npc_amount}", fg="#FFD700", font=("Arial", 10, "bold"))

    def _clear_bet_chips(self):
        """Clear displayed bet chips."""
        try:
            self.player_bet_label.config(image='', text='')
            if hasattr(self.player_bet_label, '_img'):
                delattr(self.player_bet_label, '_img')
        except Exception:
            pass
        try:
            self.npc_bet_label.config(image='', text='')
            if hasattr(self.npc_bet_label, '_img'):
                delattr(self.npc_bet_label, '_img')
        except Exception:
            pass
    
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
        # reveal button removed — dealer will be revealed automatically when round finishes
        
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
    
    # Reveal button removed; dealer reveals when round finishes
    
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

        # Show result pop-up summarizing human and AI outcome
        try:
            player_value = self.human_hand.best_value()
            dealer_value = self.dealer_hand.best_value()
            npc_value = self.npc_hand.best_value()

            def _result_label(value, dealer_value):
                if value > 21:
                    return "LOSS (Verloren)"
                if dealer_value > 21:
                    return "WIN (Gewonnen)"
                if value > dealer_value:
                    return "WIN (Gewonnen)"
                if value == dealer_value:
                    return "PUSH (Gelijkspel)"
                return "LOSS (Verloren)"

            human_result = _result_label(player_value, dealer_value)
            npc_result = _result_label(npc_value, dealer_value)

            # Show result in the banner instead of a modal popup
            msg = f"Jij: {human_result} | AI: {npc_result} — Jouw geld: €{self.human_money} | AI geld: €{self.npc_money}"
            self._show_round_banner(human_result, npc_result, msg)
        except Exception:
            # Don't let a popup failure interrupt the game flow
            pass
        
        # End of round
        self.game_over = True
        self.hit_btn.config(state=tk.DISABLED)
        self.stand_btn.config(state=tk.DISABLED)
        self.double_btn.config(state=tk.DISABLED)
        # reveal button removed
        self.new_round_btn.config(state=tk.NORMAL)
        # Clear bet chips after round ends
        try:
            self._clear_bet_chips()
        except Exception:
            pass
        
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

    def _show_round_banner(self, human_result, npc_result, text):
        """Display the round result in the in-UI banner with color coding and auto-hide."""
        # Choose color based on human result
        color_map = {
            'WIN (Gewonnen)': '#2E7D32',  # green
            'LOSS (Verloren)': '#C62828',  # red
            'PUSH (Gelijkspel)': '#F9A825',  # amber
        }
        bg = color_map.get(human_result, '#333333')
        try:
            self.result_banner.config(text=text, bg=bg)
            # set foreground contrast
            fg = 'white' if human_result != 'PUSH (Gelijkspel)' else 'black'
            self.result_banner.config(fg=fg)
            # Auto-hide after 4 seconds
            try:
                if hasattr(self, '_banner_after_id') and self._banner_after_id:
                    self.root.after_cancel(self._banner_after_id)
            except Exception:
                pass
            self._banner_after_id = self.root.after(4000, lambda: self.result_banner.config(text='', bg='#111111'))
        except Exception:
            pass
    
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

        for idx, card in enumerate(hand.cards):
            # If rendering dealer and the round is ongoing, hide the dealer's second card
            if hand is self.dealer_hand and (not self.game_over) and idx == 1:
                card_widget = CardWidget(frame, card, hidden=True)
            else:
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