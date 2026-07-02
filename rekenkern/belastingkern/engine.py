"""Engine: voegt box 1, box 3 en heffingskortingen samen tot het eindresultaat.

Verzilvering (art. 8.8 Wet IB 2001): de gecombineerde heffingskorting kan niet hoger
zijn dan de gecombineerde inkomensheffing (box 1 + box 3). Het meerdere verdampt
(behoudens uitbetaling minstverdienende partner, art. 8.9 — nog niet gemodelleerd).
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from .box1 import Box1Resultaat, bereken_box1, _heffing_over
from .box3 import Box3Resultaat, bereken_box3
from .heffingskortingen import Heffingskortingen, bereken_heffingskortingen
from .model import Huishouden, Persoon
from .onderneming import OndernemingResultaat, bereken_onderneming
from .params import Params, laad_params


@dataclass
class ResultaatPersoon:
    naam: str
    jaar: int
    box1: Box1Resultaat
    box3: Box3Resultaat
    kortingen: Heffingskortingen
    onderneming: OndernemingResultaat | None
    box2_inkomen: float
    box2_belasting: float
    verzamelinkomen: float
    gecombineerde_heffing_voor_kortingen: float
    verzilverde_korting: float
    verdampte_korting: float
    te_betalen: float
    waarschuwingen: list[str] = field(default_factory=list)

    def samenvatting(self) -> str:
        regels = [
            f"=== {self.naam} — belastingjaar {self.jaar} ===",
            f"Belastbaar inkomen box 1 : € {self.box1.belastbaar_inkomen:>12,.2f}",
            f"Heffing box 1            : € {self.box1.belasting_en_premies:>12,.2f}",
            f"Heffing box 3            : € {self.box3.belasting:>12,.2f}",
            f"Box 2-inkomen/heffing    : € {self.box2_inkomen:>12,.2f} / "
            f"€ {self.box2_belasting:,.2f}",
            f"Verzamelinkomen          : € {self.verzamelinkomen:>12,.2f}",
            f"Heffingskortingen        : € {self.kortingen.totaal:>12,.2f}"
            f"  (verzilverd € {self.verzilverde_korting:,.2f})",
            f"  - algemene             : € {self.kortingen.algemene:>12,.2f}",
            f"  - arbeids              : € {self.kortingen.arbeids:>12,.2f}",
            f"  - iack                 : € {self.kortingen.iack:>12,.2f}",
            f"  - ouderen              : € {self.kortingen.ouderen:>12,.2f}",
            f"  - alleenst. ouderen    : € {self.kortingen.alleenstaande_ouderen:>12,.2f}",
            f"  - jonggehandicapten    : € {self.kortingen.jonggehandicapten:>12,.2f}",
            f"TE BETALEN (IB/PVV)      : € {self.te_betalen:>12,.2f}",
        ]
        if self.verdampte_korting > 0:
            regels.append(
                f"  ! € {self.verdampte_korting:,.2f} heffingskorting verdampt "
                "(niet verzilverbaar)."
            )
        for w in self.waarschuwingen:
            regels.append(f"  * {w}")
        return "\n".join(regels)


def bereken_persoon(
    persoon: Persoon,
    jaar: int | Params,
    *,
    is_minstverdienende: bool = True,
    box3_aandeel: float = 1.0,
    box2_inkomen: float = 0.0,
) -> ResultaatPersoon:
    """`box2_inkomen`: regulier voordeel uit aanmerkelijk belang (bv. dividend DGA).
    Telt mee in het verzamelinkomen (afbouw heffingskortingen) en wordt apart belast."""
    p = jaar if isinstance(jaar, Params) else laad_params(jaar)

    # Volledige ondernemersroute: winst → belastbare winst (incl. ondernemersaftrek/MKB).
    onderneming_resultaat: OndernemingResultaat | None = None
    extra_aftrek_2_10a = 0.0
    eff = persoon
    if persoon.onderneming is not None:
        onderneming_resultaat = bereken_onderneming(persoon.onderneming, p)
        extra_aftrek_2_10a = onderneming_resultaat.aftrek_onder_2_10a
        eff = dataclasses.replace(
            persoon,
            winst_uit_onderneming=persoon.winst_uit_onderneming
            + onderneming_resultaat.belastbare_winst,
            onderneming=None,
        )

    # Persoonsgebonden aftrek (giften/alimentatie/zorgkosten): verlaagt box 1 én valt onder de
    # tariefaanpassing van art. 2.10a → in aftrekposten_box1 (inkomensverlaging) + extra_aftrek_2_10a.
    if eff.persoonsgebonden_aftrek:
        extra_aftrek_2_10a += eff.persoonsgebonden_aftrek
        eff = dataclasses.replace(
            eff,
            aftrekposten_box1=eff.aftrekposten_box1 + eff.persoonsgebonden_aftrek,
            persoonsgebonden_aftrek=0.0,
        )

    box1 = bereken_box1(eff, p, extra_aftrek_2_10a=extra_aftrek_2_10a)
    box3 = bereken_box3(
        eff.box3,
        p,
        heeft_fiscale_partner=eff.heeft_fiscale_partner,
        aandeel=box3_aandeel,
    )

    # Box 2 (aanmerkelijk belang): apart tarief, telt mee in het verzamelinkomen.
    box2_belasting = round(_heffing_over(box2_inkomen, p["box2"]["schijven"]), 2)

    # Verzamelinkomen = belastbaar box 1 + box 3-voordeel + box 2-inkomen.
    box3_voordeel = round(box3.belasting / p.box3["tarief"], 2) if p.box3["tarief"] else 0.0
    verzamelinkomen = round(box1.belastbaar_inkomen + box3_voordeel + box2_inkomen, 2)

    kortingen = bereken_heffingskortingen(
        eff, verzamelinkomen, p, is_minstverdienende=is_minstverdienende
    )

    gecombineerde_heffing = round(
        box1.belasting_en_premies + box3.belasting + box2_belasting, 2
    )
    # Verzilvering (art. 8.8): korting maximaal de verschuldigde heffing.
    verzilverd = min(kortingen.totaal, gecombineerde_heffing)
    verdampt = round(kortingen.totaal - verzilverd, 2)
    te_betalen = round(gecombineerde_heffing - verzilverd, 2)

    waarschuwingen = list(box3.waarschuwingen) + list(box1.toelichting) + list(
        kortingen.benaderingen
    )
    if onderneming_resultaat is not None:
        waarschuwingen += list(onderneming_resultaat.toelichting)

    return ResultaatPersoon(
        naam=persoon.naam,
        jaar=p.jaar,
        box1=box1,
        box3=box3,
        kortingen=kortingen,
        onderneming=onderneming_resultaat,
        box2_inkomen=round(box2_inkomen, 2),
        box2_belasting=box2_belasting,
        verzamelinkomen=verzamelinkomen,
        gecombineerde_heffing_voor_kortingen=gecombineerde_heffing,
        verzilverde_korting=verzilverd,
        verdampte_korting=verdampt,
        te_betalen=te_betalen,
        waarschuwingen=waarschuwingen,
    )


def bereken_huishouden(
    huishouden: Huishouden, jaar: int
) -> list[ResultaatPersoon]:
    """Bereken beide partners. v1: geen automatische toerekening-optimalisatie;
    inkomsten/vermogen worden genomen zoals ingevuld per persoon."""
    p = laad_params(jaar)
    resultaten: list[ResultaatPersoon] = []

    personen = [huishouden.persoon]
    if huishouden.partner is not None:
        personen.append(huishouden.partner)

    # Bepaal de minstverdienende partner (voor IACK) op arbeidsinkomen.
    if len(personen) == 2:
        minst = min(personen, key=lambda x: x.arbeidsinkomen)
    else:
        minst = personen[0]

    for persoon in personen:
        resultaten.append(
            bereken_persoon(
                persoon, p, is_minstverdienende=(persoon is minst)
            )
        )
    return resultaten
