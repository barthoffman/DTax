"""Specifieke zorgkosten (Wet IB 2001 art. 6.17 e.v.) — persoonsgebonden aftrek in box 1.

Alleen het deel van de specifieke zorgkosten bóven de inkomensafhankelijke drempel (art. 6.20)
is aftrekbaar. Premie zorgverzekering en eigen risico tellen NIET mee. De verhoging van art. 6.19
(bepaalde kosten +40% onder de AOW-leeftijd bij laag inkomen; anders voor AOW-ers) is nog niet
gemodelleerd → conservatief (aftrek eerder te laag dan te hoog). Bron-ID ZORG-* in het register.
"""

from __future__ import annotations


def zorgkosten_drempel(drempelinkomen: float, heeft_partner: bool, p) -> float:
    """Drempelbedrag specifieke zorgkosten o.b.v. het drempelinkomen (art. 6.20)."""
    z = p["zorgkosten"]
    grens_vast = z["grens_vast_partner"] if heeft_partner else z["grens_vast_solo"]
    vast = z["drempel_vast_partner"] if heeft_partner else z["drempel_vast_solo"]
    di = max(0.0, drempelinkomen)
    if di <= grens_vast:
        return float(vast)
    if di <= z["midden_tot"]:
        return round(z["midden_pct"] * di, 2)
    return round(z["hoog_vast"] + z["hoog_pct"] * (di - z["hoog_vanaf"]), 2)


def zorgkosten_aftrek(zorgkosten: float, drempelinkomen: float, heeft_partner: bool, p) -> float:
    """Aftrekbaar deel = specifieke zorgkosten minus de drempel (niet negatief)."""
    return round(max(0.0, max(0.0, zorgkosten) - zorgkosten_drempel(drempelinkomen, heeft_partner, p)), 2)
