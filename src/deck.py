# Gemaakt door Joshua Meuleman

"""Deck utilities voor Blackjack."""
from typing import List, Dict
import random


def create_deck(num_decks: int = 1) -> List[Dict[str, str]]:
    """Maakt een lijst van kaarten als dicts met keys 'suit' en 'rank'.

    num_decks: aantal 52-kaarten decks om samen te voegen (minimaal 1).
    Retourneert een lijst met kaart-dicts.
    """
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck: List[Dict[str, str]] = [] # Maak lege lijst voor kaarten en zorgt dat type bekend is
    count = max(1, int(num_decks))# Zorg dat er minimaal 1 deck is
    for _ in range(count):
        for suit in suits:
            for rank in ranks:
                deck.append({'suit': suit, 'rank': rank})
    return deck


def shuffle(deck: List[Dict[str, str]]) -> None:
    """Schudt het deck in-place."""
    random.shuffle(deck)


def draw(deck: List[Dict[str, str]]):
    """Trek één kaart uit het deck (laatste element)."""
    return deck.pop()
# Gemaakt door Joshua Meuleman



