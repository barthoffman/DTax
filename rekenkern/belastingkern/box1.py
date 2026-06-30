"""Box 1: belastbaar inkomen uit werk en woning + tarief.

Wet IB 2001 hoofdstuk 3 (inkomen), art. 2.10/2.10a (tarief), art. 3.112 (EWF),
art. 3.120 (rente eigen woning), art. 3.123a (Hillen), art. 2.10 lid 6/7
(tariefsaanpassing aftrek eigen woning).
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Persoon
from .params import Params


@dataclass
class EigenWoningResultaat:
    eigenwoningforfait: float
    aftrekbare_rente: float
    hillen_aftrek: float
    saldo: float  # positief = bijtelling, negatief = aftrek (inkomen uit eigen woning)


@dataclass
class Box1Resultaat:
    arbeidsinkomen: float
    eigen_woning: EigenWoningResultaat
    belastbaar_inkomen: float
    belasting_en_premies: float          # gecombineerde heffing box 1 (excl. kortingen)
    tariefsaanpassing_eigen_woning: float  # bijtelling wegens afgetopte aftrek (art. 2.10)
    schijf1_premiedeel: float            # premies volksverzekeringen in schijf 1
    schijf1_belastingdeel: float
    toelichting: list[str]


def _eigenwoningforfait(woz: float, p: Params) -> float:
    ewf = p.box1["eigenwoningforfait"]
    grens = ewf["woz_grens_villa"]
    if woz <= grens:
        return round(woz * ewf["percentage"], 2)
    return round(ewf["villa_vast_bedrag"] + (woz - grens) * ewf["villa_percentage"], 2)


def bereken_eigen_woning(persoon: Persoon, p: Params) -> EigenWoningResultaat:
    """Saldo inkomen uit eigen woning incl. Hillen-aftrek (art. 3.123a)."""
    w = persoon.eigen_woning
    ewf = _eigenwoningforfait(w.woz_waarde, p)
    rente = w.betaalde_hypotheekrente
    hillen = 0.0
    if ewf > rente:
        # Aftrek wegens geen/geringe eigenwoningschuld: percentage van (EWF - kosten).
        hillen = round((ewf - rente) * p.box1["hillen_percentage"], 2)
    saldo = round(ewf - rente - hillen, 2)
    return EigenWoningResultaat(
        eigenwoningforfait=ewf,
        aftrekbare_rente=rente,
        hillen_aftrek=hillen,
        saldo=saldo,
    )


def _schijven(persoon: Persoon, p: Params) -> list[dict]:
    key = "schijven_vanaf_aow" if persoon.aow_gerechtigd else "schijven_onder_aow"
    return p.box1[key]


def _heffing_over(inkomen: float, schijven: list[dict]) -> float:
    """Progressieve heffing; `tot` = None betekent geen bovengrens."""
    heffing = 0.0
    ondergrens = 0.0
    for schijf in schijven:
        boven = schijf["tot"] if schijf["tot"] is not None else float("inf")
        if inkomen <= ondergrens:
            break
        deel = min(inkomen, boven) - ondergrens
        heffing += deel * schijf["tarief"]
        ondergrens = boven
    return heffing


def bereken_box1(
    persoon: Persoon, p: Params, *, extra_aftrek_2_10a: float = 0.0
) -> Box1Resultaat:
    """`extra_aftrek_2_10a`: aftrek die naast de eigen woning onder de tariefaanpassing
    van art. 2.10a valt (ondernemersaftrek + MKB-winstvrijstelling)."""
    toelichting: list[str] = []
    ew = bereken_eigen_woning(persoon, p)

    inkomen_voor_ew = (
        persoon.box1_bruto_inkomen - persoon.aftrekposten_box1
    )
    belastbaar = round(inkomen_voor_ew + ew.saldo, 2)
    belastbaar = max(0.0, belastbaar)  # box 1 wordt niet negatief belast

    schijven = _schijven(persoon, p)
    heffing = _heffing_over(belastbaar, schijven)

    # Premiedeel/belastingdeel van schijf 1 (informatief).
    premies = p.box1["premies_volksverzekeringen_schijf1"]
    premie_tarief = 0.0 if persoon.aow_gerechtigd else (
        premies["aow"] + premies["anw"] + premies["wlz"]
    )
    schijf1_grens = schijven[0]["tot"] or 0
    schijf1_grondslag = min(belastbaar, schijf1_grens)
    schijf1_premiedeel = round(schijf1_grondslag * premie_tarief, 2)
    schijf1_belastingdeel = round(
        schijf1_grondslag * schijven[0]["tarief"] - schijf1_premiedeel, 2
    )

    # Tariefaanpassing (art. 2.10a): aftrek die feitelijk tegen het toptarief is genoten,
    # wordt teruggenomen tot het max. aftrektarief. Geldt voor eigenwoningaftrek én
    # ondernemersaftrek/MKB-winstvrijstelling (meegegeven via extra_aftrek_2_10a).
    tariefsaanpassing = 0.0
    aftrek_ew = max(0.0, -ew.saldo)  # netto aftrek uit eigen woning
    totale_aftrek_2_10a = aftrek_ew + max(0.0, extra_aftrek_2_10a)
    if totale_aftrek_2_10a > 0:
        toptarief = schijven[-1]["tarief"]
        max_aftrek = p.box1["hra_max_aftrektarief"]
        schijf2_grens = schijven[1]["tot"] or float("inf")
        # Inkomen vóór deze aftrekposten bepaalt hoeveel ervan in de topschijf viel.
        inkomen_voor_aftrek = belastbaar + totale_aftrek_2_10a
        aftrek_in_top = min(
            totale_aftrek_2_10a, max(0.0, inkomen_voor_aftrek - schijf2_grens)
        )
        if aftrek_in_top > 0:
            tariefsaanpassing = round(aftrek_in_top * (toptarief - max_aftrek), 2)
            toelichting.append(
                f"Tariefaanpassing (art. 2.10a): € {tariefsaanpassing:.2f} bijtelling "
                f"over € {aftrek_in_top:.0f} aftrek in de topschijf."
            )

    if ew.hillen_aftrek > 0:
        toelichting.append(
            f"Hillen-aftrek (art. 3.123a): € {ew.hillen_aftrek:.2f} "
            f"({p.box1['hillen_percentage']:.2%} van EWF − rente)."
        )

    totaal = round(heffing + tariefsaanpassing, 2)
    return Box1Resultaat(
        arbeidsinkomen=persoon.arbeidsinkomen,
        eigen_woning=ew,
        belastbaar_inkomen=belastbaar,
        belasting_en_premies=totaal,
        tariefsaanpassing_eigen_woning=tariefsaanpassing,
        schijf1_premiedeel=schijf1_premiedeel,
        schijf1_belastingdeel=schijf1_belastingdeel,
        toelichting=toelichting,
    )
