"""Pensioen: jaarruimte en reserveringsruimte voor lijfrente (art. 3.127 Wet IB 2001).

De jaarruimte is het maximaal aftrekbare lijfrentebedrag in box 1. Aftrek verlaagt het
belastbaar inkomen (tegen het marginale tarief) én het toetsingsinkomen voor toeslagen;
bovendien valt het opgebouwde lijfrentekapitaal niet in box 3.

Formule (art. 3.127 lid 1):
    jaarruimte = opbouw% × (premiegevend inkomen − AOW-franchise)
                 − factor × factor A (pensioenaangroei werkgever) − FOR-afname
gemaximeerd op het premiegevend inkomen tot de aftoppingsgrens, en op de max. jaarruimte.

Voor ZZP/DGA zonder werkgeverspensioen is factor A = 0. Bron-ID's PEN-* in het register.
"""

from __future__ import annotations

from .params import Params


def jaarruimte(
    premiegevend_inkomen: float,
    p: Params,
    *,
    factor_a: float = 0.0,
    for_afname: float = 0.0,
) -> float:
    """Maximaal aftrekbare lijfrentepremie dit jaar."""
    cfg = p["pensioen"]
    grondslag = max(
        0.0, min(premiegevend_inkomen, cfg["max_premiegevend_inkomen"]) - cfg["aow_franchise"]
    )
    ruimte = (
        cfg["opbouwpercentage"] * grondslag
        - cfg["factor_aftrek_pensioenaangroei"] * factor_a
        - for_afname
    )
    return round(max(0.0, min(ruimte, cfg["max_jaarruimte"])), 2)


def reserveringsruimte(ongebruikte_jaarruimte_laatste_jaren: float, p: Params) -> float:
    """Inhaalruimte: niet-benutte jaarruimte van de afgelopen jaren, tot het maximum."""
    return round(
        min(max(0.0, ongebruikte_jaarruimte_laatste_jaren), p["pensioen"]["max_reserveringsruimte"]),
        2,
    )
