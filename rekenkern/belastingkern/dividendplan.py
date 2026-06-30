"""Box 2-dividendplanning: de optimale jaarlijkse dividenduitkering uit de BV.

Box 2 (aanmerkelijk belang, art. 2.12 Wet IB 2001): 24,5% tot de grens (€ 68.843 p.p. in
2026), 31% daarboven. Door de uitkering te SPREIDEN onder de grens betaal je alles tegen
24,5% i.p.v. 31% over het meerdere. Fiscale partners met aanmerkelijk belang hebben elk een
eigen schijf (samen 2×). De 15% dividendbelasting die de BV inhoudt is een voorheffing en
wordt met de box 2-aanslag verrekend (effectief tarief = box 2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil

from .params import laad_params


@dataclass
class DividendplanResultaat:
    jaar: int
    bedrag: float
    grens_laag: float            # 24,5%-grens (×2 bij partner)
    tarief_laag: float
    tarief_hoog: float
    heffing_ineens: float        # box 2 als je alles dit jaar uitkeert
    heffing_gespreid: float      # box 2 bij optimaal spreiden (alles in de lage schijf)
    besparing: float
    jaren_optimaal: int
    jaarlijks_dividend: float    # het optimale jaarbedrag (= grens, of het hele bedrag)
    waarschuwingen: list[str] = field(default_factory=list)


def box2_dividendplan(
    bedrag: float,
    jaar: int,
    *,
    partner: bool = False,
    overig_box2: float = 0.0,
) -> DividendplanResultaat:
    p = laad_params(jaar)
    schijven = p["box2"]["schijven"]
    grens = schijven[0]["tot"] * (2 if partner else 1)
    t_laag = schijven[0]["tarief"]
    t_hoog = schijven[1]["tarief"]

    # Alles dit jaar uitkeren: deel boven de grens valt in 31%.
    ruimte_laag = max(0.0, grens - overig_box2)
    in_laag = min(bedrag, ruimte_laag)
    in_hoog = max(0.0, bedrag - in_laag)
    heffing_ineens = round(in_laag * t_laag + in_hoog * t_hoog, 2)

    # Optimaal spreiden: elk jaar ≤ grens → alles tegen 24,5%.
    heffing_gespreid = round(bedrag * t_laag, 2)
    jaren = max(1, ceil(bedrag / grens)) if grens > 0 else 1
    jaarlijks = round(min(bedrag, grens), 2)

    waarschuwingen = [
        "Spreiden vereist dat je de uitkering écht over meerdere jaren neemt; het geld blijft "
        "ondertussen in de BV (groeit onder Vpb, box 2 uitgesteld) — zie de BV-uitstel-analyse.",
        "Aanname: geen ander box 2-inkomen dit jaar. Een fiscale partner met aanmerkelijk belang "
        "heeft een eigen 24,5%-schijf (samen 2×).",
        "De 15% dividendbelasting die de BV inhoudt is een voorheffing en wordt met box 2 verrekend "
        "— het effectieve tarief is dus box 2 (24,5% / 31%), niet 15%.",
    ]
    return DividendplanResultaat(
        jaar=jaar, bedrag=round(bedrag, 2), grens_laag=grens,
        tarief_laag=t_laag, tarief_hoog=t_hoog,
        heffing_ineens=heffing_ineens, heffing_gespreid=heffing_gespreid,
        besparing=round(heffing_ineens - heffing_gespreid, 2),
        jaren_optimaal=jaren, jaarlijks_dividend=jaarlijks, waarschuwingen=waarschuwingen,
    )
