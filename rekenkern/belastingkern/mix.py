"""Mix: gegeven een VAST dienstverband (loon) én de volledige situatie (partner, box 3,
eigen woning, kinderen), wat is de gunstigste vorm voor EXTRA inkomen (freelance/
onderneming) dat marginaal bovenop het loon stapelt?

Drie opties voor de extra economische waarde W:
1. **meer loon** — W als (extra) dienstverband: W tegen je marginale box 1-tarief.
2. **ZZP ernaast** — W als winst uit onderneming (MKB-winstvrijstelling; zelfstandigenaftrek
   alleen bij urencriterium, lastig naast een baan).
3. **BV ernaast** — gebruikelijk loon uit de BV + dividend (Vpb + box 2). Bij een kleine
   bijverdienste (< normbedrag) gaat alles op aan gebruikelijk loon → geen dividendvoordeel.

Per optie wordt de VOLLEDIGE situatie doorgerekend: persoon (incl. eigen woning + box 3)
+ partner + huishoudtoeslagen → netto besteedbaar van het huishouden. Ranking op dat netto.
Zvw/WW-marginaal niet meegenomen (vaak al afgetopt door het vaste loon) — als waarschuwing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .box1 import _heffing_over
from .dga import bepaal_gebruikelijk_loon
from .engine import bereken_persoon
from .model import Box3Vermogen, EigenWoning, Onderneming, Persoon
from .params import laad_params
from .toeslagen import Huishoudprofiel, bereken_toeslagen


@dataclass
class MixOptie:
    naam: str
    label: str
    marginale_belasting: float    # extra t.o.v. alleen het vaste loon (persoon)
    netto_extra: float
    marginaal_tarief: float
    huishouden_belasting: float   # totale heffing huishouden (persoon + partner)
    huishouden_netto: float       # volledige situatie: inkomen - heffing + toeslagen
    gemiddelde_druk: float        # huishouden_belasting / huishoudinkomen
    componenten: dict = field(default_factory=dict)  # belastbaar/heffing/vpb/box2 per vorm


@dataclass
class MixResultaat:
    jaar: int
    vast_loon: float
    extra_waarde: float
    opties: list[MixOptie]
    detail_beste: dict = field(default_factory=dict)   # volledige uitsplitsing beste optie
    waarschuwingen: list[str] = field(default_factory=list)

    @property
    def beste(self) -> MixOptie:
        return max(self.opties, key=lambda o: o.huishouden_netto)


def _ond(winst, urencriterium):
    return Onderneming(winst=winst, voldoet_urencriterium=urencriterium) if winst else None


def _persoon_en_heffing(
    naam, vast_loon, vast_winst, extra, jaar, p, *,
    urencriterium, gl_override, eigen_woning, box3, bv_overhead
):
    """Geef (persoonheffing incl. Vpb/overhead, verzamelinkomen) voor één vorm van de extra.
    `vast_winst` = bestaande winst uit onderneming (basis); de extra komt daar bovenop."""
    dividend = 0.0
    extra_heffing = 0.0
    if naam == "meer_loon":
        persoon = Persoon(loon=vast_loon + extra, onderneming=_ond(vast_winst, urencriterium),
                          eigen_woning=eigen_woning, box3=box3)
    elif naam == "zzp":
        persoon = Persoon(loon=vast_loon,
                          onderneming=_ond(vast_winst + extra, urencriterium),
                          eigen_woning=eigen_woning, box3=box3)
    else:  # bv
        gl = bepaal_gebruikelijk_loon(extra, p, hoger_loon=gl_override or 0.0)
        winst_voor_vpb = max(0.0, extra - gl)
        vpb = _heffing_over(winst_voor_vpb, p["vpb"]["schijven"])
        dividend = winst_voor_vpb - vpb
        overhead = 0.0
        if bv_overhead:
            ok = p["oprichtingskosten_indicatief"]
            overhead = (p["vaste_kosten_indicatief"]["dga"]
                        + ok["dga"] / ok["standaard_horizon_jaren"])  # jaarlijks + geamortiseerde oprichting
        extra_heffing = vpb + overhead
        persoon = Persoon(loon=vast_loon + gl, onderneming=_ond(vast_winst, urencriterium),
                          eigen_woning=eigen_woning, box3=box3)
    r = bereken_persoon(persoon, p, box2_inkomen=dividend)
    comp = {
        "belastbaar_box1": r.box1.belastbaar_inkomen,
        "heffing_box1": r.box1.belasting_en_premies,
        "box2_belasting": r.box2_belasting,
        "te_betalen": round(r.te_betalen + extra_heffing, 2),
    }
    if naam == "bv":
        comp.update({"gebruikelijk_loon": round(gl, 2), "vpb": round(vpb, 2),
                     "dividend": round(dividend, 2), "bv_kosten": round(extra_heffing - vpb, 2)})
    return round(r.te_betalen + extra_heffing, 2), r.verzamelinkomen, r, round(extra_heffing, 2), comp


def box3_detail(r) -> dict:
    """Uitsplitsing van de box 3-heffing, zodat het bedrag herleidbaar is."""
    b3 = r.box3
    return {
        "grondslag": b3.rendementsgrondslag,
        "heffingvrij": round(b3.rendementsgrondslag - b3.grondslag_na_heffingvrij, 2),
        "effectief_rendementspercentage": b3.effectief_rendementspercentage,
        "belasting": b3.belasting,
        "tegenbewijs": b3.tegenbewijs_toegepast,
    }


def _persoon_detail(r, bruto: float, vpb_overhead: float) -> dict:
    return {
        "bruto_inkomen": round(bruto, 2),
        "belastbaar_box1": r.box1.belastbaar_inkomen,
        "heffing_box1": r.box1.belasting_en_premies,
        "heffing_box3": r.box3.belasting,
        "box3": box3_detail(r),
        "box2_belasting": r.box2_belasting,
        "vpb_overhead": vpb_overhead,
        "verzilverd": r.verzilverde_korting,
        "te_betalen": round(r.te_betalen + vpb_overhead, 2),
    }


def bereken_mix(
    vast_loon: float,
    extra_waarde: float,
    jaar: int,
    *,
    vast_winst: float = 0.0,
    urencriterium: bool = False,
    gebruikelijk_loon: float | None = None,
    eigen_woning: EigenWoning | None = None,
    box3: Box3Vermogen | None = None,
    partner_inkomen: float = 0.0,
    profiel: Huishoudprofiel | None = None,
    bv_overhead: bool = True,
) -> MixResultaat:
    p = laad_params(jaar)
    ew = eigen_woning or EigenWoning()
    b3 = box3 or Box3Vermogen()

    # Partner (constant over de opties) en basis (alleen vast loon, zelfde context).
    partner_r = bereken_persoon(Persoon(loon=partner_inkomen), p) if partner_inkomen else None
    partner_tax = partner_r.te_betalen if partner_r else 0.0
    partner_vi = partner_r.verzamelinkomen if partner_r else 0.0
    basis_tax, *_ = _persoon_en_heffing(
        "meer_loon", vast_loon, vast_winst, 0.0, jaar, p, urencriterium=urencriterium,
        gl_override=gebruikelijk_loon, eigen_woning=ew, box3=b3, bv_overhead=bv_overhead,
    )
    inkomen = vast_loon + vast_winst + extra_waarde + partner_inkomen

    opties = []
    details = {}   # naam -> (resultaat, vpb_overhead, toeslagen)
    for naam, label in [
        ("meer_loon", "Extra als loon (meer/ander dienstverband)"),
        ("zzp", "Eigen onderneming (ZZP) naast loon"),
        ("bv", "Eigen BV naast loon"),
    ]:
        ptax, vi, r_opt, vpb_overhead, comp = _persoon_en_heffing(
            naam, vast_loon, vast_winst, extra_waarde, jaar, p, urencriterium=urencriterium,
            gl_override=gebruikelijk_loon, eigen_woning=ew, box3=b3, bv_overhead=bv_overhead,
        )
        toeslagen = (
            bereken_toeslagen(vi + partner_vi, p, profiel=profiel).totaal if profiel else 0.0
        )
        details[naam] = (r_opt, vpb_overhead, toeslagen)
        marg = round(ptax - basis_tax, 2)
        h_belasting = round(ptax + partner_tax, 2)
        opties.append(MixOptie(
            naam=naam, label=label, marginale_belasting=marg,
            netto_extra=round(extra_waarde - marg, 2),
            marginaal_tarief=round(marg / extra_waarde, 4) if extra_waarde else 0.0,
            huishouden_belasting=h_belasting,
            huishouden_netto=round(inkomen - h_belasting + toeslagen, 2),
            gemiddelde_druk=round(h_belasting / inkomen, 4) if inkomen else 0.0,
            componenten=comp,
        ))

    beste = max(opties, key=lambda o: o.huishouden_netto)
    r_opt, vpb_overhead, toeslagen = details[beste.naam]
    detail_beste = {
        "vorm": beste.naam,
        "persoon": _persoon_detail(r_opt, vast_loon + vast_winst + extra_waarde, vpb_overhead),
        "partner": _persoon_detail(partner_r, partner_inkomen, 0.0) if partner_r else None,
        "toeslagen": round(toeslagen, 2),
        "huishouden": {"te_betalen": beste.huishouden_belasting, "netto": beste.huishouden_netto},
    }

    waarschuwingen = [
        "Marginale vergelijking (IB/PVV + Vpb/box 2 + BV-overhead). Zvw/WW niet meegenomen "
        "— vaak al afgetopt door het vaste loon.",
        "Zelfstandigenaftrek vereist het urencriterium (1.225 uur) — lastig naast een baan.",
        "BV-afscherming van privévermogen is beperkt: banken eisen vaak een persoonlijke "
        "borgstelling en bestuurdersaansprakelijkheid kan privé doorwerken.",
    ]
    if bepaal_gebruikelijk_loon(extra_waarde, p, hoger_loon=gebruikelijk_loon or 0.0) >= extra_waarde:
        waarschuwingen.append(
            "Bij deze bijverdienste gaat (bijna) alles op aan gebruikelijk loon → geen "
            "dividendvoordeel; de BV is dan vooral overhead."
        )
    if profiel and profiel.aantal_kinderen:
        if detail_beste["toeslagen"] == 0:
            waarschuwingen.append(
                "Geen zorg-/huur-/kindgebonden budget bij dit inkomen (boven de afbouwgrenzen)."
            )
        waarschuwingen.append(
            "Kinderopvangtoeslag is niet meegerekend (situationeel: opvanguren/-tarief; "
            "géén harde inkomensgrens, ook hoge inkomens krijgen ~36,5%)."
        )
    return MixResultaat(
        jaar=jaar, vast_loon=vast_loon, extra_waarde=extra_waarde,
        opties=opties, detail_beste=detail_beste, waarschuwingen=waarschuwingen,
    )
