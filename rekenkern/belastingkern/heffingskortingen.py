"""Heffingskortingen (Wet IB 2001 hoofdstuk 8).

Berekent algemene heffingskorting (8.10), arbeidskorting (8.11), IACK (8.14a),
ouderenkorting (8.17), alleenstaande-ouderenkorting (8.18) en
jonggehandicaptenkorting (8.16a). Verzilvering (art. 8.8) gebeurt in engine.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Persoon
from .params import Params


@dataclass
class Heffingskortingen:
    algemene: float
    arbeids: float
    iack: float
    ouderen: float
    alleenstaande_ouderen: float
    jonggehandicapten: float
    benaderingen: list[str]

    @property
    def totaal(self) -> float:
        return round(
            self.algemene
            + self.arbeids
            + self.iack
            + self.ouderen
            + self.alleenstaande_ouderen
            + self.jonggehandicapten,
            2,
        )


def _afbouw(max_bedrag: float, grondslag: float, start: float, pct: float) -> float:
    """Lineaire afbouw vanaf `start` met percentage `pct`, ondergrens 0."""
    if grondslag <= start:
        return max_bedrag
    return max(0.0, round(max_bedrag - (grondslag - start) * pct, 2))


def algemene_heffingskorting(verzamelinkomen: float, persoon: Persoon, p: Params) -> float:
    cfg = p.heffingskortingen["algemene"]
    sub = cfg["vanaf_aow"] if persoon.aow_gerechtigd else cfg["onder_aow"]
    return _afbouw(sub["max"], verzamelinkomen, sub["afbouw_start"], sub["afbouw_pct"])


def arbeidskorting(persoon: Persoon, p: Params) -> tuple[float, list[str]]:
    cfg = p.heffingskortingen["arbeids"]
    inkomen = persoon.arbeidsinkomen
    onder = cfg["onder_aow"]
    segmenten = onder["segmenten"]

    # Vind het hoogste segment waarvan de ondergrens <= inkomen.
    bedrag = 0.0
    for seg in segmenten:
        if inkomen >= seg["ondergrens"]:
            bedrag = seg["basis"] + seg["pct"] * (inkomen - seg["ondergrens"])
    bedrag = max(0.0, min(bedrag, onder["max"]))
    bedrag = round(bedrag, 2)

    benaderingen: list[str] = []
    if persoon.aow_gerechtigd and bedrag > 0:
        # Boven AOW-leeftijd zijn de percentages ~gehalveerd; v1 schaalt de uitkomst
        # naar het AOW-maximum. Benadering (geen exacte AOW-segmenttabel in params).
        factor = cfg["vanaf_aow_max"] / onder["max"] if onder["max"] else 0.0
        bedrag = round(bedrag * factor, 2)
        benaderingen.append(
            "Arbeidskorting boven AOW-leeftijd is benaderd via schaalfactor "
            f"({factor:.3f}); exacte AOW-segmenttabel nog niet in params."
        )
    return bedrag, benaderingen


def iack(persoon: Persoon, p: Params, *, is_minstverdienende: bool) -> float:
    """Inkomensafhankelijke combinatiekorting (art. 8.14a).

    Recht: kind < kind_max_leeftijd, recht behouden (kind geboren < 2025),
    arbeidsinkomen boven de drempel, en (bij partners) de minstverdienende partner.
    """
    cfg = p.heffingskortingen["iack"]
    kind = persoon.jongste_kind_leeftijd
    if kind is None or kind >= cfg["kind_max_leeftijd"]:
        return 0.0
    if not persoon.iack_recht_behouden:
        return 0.0
    if persoon.heeft_fiscale_partner and not is_minstverdienende:
        return 0.0
    inkomen = persoon.arbeidsinkomen
    if inkomen <= cfg["drempel"]:
        return 0.0
    max_bedrag = cfg["vanaf_aow_max"] if persoon.aow_gerechtigd else cfg["max"]
    bedrag = cfg["opbouw_pct"] * (inkomen - cfg["drempel"])
    return round(min(bedrag, max_bedrag), 2)


def ouderenkorting(verzamelinkomen: float, persoon: Persoon, p: Params) -> float:
    if not persoon.aow_gerechtigd:
        return 0.0
    cfg = p.heffingskortingen["ouderen"]
    return _afbouw(cfg["max"], verzamelinkomen, cfg["afbouw_start"], cfg["afbouw_pct"])


def bereken_heffingskortingen(
    persoon: Persoon,
    verzamelinkomen: float,
    p: Params,
    *,
    is_minstverdienende: bool = True,
) -> Heffingskortingen:
    benaderingen: list[str] = []

    ahk = algemene_heffingskorting(verzamelinkomen, persoon, p)
    ak, ak_benaderingen = arbeidskorting(persoon, p)
    benaderingen.extend(ak_benaderingen)
    iack_bedrag = iack(persoon, p, is_minstverdienende=is_minstverdienende)
    ouderen = ouderenkorting(verzamelinkomen, persoon, p)

    alleenstaande_ouderen = 0.0
    if persoon.aow_gerechtigd and persoon.recht_alleenstaande_ouderenkorting:
        alleenstaande_ouderen = float(
            p.heffingskortingen["alleenstaande_ouderen"]["bedrag"]
        )

    jonggehandicapten = 0.0
    if persoon.recht_jonggehandicaptenkorting:
        # Niet combineerbaar met ouderenkorting.
        if ouderen == 0.0:
            jonggehandicapten = float(
                p.heffingskortingen["jonggehandicapten"]["bedrag"]
            )
        else:
            benaderingen.append(
                "Jonggehandicaptenkorting niet toegepast: niet combineerbaar met "
                "ouderenkorting."
            )

    return Heffingskortingen(
        algemene=ahk,
        arbeids=ak,
        iack=iack_bedrag,
        ouderen=ouderen,
        alleenstaande_ouderen=alleenstaande_ouderen,
        jonggehandicapten=jonggehandicapten,
        benaderingen=benaderingen,
    )
