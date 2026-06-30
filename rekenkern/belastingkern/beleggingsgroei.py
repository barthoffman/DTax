"""Vierde scenario: hoe wordt beleggings-GROEI belast — box 3, box 1 (resultaat overige
werkzaamheden of winst uit onderneming), of via een BV?

Dit is een KWALIFICATIEvraag, geen vrije keuze: de wet bepaalt het regime op basis van de
aard van de activiteit (normaal vermogensbeheer → box 3; arbeid/kennis gericht op
meerrendement → box 1). De motor toont de belastingdruk op de groei per kwalificatie,
zodat de fiscaal optimale (en verdedigbare) route zichtbaar wordt.

Box 3 heft op het VERMOGEN (forfaitair, evt. tegenbewijs); de andere regimes op de
WERKELIJKE groei. Daardoor is box 3 relatief gunstiger naarmate het rendement hoger is.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .box1 import _heffing_over
from .engine import bereken_persoon
from .model import Onderneming, Persoon
from .optimalisatiemotor import box3_last
from .params import laad_params


@dataclass
class GroeiOptie:
    naam: str
    label: str
    belasting: float
    netto: float
    effectief_tarief: float   # belasting / groei
    toelichting: str


@dataclass
class BeleggingsgroeiResultaat:
    jaar: int
    spaargeld: float
    beleggingen: float
    schulden: float
    rendement_pct: float
    groei: float
    opties: list[GroeiOptie]
    waarschuwingen: list[str] = field(default_factory=list)

    @property
    def beste(self) -> GroeiOptie:
        return min(self.opties, key=lambda o: o.belasting)


def vergelijk_beleggingsgroei(
    beleggingen: float,
    rendement_pct: float,
    jaar: int,
    *,
    spaargeld: float = 0.0,
    schulden: float = 0.0,
    overig_inkomen: float = 0.0,
    urencriterium: bool = False,
    tegenbewijs: bool = True,
    partner: bool = False,
) -> BeleggingsgroeiResultaat:
    p = laad_params(jaar)
    # De te belasten groei rust op het beleggingsdeel (spaargeld groeit nauwelijks).
    groei = round(beleggingen * rendement_pct, 2)

    # Basis: belasting op het overige box 1-inkomen (voor het marginale effect van de groei).
    basis = bereken_persoon(Persoon(loon=overig_inkomen), p).te_betalen

    # 1. Box 3 — heft op het vermogen per categorie (forfaitair, of werkelijk via tegenbewijs).
    werkelijk = rendement_pct if tegenbewijs else None
    box3 = box3_last(
        p, spaargeld=spaargeld, beleggingen=beleggingen, schulden=schulden,
        partner=partner, werkelijk_rendement=werkelijk,
    )

    # 2. Box 1 — resultaat uit overige werkzaamheden (werkelijke groei, geen faciliteiten).
    row = round(
        bereken_persoon(
            Persoon(loon=overig_inkomen, resultaat_overige_werkzaamheden=groei), p
        ).te_betalen - basis, 2)

    # 3. Box 1 — winst uit onderneming (MKB-winstvrijstelling; zelfstandigenaftrek bij uren).
    winst = round(
        bereken_persoon(
            Persoon(loon=overig_inkomen,
                    onderneming=Onderneming(winst=groei, voldoet_urencriterium=urencriterium)),
            p,
        ).te_betalen - basis, 2)

    # 4. BV — Vpb over de groei + box 2 over het dividend.
    vpb = _heffing_over(groei, p["vpb"]["schijven"])
    bv = round(vpb + _heffing_over(groei - vpb, p["box2"]["schijven"]), 2)

    ruw = [
        ("box3", "Box 3 — normaal vermogensbeheer (forfaitair)", box3,
         "heft op het vermogen, niet op de werkelijke groei"),
        ("row", "Box 1 — resultaat overige werkzaamheden", row,
         "werkelijke groei, marginaal tarief, géén ondernemersfaciliteiten"),
        ("winst", "Box 1 — winst uit onderneming", winst,
         "werkelijke groei, mét MKB-winstvrijstelling"),
        ("bv", "BV — Vpb + box 2", bv,
         "werkelijke groei via de vennootschap"),
    ]
    opties = [
        GroeiOptie(n, l, round(b, 2), round(groei - b, 2),
                   round(b / groei, 4) if groei else 0.0, t)
        for (n, l, b, t) in ruw
    ]
    waarschuwingen = [
        "Dit is GEEN vrije keuze: de wet kwalificeert op basis van de aard van de activiteit.",
        "Box 3 alleen bij normaal vermogensbeheer; arbeid/kennis/frequentie gericht op "
        "meerrendement → box 1 (resultaat overige werkzaamheden of onderneming).",
        "Box 3-bedrag is inclusief heffingvrij vermogen (aanname: dit is je enige box 3-vermogen).",
        "De exacte grens is jurisprudentie-afhankelijk (art. 3.90/3.91 Wet IB 2001) → "
        "geschikt voor een onderbouwd standpunt richting de Belastingdienst.",
        "De box 1-uitkomst (ROW/winst) hangt af van je marginale tarief: bij weinig overig "
        "inkomen kan box 1 juist goedkoper zijn dan box 3; bij een hoog inkomen wint box 3.",
    ]
    return BeleggingsgroeiResultaat(
        jaar=jaar, spaargeld=spaargeld, beleggingen=beleggingen, schulden=schulden,
        rendement_pct=rendement_pct, groei=groei,
        opties=opties, waarschuwingen=waarschuwingen,
    )
