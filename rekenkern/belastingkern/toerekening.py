"""Partnertoerekening (art. 2.17): optimale verdeling van gemeenschappelijke
inkomensbestanddelen tussen fiscale partners.

v1 optimaliseert de **eigen woning** (saldo EWF − hypotheekrente − Hillen), het
bestanddeel met de meeste verdeelruimte. De optimizer zoekt de verdeelfractie die de
totale box 1-heffing van het huishouden minimaliseert.

Let op:
- **Toeslagen** zijn invariant onder toerekening (ze gebruiken het gezamenlijke
  toetsingsinkomen) — daarom hier buiten beschouwing.
- **Box 3-grondslag** mag óók vrij verdeeld worden, maar de totale box 3-heffing is voor
  partners (2× heffingvrij vermogen, vlak 36%) feitelijk verdeling-invariant; het effect
  loopt alleen via de afbouw van de algemene heffingskorting (tweede orde) — nog niet in
  deze optimizer.
"""

from __future__ import annotations

from dataclasses import dataclass

from .engine import bereken_persoon
from .model import EigenWoning, Persoon
from .params import laad_params


@dataclass
class ToerekeningResultaat:
    optimale_fractie_partner_a: float   # deel eigen woning bij partner A
    totaal_optimaal: float
    totaal_5050: float
    besparing_vs_5050: float
    toelichting: str


def optimale_eigenwoning_verdeling(
    inkomen_a: float,
    inkomen_b: float,
    woz_waarde: float,
    hypotheekrente: float,
    jaar: int,
    *,
    stappen: int = 20,
) -> ToerekeningResultaat:
    """Zoek de verdeling van de eigen woning over twee partners (vaste arbeidsinkomens)
    die de totale box 1-heffing minimaliseert."""
    p = laad_params(jaar)

    def totaal_bij(fractie_a: float) -> float:
        a = bereken_persoon(
            Persoon(loon=inkomen_a, eigen_woning=EigenWoning(
                woz_waarde=woz_waarde * fractie_a,
                betaalde_hypotheekrente=hypotheekrente * fractie_a,
            )),
            p,
        )
        b = bereken_persoon(
            Persoon(loon=inkomen_b, eigen_woning=EigenWoning(
                woz_waarde=woz_waarde * (1 - fractie_a),
                betaalde_hypotheekrente=hypotheekrente * (1 - fractie_a),
            )),
            p,
        )
        return round(a.te_betalen + b.te_betalen, 2)

    beste_f, beste_totaal = 0.5, totaal_bij(0.5)
    for i in range(stappen + 1):
        f = i / stappen
        t = totaal_bij(f)
        if t < beste_totaal:
            beste_f, beste_totaal = f, t

    totaal_5050 = totaal_bij(0.5)
    besparing = round(totaal_5050 - beste_totaal, 2)

    if besparing < 1:
        toel = "Verdeling maakt nauwelijks uit (aftrek bij beiden afgetopt op 37,56%)."
    elif beste_f >= 0.99:
        toel = "Reken de eigen woning volledig toe aan partner A (hoogste verzilverbare heffing)."
    elif beste_f <= 0.01:
        toel = "Reken de eigen woning volledig toe aan partner B."
    else:
        toel = f"Optimale verdeling: {beste_f:.0%} bij partner A."

    return ToerekeningResultaat(
        optimale_fractie_partner_a=round(beste_f, 3),
        totaal_optimaal=beste_totaal,
        totaal_5050=totaal_5050,
        besparing_vs_5050=besparing,
        toelichting=toel,
    )
