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
    deck: List[Dict[str, str]] = []
    count = max(1, int(num_decks))
    for _ in range(count):
        for suit in suits:
            for rank in ranks:
                deck.append({'suit': suit, 'rank': rank})
    return deck


def shuffle(deck: List[Dict[str, str]]) -> None:
    """Schudt het deck in-place."""
    random.shuffle(deck)


# Draw observers: functies die worden aangeroepen met de kaart wanneer `draw` wordt gebruikt.
_draw_observers = []


def draw(deck: List[Dict[str, str]]):
    """Trek één kaart uit het deck (laatste element) en notify observers.

    Observers worden aangeroepen met één argument: de kaart-dict.
    """
    card = deck.pop()
    # Notify observers (if any). Observers must accept one argument: the card.
    for obs in list(_draw_observers):
        try:
            obs(card)
        except Exception:
            # Observer exceptions should not break drawing.
            continue
    return card


def register_draw_observer(func):
    """Registreer een observer (callable) die wordt aangeroepen met elke getrokken kaart.

    Example: `register_draw_observer(npc.observe_card)`
    """
    if func not in _draw_observers:
        _draw_observers.append(func)


def unregister_draw_observer(func):
    """Verwijder een eerder geregistreerde observer."""
    try:
        _draw_observers.remove(func)
    except ValueError:
        pass

# Gemaakt door Joshua Meuleman
