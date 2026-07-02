"""Giftenaftrek (Wet IB 2001 art. 6.32 e.v.) — persoonsgebonden aftrek in box 1.

Twee soorten:
- **Gewone giften**: aftrekbaar vóór zover boven de drempel (1% van het drempelinkomen, min € 60)
  en tot het plafond (10% van het drempelinkomen).
- **Periodieke giften** (vastgelegd, min. 5 jaar): géén drempel/plafond, tot een jaarmaximum.

Bron-ID GIFT-* in het register. Culturele-ANBI-verhoging (25%, max € 1.250) nog niet gemodelleerd.
"""

from __future__ import annotations


def giftenaftrek(p, *, gewone: float = 0.0, periodiek: float = 0.0, drempelinkomen: float = 0.0) -> float:
    """Aftrekbaar giftenbedrag. `drempelinkomen` ≈ verzamelinkomen (voor de 1%/10%-grenzen)."""
    g = p["giften"]
    # Periodieke giften: geen drempel, tot het jaarmaximum.
    periodiek_aftrek = min(max(0.0, periodiek), g["periodiek_max"])
    # Gewone giften: alleen het deel boven de drempel, en niet meer dan het plafond.
    drempel = max(g["drempel_pct"] * max(0.0, drempelinkomen), g["drempel_min"])
    plafond = g["plafond_pct"] * max(0.0, drempelinkomen)
    gewone_aftrek = max(0.0, min(max(0.0, gewone), plafond) - drempel)
    return round(periodiek_aftrek + gewone_aftrek, 2)
