"""Winst uit onderneming → belastbare winst (IB-ondernemer).

Wet IB 2001 afd. 3.2: art. 3.76 (zelfstandigen-/startersaftrek), art. 3.79a
(MKB-winstvrijstelling), art. 3.6 (urencriterium). De ondernemersaftrek én de
MKB-winstvrijstelling vallen onder de tariefaanpassing van art. 2.10a (afgetopt
aftrektarief); die correctie zit in box1.py.

Volgorde: winst − ondernemersaftrek = winst na ondernemersaftrek;
daarover MKB-winstvrijstelling (12,7%); resultaat = belastbare winst.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Onderneming
from .params import Params


def kia_aftrek(investering: float, p) -> float:
    """Kleinschaligheidsinvesteringsaftrek (art. 3.41): aftrek o.b.v. het totale
    investeringsbedrag in bedrijfsmiddelen. Onder de drempel of boven de bovengrens: 0."""
    k = p["onderneming"].get("kia")
    if not k or investering <= k["drempel"] or investering > k["boven"]:
        return 0.0
    if investering <= k["eerste_tot"]:
        return round(k["eerste_pct"] * investering, 2)
    if investering <= k["vast_tot"]:
        return float(k["vast_bedrag"])
    return round(max(0.0, k["vast_bedrag"] - k["afbouw_pct"] * (investering - k["vast_tot"])), 2)


@dataclass
class OndernemingResultaat:
    bruto_winst: float
    zelfstandigenaftrek: float
    startersaftrek: float
    overige_ondernemersaftrek: float
    ondernemersaftrek_totaal: float
    winst_na_ondernemersaftrek: float
    mkb_winstvrijstelling: float
    belastbare_winst: float
    aftrek_onder_2_10a: float       # ondernemersaftrek + MKB-vrijstelling
    toelichting: list[str]


def bereken_onderneming(ond: Onderneming, p: Params) -> OndernemingResultaat:
    cfg = p["onderneming"]
    winst = ond.winst
    toelichting: list[str] = []

    zelfstandigenaftrek = 0.0
    startersaftrek = 0.0
    if ond.voldoet_urencriterium:
        zelfstandigenaftrek = float(cfg["zelfstandigenaftrek"])
        if not ond.starter:
            # Niet-starter: zelfstandigenaftrek niet hoger dan de winst (geen verlies
            # creëren); het niet-benutte deel is voortwentelbaar (v1: niet bijgehouden).
            begrensd = min(zelfstandigenaftrek, max(0.0, winst))
            if begrensd < zelfstandigenaftrek:
                toelichting.append(
                    f"Zelfstandigenaftrek begrensd tot de winst (€ {begrensd:.0f} i.p.v. "
                    f"€ {zelfstandigenaftrek:.0f}); restant voortwentelbaar."
                )
            zelfstandigenaftrek = begrensd
        else:
            startersaftrek = float(cfg["startersaftrek"])
    else:
        toelichting.append(
            "Geen zelfstandigenaftrek: voldoet niet aan het urencriterium (1.225 uur)."
        )

    overige = max(0.0, ond.overige_ondernemersaftrek)
    ondernemersaftrek = round(zelfstandigenaftrek + startersaftrek + overige, 2)
    winst_na = round(winst - ondernemersaftrek, 2)

    mkb_pct = cfg["mkb_winstvrijstelling_pct"]
    # MKB-winstvrijstelling over de (positieve) winst na ondernemersaftrek.
    mkb = round(max(0.0, winst_na) * mkb_pct, 2)
    belastbare_winst = round(winst_na - mkb, 2)
    aftrek_2_10a = round(ondernemersaftrek + mkb, 2)

    toelichting.append(
        f"MKB-winstvrijstelling {mkb_pct:.1%} over € {winst_na:.0f} = € {mkb:.2f}."
    )

    return OndernemingResultaat(
        bruto_winst=round(winst, 2),
        zelfstandigenaftrek=round(zelfstandigenaftrek, 2),
        startersaftrek=round(startersaftrek, 2),
        overige_ondernemersaftrek=round(overige, 2),
        ondernemersaftrek_totaal=ondernemersaftrek,
        winst_na_ondernemersaftrek=winst_na,
        mkb_winstvrijstelling=mkb,
        belastbare_winst=belastbare_winst,
        aftrek_onder_2_10a=aftrek_2_10a,
        toelichting=toelichting,
    )
