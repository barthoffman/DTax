"""DGA / bv-route: vennootschapsbelasting + gebruikelijk loon (box 1) + dividend (box 2).

Wet Vpb 1969 art. 22 (tarief), Wet IB 2001 art. 2.12 (box 2), Wet LB 1964 art. 12a
(gebruikelijk loon). Bron-ID's DGA-* in het bronregister.

Aanname v1 (geoptimaliseerde DGA): de bv keert het gebruikelijk loon uit en deelt de
resterende winst na Vpb volledig uit als dividend (box 2). In werkelijkheid kan box 2
worden uitgesteld door winst in de bv te laten (rentevoordeel/uitstel) — dat is een
extra optimalisatie die hier NIET wordt meegenomen (zie waarschuwing).
"""

from __future__ import annotations

from dataclasses import dataclass

from .box1 import _heffing_over
from .engine import ResultaatPersoon, bereken_persoon
from .model import Persoon
from .params import Params, laad_params


@dataclass
class DGAResultaat:
    bv_winst: float
    gebruikelijk_loon: float
    winst_voor_vpb: float
    vennootschapsbelasting: float
    dividend_bruto: float            # box 2-grondslag (winst na Vpb)
    box1_resultaat: ResultaatPersoon  # loon + box 2 samen doorgerekend
    totale_belasting: float
    netto: float
    effectief_tarief: float
    waarschuwingen: list[str]


def bepaal_gebruikelijk_loon(bv_winst: float, p: Params, *, hoger_loon: float = 0.0) -> float:
    """Gebruikelijk loon = hoogste van normbedrag en een eventueel hoger zakelijk loon,
    maar nooit meer dan de beschikbare winst (vereenvoudiging)."""
    norm = p["dga"]["gebruikelijk_loon_normbedrag"]
    loon = max(norm, hoger_loon)
    return float(min(loon, max(0.0, bv_winst)))


def bereken_dga(
    bv_winst: float,
    jaar: int | Params,
    *,
    hoger_gebruikelijk_loon: float = 0.0,
    keer_dividend_uit: bool = True,
) -> DGAResultaat:
    p = jaar if isinstance(jaar, Params) else laad_params(jaar)
    waarschuwingen: list[str] = []

    loon = bepaal_gebruikelijk_loon(bv_winst, p, hoger_loon=hoger_gebruikelijk_loon)
    winst_voor_vpb = max(0.0, bv_winst - loon)
    vpb = round(_heffing_over(winst_voor_vpb, p["vpb"]["schijven"]), 2)
    dividend = round(winst_voor_vpb - vpb, 2)

    if not keer_dividend_uit:
        dividend = 0.0
        waarschuwingen.append(
            "Dividend niet uitgekeerd: box 2-heffing uitgesteld (winst blijft in bv). "
            "De totale druk is dan tijdelijk lager; bij latere uitkering volgt box 2 alsnog."
        )

    # Loon (box 1) en dividend (box 2) samen door de IB-engine: dividend telt mee in het
    # verzamelinkomen en beïnvloedt zo de afbouw van de heffingskortingen.
    persoon = Persoon(naam="dga", loon=loon)
    res = bereken_persoon(persoon, p, box2_inkomen=dividend)

    totale_belasting = round(vpb + res.te_betalen, 2)
    netto = round(bv_winst - totale_belasting, 2)
    effectief = round(totale_belasting / bv_winst, 4) if bv_winst else 0.0

    if loon >= bv_winst and bv_winst > 0:
        waarschuwingen.append(
            "Volledige winst gaat op aan gebruikelijk loon (geen dividend); "
            "feitelijk gelijk aan een werknemer."
        )

    return DGAResultaat(
        bv_winst=round(bv_winst, 2),
        gebruikelijk_loon=round(loon, 2),
        winst_voor_vpb=round(winst_voor_vpb, 2),
        vennootschapsbelasting=vpb,
        dividend_bruto=dividend,
        box1_resultaat=res,
        totale_belasting=totale_belasting,
        netto=netto,
        effectief_tarief=effectief,
        waarschuwingen=waarschuwingen + list(res.waarschuwingen),
    )
