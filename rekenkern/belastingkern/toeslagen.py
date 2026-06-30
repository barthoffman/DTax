"""Toeslagen (Awir + materiewetten), gekoppeld aan het toetsingsinkomen.

Toetsingsinkomen = verzamelinkomen (box 1 + 2 + 3) van aanvrager + toeslagpartner.
v1 dekt de twee zuiver inkomensafhankelijke toeslagen die geen extra invoer vergen:
- **Zorgtoeslag** (Wet op de zorgtoeslag) — lineaire benadering van de afbouw.
- **Kindgebonden budget** (Wet kindgebonden budget) — exacte afbouw (afbouwpunt + %).

Huurtoeslag (vraagt rekenhuur) en kinderopvangtoeslag (vraagt opvanguren/-kosten) volgen
apart. Vermogenstoets: box 3-grondslag op peildatum 1 januari boven de grens → € 0.

Bron-ID's TOE-* in het bronregister.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .params import Params


@dataclass
class Huishoudprofiel:
    """Niet-financiële kenmerken die het toeslagrecht bepalen."""

    heeft_toeslagpartner: bool = False
    partner_inkomen: float = 0.0     # verzamelinkomen toeslagpartner (telt mee in toetsingsinkomen)
    aantal_kinderen: int = 0
    kinderen_12_15: int = 0          # subset van aantal_kinderen
    kinderen_16_17: int = 0          # subset van aantal_kinderen
    alleenstaande_ouder: bool = False
    box3_vermogen_1jan: float = 0.0  # gezamenlijk, peildatum 1 januari
    rekenhuur: float | None = None   # kale huur + servicekosten per maand (voor huurtoeslag)
    # Kinderopvang (situationeel; leeg = niet berekenen)
    kinderopvang_soort: str | None = None    # "dagopvang" | "bso" | "gastouder"
    kinderopvang_uren_per_maand: float = 0.0  # per kind
    kinderopvang_uurtarief: float = 0.0
    kinderopvang_kinderen: int = 0            # aantal kinderen in opvang
    kinderopvang_gewerkte_uren: float = 1000.0  # minstverdiener; hoog = geen urennorm-cap

    @property
    def aantal_personen(self) -> int:
        return 1 + (1 if self.heeft_toeslagpartner else 0) + self.aantal_kinderen


@dataclass
class ToeslagenResultaat:
    zorgtoeslag: float
    kindgebonden_budget: float
    huurtoeslag: float = 0.0
    kinderopvangtoeslag: float = 0.0
    waarschuwingen: list[str] = field(default_factory=list)

    @property
    def totaal(self) -> float:
        return round(
            self.zorgtoeslag + self.kindgebonden_budget
            + self.huurtoeslag + self.kinderopvangtoeslag, 2
        )


def zorgtoeslag(
    toetsingsinkomen: float, p: Params, *, partner: bool = False, vermogen: float = 0.0
) -> float:
    cfg = p["toeslagen"]["zorgtoeslag"]
    vgrens = cfg["vermogensgrens_partners" if partner else "vermogensgrens_alleenstaande"]
    if vermogen > vgrens:
        return 0.0
    maxb = cfg["max_partners" if partner else "max_alleenstaande"]
    drempel = cfg["drempelinkomen"]
    grens = cfg["inkomensgrens_partners" if partner else "inkomensgrens_alleenstaande"]
    if toetsingsinkomen <= drempel:
        return float(maxb)
    if toetsingsinkomen >= grens:
        return 0.0
    # Lineaire benadering tussen drempelinkomen (volledig) en inkomensgrens (nihil).
    return round(maxb * (grens - toetsingsinkomen) / (grens - drempel), 2)


def kindgebonden_budget(
    toetsingsinkomen: float,
    p: Params,
    *,
    profiel: Huishoudprofiel,
) -> float:
    if profiel.aantal_kinderen <= 0:
        return 0.0
    cfg = p["toeslagen"]["kindgebonden_budget"]
    partner = profiel.heeft_toeslagpartner
    vgrens = cfg["vermogensgrens_partners" if partner else "vermogensgrens_alleenstaande"]
    if profiel.box3_vermogen_1jan > vgrens:
        return 0.0

    basis = (
        profiel.aantal_kinderen * cfg["basisbedrag_per_kind"]
        + profiel.kinderen_12_15 * cfg["opslag_12_15"]
        + profiel.kinderen_16_17 * cfg["opslag_16_17"]
    )
    if profiel.alleenstaande_ouder:
        basis += cfg["alleenstaande_ouderkop"]

    afbouwpunt = cfg["afbouwpunt_partners" if partner else "afbouwpunt_alleenstaande"]
    bedrag = basis - cfg["afbouw_pct"] * max(0.0, toetsingsinkomen - afbouwpunt)
    return max(0.0, round(bedrag, 2))


def huurtoeslag(
    rekenhuur: float,
    toetsingsinkomen: float,
    p: Params,
    *,
    profiel: Huishoudprofiel,
) -> tuple[float, list[str]]:
    """Huurtoeslag (per jaar). 2026: lineaire afbouw; 2025: benadering (zie structuur).

    Subsidiestaffel op de maandhuur boven de eigen bijdrage (100% / 65% / 40%), daarna
    lineaire inkomensafbouw boven het minimuminkomensijkpunt.
    """
    cfg = p["toeslagen"]["huurtoeslag"]
    waarschuwingen: list[str] = []
    partner = profiel.heeft_toeslagpartner
    meerpersoons = profiel.aantal_personen >= 2

    vgrens = cfg["vermogensgrens_partners" if partner else "vermogensgrens_alleenstaande"]
    if profiel.box3_vermogen_1jan > vgrens:
        return 0.0, ["Geen huurtoeslag: vermogen boven de grens."]

    maxhuur = cfg["max_huurgrens"]
    if rekenhuur > maxhuur:
        if cfg["structuur"].startswith("benadering"):  # 2025: harde huurgrens
            return 0.0, ["Geen huurtoeslag: rekenhuur boven de maximale huurgrens (2025)."]
        rekenhuur = maxhuur  # 2026: geen harde grens, staffel tot de max-grens

    basis = cfg["min_eigen_bijdrage_mp" if meerpersoons else "min_eigen_bijdrage_1p"]
    kk = cfg["kwaliteitskortingsgrens"]
    at = cfg["aftoppingsgrens_hoog" if profiel.aantal_personen >= 3 else "aftoppingsgrens_laag"]
    if rekenhuur <= basis:
        return 0.0, waarschuwingen

    maand = max(0.0, min(rekenhuur, kk) - basis)               # 100%
    if rekenhuur > kk:
        maand += 0.65 * (min(rekenhuur, at) - kk)              # 65%
    if rekenhuur > at:
        maand += 0.40 * (min(rekenhuur, maxhuur) - at)         # 40%

    per_jaar = maand * 12
    ijk = cfg["minimuminkomensijkpunt_mp" if meerpersoons else "minimuminkomensijkpunt_1p"]
    factor = cfg["afbouw_per_euro_mp" if meerpersoons else "afbouw_per_euro_1p"]
    afbouw = factor * max(0.0, toetsingsinkomen - ijk)

    if cfg["structuur"].startswith("benadering"):
        waarschuwingen.append(
            "Huurtoeslag 2025 is een benadering (officieel kwadratische eigen-bijdrageformule)."
        )
    return round(max(0.0, per_jaar - afbouw), 2), waarschuwingen


def kinderopvang_vergoedingspercentage(
    toetsingsinkomen: float, p: Params, *, eerste_kind: bool = True
) -> float:
    """Inkomensafhankelijk vergoedingspercentage (lineaire benadering van Bijlage I)."""
    cfg = p["toeslagen"]["kinderopvangtoeslag"]
    maxp = cfg["vergoeding_max_pct"]
    minp = cfg["vergoeding_min_pct_eerste_kind" if eerste_kind else "vergoeding_min_pct_volgende_kind"]
    g_max = cfg["vergoeding_inkomensgrens_max"]
    g_min = cfg["vergoeding_inkomensgrens_min"]
    if toetsingsinkomen <= g_max:
        return maxp
    if toetsingsinkomen >= g_min:
        return minp
    return round(maxp - (maxp - minp) * (toetsingsinkomen - g_max) / (g_min - g_max), 4)


def kinderopvangtoeslag(
    toetsingsinkomen: float,
    p: Params,
    *,
    opvangsoort: str,                 # "dagopvang" | "bso" | "gastouder"
    uurtarief: float,                 # werkelijk uurtarief
    opvanguren_per_maand: float,      # afgenomen uren per kind per maand
    gewerkte_uren_minstverdiener_per_maand: float,
    eerste_kind: bool = True,
) -> float:
    """Kinderopvangtoeslag per jaar voor één kind (situationeel; geen vermogenstoets)."""
    cfg = p["toeslagen"]["kinderopvangtoeslag"]
    vergoed_tarief = min(uurtarief, cfg[f"max_uurtarief_{opvangsoort}"])
    norm = cfg[f"urennorm_{opvangsoort}_pct"]
    vergoede_uren = min(
        opvanguren_per_maand,
        norm * gewerkte_uren_minstverdiener_per_maand,
        cfg["max_uren_per_kind_per_maand"],
    )
    pct = kinderopvang_vergoedingspercentage(toetsingsinkomen, p, eerste_kind=eerste_kind)
    return round(vergoed_tarief * vergoede_uren * pct * 12, 2)


def bereken_toeslagen(
    toetsingsinkomen: float,
    p: Params,
    *,
    profiel: Huishoudprofiel | None = None,
) -> ToeslagenResultaat:
    profiel = profiel or Huishoudprofiel()
    partner = profiel.heeft_toeslagpartner
    verm = profiel.box3_vermogen_1jan

    zt = zorgtoeslag(toetsingsinkomen, p, partner=partner, vermogen=verm)
    kgb = kindgebonden_budget(toetsingsinkomen, p, profiel=profiel)

    waarschuwingen = [
        "Zorgtoeslag-afbouw is een lineaire benadering (drempelinkomen afgeleid)."
    ]

    ht = 0.0
    if profiel.rekenhuur is not None:
        ht, ht_waarschuwingen = huurtoeslag(profiel.rekenhuur, toetsingsinkomen, p, profiel=profiel)
        waarschuwingen += ht_waarschuwingen
    else:
        waarschuwingen.append("Huurtoeslag niet berekend (geen rekenhuur opgegeven).")

    # Kinderopvangtoeslag (situationeel): per kind, 1e kind eerste-%, volgende kinderen hoger-%.
    kot = 0.0
    if (
        profiel.kinderopvang_soort and profiel.kinderopvang_kinderen
        and profiel.kinderopvang_uren_per_maand and profiel.kinderopvang_uurtarief
    ):
        for i in range(profiel.kinderopvang_kinderen):
            kot += kinderopvangtoeslag(
                toetsingsinkomen, p,
                opvangsoort=profiel.kinderopvang_soort,
                uurtarief=profiel.kinderopvang_uurtarief,
                opvanguren_per_maand=profiel.kinderopvang_uren_per_maand,
                gewerkte_uren_minstverdiener_per_maand=profiel.kinderopvang_gewerkte_uren,
                eerste_kind=(i == 0),
            )
        kot = round(kot, 2)
        waarschuwingen.append(
            "Kinderopvangtoeslag: urennorm-cap is vereenvoudigd (aanname: beide ouders werken "
            "voldoende); géén harde inkomensgrens (minimaal ~36,5%)."
        )

    return ToeslagenResultaat(
        zorgtoeslag=zt, kindgebonden_budget=kgb, huurtoeslag=ht,
        kinderopvangtoeslag=kot, waarschuwingen=waarschuwingen,
    )
