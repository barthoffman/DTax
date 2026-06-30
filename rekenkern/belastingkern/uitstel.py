"""BV-uitstel vs. uitkeren-en-privé-beleggen over een horizon.

De centrale vraag: levert geld in de BV laten groeien (jaarlijks alleen Vpb, box 2
uitgesteld) de eigenaar méér op dan nu uitkeren (box 2 betalen) en privé beleggen (box 3)?

Kerninzicht — het hangt af van of je het rendement CONSUMEERT of ACCUMULEERT:
- Accumuleren in de BV: jaarlijkse druk = alleen Vpb (~19%); box 2 wordt uitgesteld.
- Privé box 3: jaarlijkse druk ≈ forfait × 36% van het vermogen (of werkelijk via tegenbewijs).

Omdat box 2 in BEIDE routes uiteindelijk wordt betaald (nu of later, op dezelfde grondslag),
valt die weg in de vergelijking: de winnaar wordt bepaald door welke route jaarlijks
sneller netto groeit. Daardoor wint de BV bij gematigd rendement en de box 3-route bij hoog
rendement (waar het forfait ondertaxeert). Het omslagrendement is forfait×36% / Vpb%.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .params import laad_params


@dataclass
class UitstelResultaat:
    jaar: int
    kapitaal: float
    rendement_pct: float
    jaren: int
    bv_netto_groei_pct: float       # jaarlijkse netto groeivoet in de BV
    prive_netto_groei_pct: float    # jaarlijkse netto groeivoet privé (box 3)
    bv_eindnetto: float             # na box 2 aan het eind
    prive_eindnetto: float
    omslag_rendement: float         # rendement waarboven box 3 wint
    beste: str                      # "bv" | "prive"
    waarschuwingen: list[str] = field(default_factory=list)


def vergelijk_uitstel(
    kapitaal: float,
    rendement_pct: float,
    jaren: int,
    jaar: int,
    *,
    tegenbewijs: bool = True,
    partner: bool = False,
    forfait_cat: str = "overige_bezittingen",
    pas_heffingvrij: bool = True,
) -> UitstelResultaat:
    p = laad_params(jaar)
    vpb = p["vpb"]["schijven"][0]["tarief"]      # 19%
    box2 = p["box2"]["schijven"][0]["tarief"]    # 24,5%
    b3 = p.box3
    forfait = b3["forfait"][forfait_cat]          # box 3-categorie van de privé-route
    tarief3 = b3["tarief"]
    heffingvrij = (b3["heffingvrij_vermogen_pp"] * (2 if partner else 1)) if pas_heffingvrij else 0.0
    pct3 = min(forfait, rendement_pct) if tegenbewijs else forfait

    # BV: jaarlijks alleen Vpb op het rendement (geen heffingvrij); box 2 aan het eind.
    bv = kapitaal
    for _ in range(int(jaren)):
        bv += bv * rendement_pct * (1 - vpb)
    bv_eind = round(bv * (1 - box2), 2)

    # Privé: nu box 2, dan jaarlijks box 3 over (vermogen − heffingvrij vermogen).
    priv = kapitaal * (1 - box2)
    for _ in range(int(jaren)):
        box3_tax = tarief3 * pct3 * max(0.0, priv - heffingvrij)
        priv += priv * rendement_pct - box3_tax
    prive_eind = round(priv, 2)

    netto_nu = kapitaal * (1 - box2)  # gemeenschappelijk vertrekpunt (na box 2)
    def annualized(eind):
        return round((eind / netto_nu) ** (1 / jaren) - 1, 4) if jaren and netto_nu > 0 else 0.0

    # Asymptotisch omslagrendement (groot vermogen, heffingvrij verwaarloosbaar).
    omslag = round(forfait * tarief3 / vpb, 4) if vpb else 0.0

    waarschuwingen = [
        "Box 2 wordt in beide routes betaald (nu of later, zelfde grondslag) en bepaalt de "
        "winnaar niet — alleen de timing. De winnaar volgt uit de jaarlijkse netto groei.",
        f"Heffingvrij vermogen box 3 (€ {heffingvrij:,.0f}) is meegerekend: dat maakt de "
        "privé-route bij kleinere bedragen gunstiger (en verlaagt het omslagrendement).".replace(",", "."),
        "Aanname: het rendement wordt geACCUMULEERD (niet jaarlijks opgenomen). Bij consumeren "
        "is de BV ~38,8% en wint box 3 (36%) — zie tab Beleggingsgroei.",
        "Box 2-tarief verondersteld stabiel (24,5%); een toekomstige tariefwijziging beïnvloedt de BV.",
    ]
    return UitstelResultaat(
        jaar=jaar, kapitaal=kapitaal, rendement_pct=rendement_pct, jaren=jaren,
        bv_netto_groei_pct=annualized(bv_eind), prive_netto_groei_pct=annualized(prive_eind),
        bv_eindnetto=bv_eind, prive_eindnetto=prive_eind,
        omslag_rendement=omslag, beste=("bv" if bv_eind >= prive_eind else "prive"),
        waarschuwingen=waarschuwingen,
    )
