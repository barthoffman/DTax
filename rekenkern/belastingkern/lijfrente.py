"""Meerjarige lijfrente-doorrekening (derde pijler) vs. privé beleggen in box 3.

De vraag: levert € X in een lijfrente/pensioenbeleggingsrekening stoppen méér op dan
hetzelfde bedrag privé beleggen — over een horizon tot aan je pensioen?

Twee routes voor dezelfde € inleg (pre-tax):
- **Lijfrente**: de volledige inleg is aftrekbaar (geen belasting nu) en groeit
  belastingvrij (géén box 3, géén Vpb). Bij opname box 1 tegen je pensioentarief.
- **Privé**: je betaalt eerst belasting over de inleg (marginaal tarief), belegt het
  ná-belaste bedrag en betaalt jaarlijks box 3 over (vermogen − heffingvrij).

Drijvende krachten: lijfrente belegt een grotere (pre-tax) basis én groeit belastingvrij,
maar betaalt aan het eind box 1. Privé belegt een kleinere basis, jaarlijks belast, geen
eindheffing. Het verschil hangt af van het tariefverschil nu↔opname en het heffingvrij
vermogen (dat de privé-route bij kleine bedragen bijna belastingvrij maakt).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .params import laad_params


@dataclass
class LijfrenteResultaat:
    jaar: int
    inleg: float
    rendement_pct: float
    jaren: int
    marginaal_nu: float
    tarief_uit: float
    lijfrente_eindnetto: float
    prive_eindnetto: float
    voordeel: float                 # lijfrente − privé (positief = lijfrente gunstiger)
    breakeven_tarief_uit: float     # opnametarief waaronder lijfrente wint
    overig_pensioen: float = 0.0    # verwacht AOW + 2e-pijler pensioen (box 1, €/jaar)
    uitkering_per_jaar: float = 0.0 # lijfrente-uitkering per jaar (pot ÷ uitkeringsjaren)
    tarief_uit_berekend: bool = False  # opnametarief afgeleid uit overig_pensioen i.p.v. aanname
    waarschuwingen: list[str] = field(default_factory=list)


def _heffing_box1_aow(schijven: list, inkomen: float) -> float:
    """Progressieve box 1-heffing (AOW-tarieven) over een inkomen."""
    h, vorig = 0.0, 0.0
    for s in schijven:
        tot = s["tot"] if s["tot"] is not None else float("inf")
        if inkomen > vorig:
            h += (min(inkomen, tot) - vorig) * s["tarief"]
        vorig = tot
        if inkomen <= tot:
            break
    return h


def _opnametarief(p, overig_pensioen: float, uitkering_pj: float) -> float:
    """Blended box 1-tarief op de lijfrente-uitkering, gestapeld op het overige pensioen."""
    schijven = p["box1"]["schijven_vanaf_aow"]
    if uitkering_pj <= 0:
        return schijven[0]["tarief"]
    h_base = _heffing_box1_aow(schijven, overig_pensioen)
    h_top = _heffing_box1_aow(schijven, overig_pensioen + uitkering_pj)
    return (h_top - h_base) / uitkering_pj


def vergelijk_lijfrente(
    inleg: float,
    rendement_pct: float,
    jaren: int,
    jaar: int,
    *,
    marginaal_nu: float = 0.3756,
    tarief_uit: float = 0.1785,
    overig_pensioen: float | None = None,
    uitkeringsjaren: int = 20,
    tegenbewijs: bool = True,
    partner: bool = False,
) -> LijfrenteResultaat:
    p = laad_params(jaar)
    b3 = p.box3
    forfait = b3["forfait"]["overige_bezittingen"]
    tarief3 = b3["tarief"]
    heffingvrij = b3["heffingvrij_vermogen_pp"] * (2 if partner else 1)
    pct3 = min(forfait, rendement_pct) if tegenbewijs else forfait

    # Lijfrente: volledige inleg groeit belastingvrij; bij opname box 1 @ tarief_uit.
    lijf_bruto = inleg * (1 + rendement_pct) ** jaren
    # Realistisch opnametarief: de uitkering (pot ÷ uitkeringsjaren) stapelt op AOW + pensioen.
    uitkering_pj = lijf_bruto / max(1, int(uitkeringsjaren))
    tarief_berekend = overig_pensioen is not None
    if tarief_berekend:
        tarief_uit = round(_opnametarief(p, overig_pensioen, uitkering_pj), 4)
    lijfrente_eind = round(lijf_bruto * (1 - tarief_uit), 2)

    # Privé: inleg eerst belast @ marginaal_nu, daarna jaarlijks box 3 over (vermogen − heffingvrij).
    priv = inleg * (1 - marginaal_nu)
    for _ in range(int(jaren)):
        box3_tax = tarief3 * pct3 * max(0.0, priv - heffingvrij)
        priv += priv * rendement_pct - box3_tax
    prive_eind = round(priv, 2)

    # Opnametarief waaronder lijfrente wint: t* = 1 − privé_eind / lijf_bruto.
    breakeven = round(1 - prive_eind / lijf_bruto, 4) if lijf_bruto > 0 else 0.0

    waarschuwingen = [
        "Lijfrente belegt de volledige (pre-tax) inleg en groeit belastingvrij (geen box 3); "
        "privé beleg je het ná-belaste bedrag, jaarlijks belast in box 3.",
        f"Heffingvrij vermogen (€ {heffingvrij:,.0f}) is op de privé-route toegepast — "
        "conservatief. Heb je al box 3-vermogen daarboven, dan is lijfrente nóg gunstiger.".replace(",", "."),
        "Opnametarief hangt af van je overige pensioeninkomen: bij AOW is schijf 1 lager "
        "(geen AOW-premie), maar bij een grote pot schuift een deel naar het hogere tarief.",
        "Inleg vereist jaarruimte (art. 3.127); het geld staat vast tot pensioen "
        "(revisierente bij vervroegde opname).",
        "Fiscaal gelijk voor lijfrenteverzekering, banksparen én pensioenbeleggen (derde "
        "pijler, afd. 3.7 Wet IB): zelfde aftrek, box 3-vrijstelling en box 1 bij opname. "
        "Verschil zit in het product: banksparen/beleggen keert een vaste termijn uit en gaat "
        "bij overlijden naar de erfgenamen; een verzekering kan levenslang uitkeren maar kan "
        "bij overlijden (zonder restitutie) aan de verzekeraar vervallen. 'Rendement' hier = "
        "sparen (laag) vs beleggen (hoger).",
    ]
    if tarief_berekend:
        waarschuwingen.insert(0,
            f"Opnametarief {tarief_uit*100:.1f}% is berekend: een uitkering van € {uitkering_pj:,.0f}/jaar "
            f"(pot ÷ {int(uitkeringsjaren)} jaar) bovenop € {overig_pensioen:,.0f} AOW + pensioen. "
            "Hoe hoger je overige pensioen, hoe meer van de lijfrente in het 37,56%-tarief valt — "
            "dan kan privé beleggen (box 3) gunstiger worden.".replace(",", "."))

    return LijfrenteResultaat(
        jaar=jaar, inleg=inleg, rendement_pct=rendement_pct, jaren=jaren,
        marginaal_nu=marginaal_nu, tarief_uit=tarief_uit,
        lijfrente_eindnetto=lijfrente_eind, prive_eindnetto=prive_eind,
        voordeel=round(lijfrente_eind - prive_eind, 2), breakeven_tarief_uit=breakeven,
        overig_pensioen=round(overig_pensioen or 0.0, 2), uitkering_per_jaar=round(uitkering_pj, 2),
        tarief_uit_berekend=tarief_berekend, waarschuwingen=waarschuwingen,
    )
