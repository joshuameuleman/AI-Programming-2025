##gemaakt door Robbe Lambrechts maar extra bewerkingen door Joshua Meuleman

import os
import math
from typing import Optional

import tkinter as tk

try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False


class CardImageLoader:
    """Laadt en cachet kaartafbeeldingen uit de luxe assets of fallback-map."""

    def __init__(self, assets_dir: Optional[str] = None):
        # Standaard: probeer luxe kaarten, anders fallback naar assets/cards
        if assets_dir is None:
            here = os.path.dirname(__file__)
            project_root = os.path.abspath(os.path.join(here, '..', '..'))
            preferred = os.path.join(project_root, 'src', 'gui', 'full_art_luxe_kaarten')
            default = os.path.join(project_root, 'assets', 'cards')
            assets_dir = preferred if os.path.isdir(preferred) else default
        self.assets_dir = assets_dir
        self._cache = {}

    def _normalize_rank(self, rank: str) -> str:
        r = str(rank).strip()
        mapping = {
            'A': 'Ace', 'Ace': 'Ace',
            'K': 'King', 'King': 'King',
            'Q': 'Queen', 'Queen': 'Queen',
            'J': 'Jack', 'Jack': 'Jack',
            '10': 'Ten', 'T': 'Ten', 'Ten': 'Ten',
            '9': 'Nine', 'Nine': 'Nine',
            '8': 'Eight', 'Eight': 'Eight',
            '7': 'Seven', 'Seven': 'Seven',
            '6': 'Six', 'Six': 'Six',
            '5': 'Five', 'Five': 'Five',
            '4': 'Four', 'Four': 'Four',
            '3': 'Three', 'Three': 'Three',
            '2': 'Two', 'Two': 'Two',
        }
        return mapping.get(r, r.title())

    def _normalize_suit(self, suit: str) -> str:
        return str(suit).replace(' ', '_').lower()

    def _fallback_suits(self, normalized_suit: str):
        """Fallback suits per color family (red->hearts, black->spades)."""
        if normalized_suit in ('hearts', 'heart', 'diamonds', 'diamond'):
            return ['hearts']
        if normalized_suit in ('spades', 'spade', 'clubs', 'club'):
            return ['spades']
        return []

    def _candidates(self, rank: str, suit: str):
        r = self._normalize_rank(rank)
        s = self._normalize_suit(suit)
        base = [
            f"{r}_of_{s}.png",
            f"{r}_{s}.png",
            f"{r}{s}.png",
            f"{r}{s[:1]}.png" if s else f"{r}.png",
            f"{r}.png",
        ]
        for alt in self._fallback_suits(s):
            base.append(f"{r}_of_{alt}.png")
            base.append(f"{r}_{alt}.png")
            base.append(f"{r}{alt}.png")
        return base + [c.lower() for c in base]

    def load(self, rank: str, suit: str, size: Optional[tuple] = None):
        key = (rank, suit, size)
        if key in self._cache:
            return self._cache[key]

        s_norm = self._normalize_suit(suit)
        for name in self._candidates(rank, suit):
            # Try base folder and suit-specific folders derived from both original and candidate name
            suit_from_name = None
            if "_of_" in name:
                suit_from_name = name.split("_of_")[-1].replace(".png", "")
            elif "_" in name:
                # e.g. Ace_spades.png
                suit_from_name = name.split("_")[-1].replace(".png", "")

            folders = [None, s_norm]
            if suit_from_name:
                folders.append(suit_from_name)

            paths = []
            for folder in folders:
                if folder:
                    paths.append(os.path.join(self.assets_dir, folder, name))
                paths.append(os.path.join(self.assets_dir, name))

            for path in [p for p in paths if p]:
                if os.path.isfile(path):
                    if _HAS_PIL:
                        img = Image.open(path)
                        if size:
                            img = img.copy()
                            img.thumbnail(size, Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self._cache[key] = photo
                        return photo
                    else:
                        try:
                            photo = tk.PhotoImage(file=path)
                            if size:
                                w, h = photo.width(), photo.height()
                                factor = max(math.ceil(w / size[0]), math.ceil(h / size[1]), 1)
                                if factor > 1:
                                    photo = photo.subsample(factor, factor)
                            self._cache[key] = photo
                            return photo
                        except Exception:
                            pass

        self._cache[key] = None
        return None

    def load_back(self, size: Optional[tuple] = None):
        key = ("__back__", size)
        if key in self._cache:
            return self._cache[key]
        path = os.path.join(self.assets_dir, 'full_art_luxe_back.png')
        if os.path.isfile(path):
            if _HAS_PIL:
                img = Image.open(path)
                if size:
                    img = img.copy()
                    img.thumbnail(size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._cache[key] = photo
                return photo
            else:
                try:
                    photo = tk.PhotoImage(file=path)
                    if size:
                        w, h = photo.width(), photo.height()
                        factor = max(math.ceil(w / size[0]), math.ceil(h / size[1]), 1)
                        if factor > 1:
                            photo = photo.subsample(factor, factor)
                    self._cache[key] = photo
                    return photo
                except Exception:
                    pass
        self._cache[key] = None
        return None


class CardWidget(tk.Frame):
    """Widget voor kaartweergave zonder witte rand."""

    def __init__(self, master, card, assets_dir: Optional[str] = None, image_size=(110, 165), box_size=(110, 165), hidden: bool = False, **kwargs):
        super().__init__(master, width=box_size[0], height=box_size[1], bg="#1a1a1a", highlightthickness=0, **kwargs)
        self.pack_propagate(False)
        self.card = card
        self.image_size = image_size
        self.box_size = box_size
        self.hidden = hidden
        self.loader = CardImageLoader(assets_dir=assets_dir)
        self._image_ref = None
        self._draw()

    def _parse(self, card):
        if isinstance(card, dict):
            return card.get('rank'), card.get('suit')
        if isinstance(card, str):
            if ' of ' in card:
                parts = card.split(' of ')
                return parts[0], parts[1]
            if ' ' in card:
                r, s = card.split(' ', 1)
                return r, s
            if len(card) >= 2:
                return card[:-1], card[-1]
        return None, None

    def _clear_children(self):
        for child in self.winfo_children():
            child.destroy()

    def _draw(self):
        self._clear_children()
        if self.hidden:
            img = self.loader.load_back(size=self.image_size)
            if img:
                lbl = tk.Label(self, image=img, bd=0, highlightthickness=0, bg="#1a1a1a")
                lbl.pack(fill='both', expand=True)
                self._image_ref = img
                return

        rank, suit = self._parse(self.card)
        img = None
        if rank is not None and suit is not None:
            img = self.loader.load(rank, suit, size=self.image_size)

        if img:
            lbl = tk.Label(self, image=img, bd=0, highlightthickness=0, bg="#1a1a1a")
            lbl.pack(fill='both', expand=True)
            self._image_ref = img
        else:
            canvas = tk.Canvas(self, width=self.box_size[0], height=self.box_size[1], highlightthickness=0, bg="#1a1a1a")
            canvas.create_rectangle(4, 4, self.box_size[0]-4, self.box_size[1]-4, fill='white', outline='black')
            text = f"{rank or '?'}\n{str(suit) if suit else ''}"
            canvas.create_text(self.box_size[0]//2, self.box_size[1]//2, text=text, font=('Arial', 11))
            canvas.pack(fill='both', expand=True)
            self._image_ref = canvas

##gemaakt door Robbe Lambrechts maar extra bewerkingen door Joshua Meuleman
