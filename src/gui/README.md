# GUI kaarten assets

Plaats je eigen kaartafbeeldingen in de map `assets/cards/` in de projectroot.

Naamconventies (de loader probeert meerdere varianten):

- `A_of_Spades.png`
- `10_of_Hearts.png`
- `K_Hearts.png`
- `A_Spades.png` of `AS.png`

Tips:
- Geef elke kaart een transparante PNG (of JPG) met ongeveer 100x150px of groter.
- Als je Pillow (`PIL`) installeert, worden afbeeldingen op grootte geschaald naar `image_size`.
- Als er geen afbeelding gevonden wordt, tekent de widget een eenvoudige fallback-kaart.

Gebruik in code (voorbeeld met tkinter):

```python
from tkinter import Tk
from src.gui.card import CardWidget

root = Tk()
cw = CardWidget(root, card={'rank':'A','suit':'Spades'})
cw.pack()
root.mainloop()
```

Als de afbeeldingen niet geladen worden, controleer of de map `assets/cards` bestaat en of de bestandsnamen precies overeenkomen.
