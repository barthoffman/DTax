"""Box 3: forfaitair rendement uit sparen en beleggen (Overbruggingswet box 3).

Wet IB 2001 hoofdstuk 5: art. 5.2/5.3 (forfait, grondslag, schuldendrempel),
art. 5.5 (heffingvrij vermogen), art. 2.13 (tarief 36%).

Vereenvoudiging v1: het werkelijk-rendement-tegenbewijs (OWR) wordt nog niet
doorgerekend; alleen het forfaitaire stelsel. Bij veel spaargeld/verlies kan OWR
gunstiger zijn — dat is een aparte module (TODO).
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Box3Vermogen
from .params import Params


@dataclass
class Box3Resultaat:
    rendementsgrondslag: float
    forfaitair_rendement: float
    grondslag_na_heffingvrij: float
    belasting: float
    effectief_rendementspercentage: float
    tegenbewijs_toegepast: bool
    waarschuwingen: list[str]


def bereken_box3(
    vermogen: Box3Vermogen,
    p: Params,
    *,
    heeft_fiscale_partner: bool = False,
    aandeel: float = 1.0,
) -> Box3Resultaat:
    """Bereken box 3-heffing voor een (deel van het) vermogen.

    `aandeel` is het aan deze persoon toegerekende deel (art. 2.17). Heffingvrij
    vermogen is per persoon; bij partners telt elk zijn eigen heffingvrij bedrag.
    """
    b3 = p.box3
    f = b3["forfait"]
    waarschuwingen: list[str] = []
    if f.get("banktegoeden_voorlopig") or f.get("schulden_voorlopig"):
        waarschuwingen.append(
            f"Box 3-forfaits {p.jaar} voor banktegoeden/schulden zijn voorlopig "
            "(definitief begin volgend jaar)."
        )

    # Groene beleggingen zijn vrijgesteld tot een maximum (vereenvoudigd: van overige).
    groen_vrij = min(vermogen.groene_beleggingen, b3["groene_vrijstelling_pp"])
    banktegoeden = vermogen.banktegoeden
    overige = max(0.0, vermogen.overige_bezittingen - groen_vrij)

    # Schuldendrempel: schulden tellen pas mee boven de drempel.
    drempel = b3["schuldendrempel_pp"]
    schulden_meetellend = max(0.0, vermogen.schulden - drempel)

    rendement = (
        banktegoeden * f["banktegoeden"]
        + overige * f["overige_bezittingen"]
        - schulden_meetellend * f["schulden"]
    )
    grondslag = banktegoeden + overige - schulden_meetellend

    heffingvrij = b3["heffingvrij_vermogen_pp"]
    # Forfaitair rendement wordt naar rato op de grondslag-na-heffingvrij toegepast.
    if grondslag > 0:
        forfait_pct = rendement / grondslag
    else:
        forfait_pct = 0.0

    # Tegenbewijsregeling: is het werkelijke rendement lager dan het forfait, dan over
    # het werkelijke (eenzijdig naar beneden). Werkt op het rendementspercentage.
    effectief_pct = forfait_pct
    tegenbewijs = False
    if vermogen.werkelijk_rendement_pct is not None and vermogen.werkelijk_rendement_pct < forfait_pct:
        effectief_pct = vermogen.werkelijk_rendement_pct
        tegenbewijs = True
        waarschuwingen.append(
            "Tegenbewijsregeling toegepast: heffing over werkelijk rendement "
            f"({effectief_pct:.2%}) i.p.v. forfait ({forfait_pct:.2%})."
        )

    grondslag_na_vrij = max(0.0, grondslag - heffingvrij)
    voordeel = grondslag_na_vrij * effectief_pct
    belasting = round(voordeel * b3["tarief"] * aandeel, 2)

    return Box3Resultaat(
        rendementsgrondslag=round(grondslag, 2),
        forfaitair_rendement=round(rendement, 2),
        grondslag_na_heffingvrij=round(grondslag_na_vrij, 2),
        belasting=belasting,
        effectief_rendementspercentage=round(effectief_pct, 4),
        tegenbewijs_toegepast=tegenbewijs,
        waarschuwingen=waarschuwingen,
    )
