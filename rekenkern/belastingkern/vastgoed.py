"""Verhuurd vastgoed: box 3 vs. BV — jaarlijkse belastingdruk + eenmalige/exit-kosten.

Vereenvoudigd model (het box 3-vastgoedregime wijzigt bovendien per 2027/2028):
- **Box 3**: forfaitaire heffing over de WOZ × leegwaarderatio − schuld (geen aparte heffing op de
  huur). Tegenbewijs (werkelijk rendement) niet meegerekend.
- **BV**: Vpb over de huurwinst (huur − kosten); geen box 3. Bij uitkeren komt box 2 erbovenop.
  Afschrijving beperkt tot de WOZ-bodemwaarde → hier conservatief buiten beschouwing.
- **Eenmalig**: overdrachtsbelasting bij aankoop/inbreng in een BV.
"""

from __future__ import annotations

from .box3 import leegwaarde
from .params import laad_params


def vergelijk_vastgoed(jaar: int, *, woz: float, jaarhuur: float, kosten: float = 0.0,
                       schuld: float = 0.0, is_woning: bool = True) -> dict:
    p = laad_params(jaar)
    lw = leegwaarde(woz, jaarhuur, p)
    netto_box3_waarde = max(0.0, lw - schuld)
    forfait = p.box3["forfait"]["overige_bezittingen"]
    tarief3 = p.box3["tarief"]
    box3_heffing = round(netto_box3_waarde * forfait * tarief3, 2)  # jaarlijks, forfaitair

    netto_huur = max(0.0, jaarhuur - kosten)
    vpb = p["vpb"]["schijven"][0]["tarief"]          # laag Vpb-tarief (eerste schijf)
    box2 = p["box2"]["schijven"][0]["tarief"]        # laag box 2-tarief
    bv_vpb = round(netto_huur * vpb, 2)                             # jaarlijks, in de BV gehouden
    bv_uitgekeerd = round(netto_huur * (vpb + (1 - vpb) * box2), 2)  # jaarlijks, volledig uitgekeerd

    ovb_pct = p["overdrachtsbelasting"]["verhuurde_woning" if is_woning else "niet_woning"]
    overdrachtsbelasting = round(woz * ovb_pct, 2)   # eenmalig bij aankoop/inbreng in de BV

    return {
        "jaar": jaar, "woz": round(woz, 2), "leegwaarde": round(lw, 2),
        "netto_box3_waarde": round(netto_box3_waarde, 2), "netto_huur": round(netto_huur, 2),
        "box3_heffing": box3_heffing,
        "bv_vpb": bv_vpb, "bv_uitgekeerd": bv_uitgekeerd,
        "vpb_tarief": vpb, "box2_tarief": box2,
        "overdrachtsbelasting": overdrachtsbelasting, "ovb_pct": ovb_pct,
        "beste": "box3" if box3_heffing <= bv_vpb else "bv",  # jaarlijks, BV in de BV gehouden
    }
