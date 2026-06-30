"""Zorgverzekeringswet (Zvw) inkomensafhankelijke bijdrage.

Twee varianten (Belastingdienst, tabel werkgeversheffing/bijdrage Zvw):
- **Werkgeversheffing** (hoog %): voor werknemers met verzekeringsplicht
  werknemersverzekeringen; betaald door de werkgever bovenop het loon.
- **Lage bijdrage** (laag %): o.a. IB-ondernemer (ZZP) en de DGA zonder
  verzekeringsplicht werknemersverzekeringen; betaald/ingehouden bij de persoon zelf.

Beide over het bijdrage-inkomen, gemaximeerd op het maximumbijdrage-inkomen.
Over box 2-dividend is GEEN Zvw verschuldigd. Bron-ID's ZVW-* in het bronregister.
"""

from __future__ import annotations

from .params import Params


def _gemaximeerd(grondslag: float, p: Params) -> float:
    return min(max(0.0, grondslag), p["zvw"]["max_bijdrage_inkomen"])


def werkgeversheffing_zvw(loon: float, p: Params) -> float:
    """Werkgeversheffing Zvw over het loon (werknemer)."""
    return round(_gemaximeerd(loon, p) * p["zvw"]["werkgeversheffing_pct"], 2)


def lage_bijdrage_zvw(bijdrage_inkomen: float, p: Params) -> float:
    """Lage inkomensafhankelijke bijdrage Zvw (ZZP / DGA, zelf betaald)."""
    return round(_gemaximeerd(bijdrage_inkomen, p) * p["zvw"]["lage_bijdrage_pct"], 2)


def werknemersverzekeringen_pct(p: Params, *, profiel: str = "klein_vast") -> float:
    """Totaal werkgeverspercentage WW/WIA. Default: kleine werkgever, vast contract
    (Awf laag + Aof laag + Whk gemiddeld). Whk is indicatief/werkgever-specifiek.

    DGA (aanmerkelijk belang) en ZZP zijn niet verzekerd → percentage niet van toepassing.
    """
    wv = p["werknemersverzekeringen"]
    awf = wv["awf_hoog"] if "flex" in profiel else wv["awf_laag"]
    aof = wv["aof_hoog"] if "groot" in profiel else wv["aof_laag"]
    return awf + aof + wv["whk_gemiddeld"]


def werknemersverzekeringen(loon: float, p: Params, *, profiel: str = "klein_vast") -> float:
    """Premies werknemersverzekeringen (werkgeverslast) over het loon, gemaximeerd op
    het maximumpremieloon."""
    wv = p["werknemersverzekeringen"]
    grondslag = min(max(0.0, loon), wv["max_premieloon"])
    return round(grondslag * werknemersverzekeringen_pct(p, profiel=profiel), 2)
