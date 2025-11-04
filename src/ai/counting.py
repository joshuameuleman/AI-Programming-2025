#iemand mag dit doen 

#wat te doen:
#API:
#maak een class Counting
#reset()
#update(card) # accepteert dict-card of string
#running_count() -> int
#true_count(remaining_decks_estimate: float) -> float
#serialize()/deserialize() of save/load(path) — optioneel

#Acceptatiecriteria:
#update() verhoogt/verlaagt running count volgens Hi‑Lo waarden (2–6 = +1, 7–9 = 0, 10–A = −1).
#true_count() ≈ running_count / remaining_decks (float).