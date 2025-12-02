##gemaakt door Robbe Lambrechts

import os
from typing import Optional

try:
	from PIL import Image, ImageTk
	_HAS_PIL = True
except Exception:
	_HAS_PIL = False

import tkinter as tk


class CardImageLoader:
	"""Laadt en cachet kaartafbeeldingen uit een asset-map.

	Zoekt naar veelvoorkomende bestandsnaamschema's voor rank en suit.
	"""

	def __init__(self, assets_dir: Optional[str] = None):
		# standaard assets dir: project_root/assets/cards
		if assets_dir is None:
			# ga twee niveaus omhoog vanaf deze file: src/gui -> src -> project root
			here = os.path.dirname(__file__)
			project_root = os.path.abspath(os.path.join(here, '..', '..'))
			assets_dir = os.path.join(project_root, 'assets', 'cards')
		self.assets_dir = assets_dir
		self._cache = {}

	def _candidates(self, rank: str, suit: str):
		# normaliseer
		r = str(rank)
		s = str(suit).replace(' ', '_')
		candidates = [
			f"{r}_of_{s}.png",
			f"{r}_{s}.png",
			f"{r}{s}.png",
			f"{r}{s[0]}.png",
			f"{r}.png",
		]
		# ook lowercase
		candidates += [c.lower() for c in candidates]
		return candidates

	def load(self, rank: str, suit: str, size: Optional[tuple] = None):
		key = (rank, suit, size)
		if key in self._cache:
			return self._cache[key]

		# probeer bestanden
		for name in self._candidates(rank, suit):
			path = os.path.join(self.assets_dir, name)
			if os.path.isfile(path):
				if _HAS_PIL:
					img = Image.open(path)
					if size:
						img = img.resize(size, Image.LANCZOS)
					photo = ImageTk.PhotoImage(img)
					self._cache[key] = photo
					return photo
				else:
					# tkinter PhotoImage kan PNGs in moderne Tcl/Tk ondersteunen
					try:
						photo = tk.PhotoImage(file=path)
						self._cache[key] = photo
						return photo
					except Exception:
						# fallback en blijf zoeken
						pass

		# geen afbeelding gevonden
		self._cache[key] = None
		return None


class CardWidget(tk.Label):
	"""Een eenvoudige widget die een kaart afbeeldt met afbeelding of fallback-tekening.

	card kan een dict zijn: {'rank': 'A', 'suit': 'Spades'} of een string zoals 'A♠' of '10 Hearts'.
	"""

	def __init__(self, master, card, assets_dir: Optional[str] = None, image_size=(100,150), **kwargs):
		super().__init__(master, **kwargs)
		self.card = card
		self.image_size = image_size
		self.loader = CardImageLoader(assets_dir=assets_dir)
		self._image_ref = None
		self._draw()

	def _parse(self, card):
		if isinstance(card, dict):
			return card.get('rank'), card.get('suit')
		if isinstance(card, str):
			# eenvoudige heuristiek: als ' of ' aanwezig is
			if ' of ' in card:
				parts = card.split(' of ')
				return parts[0], parts[1]
			# probeer splits op space
			if ' ' in card:
				r, s = card.split(' ', 1)
				return r, s
			# anders neem laatste teken als suit
			if len(card) >= 2:
				return card[:-1], card[-1]
		return None, None

	def _draw(self):
		rank, suit = self._parse(self.card)
		img = None
		if rank is not None and suit is not None:
			img = self.loader.load(rank, suit, size=self.image_size)

		if img:
			self.configure(image=img)
			self._image_ref = img
			self.configure(width=self.image_size[0], height=self.image_size[1])
		else:
			# fallback: toon een eenvoudige getekende kaart op een Canvas en embed het
			canvas = tk.Canvas(self, width=self.image_size[0], height=self.image_size[1], highlightthickness=0)
			canvas.create_rectangle(2,2,self.image_size[0]-2,self.image_size[1]-2, fill='white', outline='black')
			text = f"{rank or '?'}\n{str(suit) if suit else ''}"
			canvas.create_text(self.image_size[0]//2, self.image_size[1]//2, text=text, font=('Arial', 18))
			# plaats canvas inside this label by packing
			canvas.pack(fill='both', expand=True)
			self._image_ref = canvas

##gemaakt door Robbe Lambrechts