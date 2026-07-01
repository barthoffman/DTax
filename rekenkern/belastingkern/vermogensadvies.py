"""Vermogensallocatie: waar laat je je vermogen het beste renderen?

Combineert de drie 'containers' tot één advies:
- **Lijfrente** (derde pijler): aftrek nu, belastingvrije groei, box 1 bij opname; begrensd
  door de jaarruimte en vast tot pensioen.
- **Box 3** (privé): volledig flexibel; heffingvrij vermogen + tegenbewijs.
- **BV-retentie** (alleen ondernemers): winst oppotten; box 2 bij opname.

Geeft (1) per container de netto-eindwaarde als je de nieuwe inleg daar zou stoppen, (2) een
**watervalallocatie** van de nieuwe inleg die rekening houdt met liquiditeitsbehoefte en
jaarruimte, en (3) analyse van bestaand privé- en BV-vermogen.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .lijfrente import vergelijk_lijfrente
from .optimalisatiemotor import box3_last
from .params import laad_params
from .uitstel import vergelijk_uitstel


@dataclass
class Container:
    naam: str
    label: str
    netto_eind: float        # netto-eindwaarde als de volledige nieuwe inleg hier in gaat
    voorwaarde: str
    max_bedrag: float | None  # plafond (jaarruimte voor lijfrente); None = ongelimiteerd
    soort: str = "privé"      # "privé" | "zakelijk"


def _fv_annuity(bedrag_per_jaar: float, groei: float, jaren: int) -> float:
    """Toekomstige waarde van een jaarlijkse inleg (stortingen einde jaar)."""
    if bedrag_per_jaar <= 0 or jaren <= 0:
        return 0.0
    if abs(groei) < 1e-9:
        return bedrag_per_jaar * jaren
    return bedrag_per_jaar * (((1 + groei) ** jaren - 1) / groei)


def _lijf_cap_persoon(p, *, marginaal, jaarruimte, verwacht_pensioen, bestaande_lijfrente,
                      rendement, jaren, uj):
    """Pensioen-bewuste lijfrente-cap voor één persoon: vul de lijfrente zó dat de toekomstige
    uitkering box 1 vult tot de schijfgrens die net ONDER het marginale tarief nu ligt (daarboven
    geen tariefarbitrage meer). De uitkering stapelt op de verwachte AOW + pensioen van die persoon."""
    schijven_aow = p["box1"]["schijven_vanaf_aow"]
    target_box1 = next((s["tot"] for s in schijven_aow if s["tot"] is not None), 0.0)
    for s in schijven_aow:
        if s["tot"] is not None and s["tarief"] < marginaal:
            target_box1 = s["tot"]
    bestaande_lijf_pot = bestaande_lijfrente * (1 + rendement) ** jaren
    bestaande_lijf_uitkering = bestaande_lijf_pot / uj
    effectief_pensioen = max(0.0, verwacht_pensioen) + bestaande_lijf_uitkering
    target_uitkering = max(0.0, target_box1 - effectief_pensioen)
    fv_factor = _fv_annuity(1.0, rendement, jaren)
    cap_raw = (target_uitkering * uj / fv_factor) if fv_factor > 0 else jaarruimte
    return {
        "marginaal": marginaal, "jaarruimte": jaarruimte,
        "cap": max(0.0, min(jaarruimte, cap_raw)),  # begrensd door de jaarruimte
        "target_box1": target_box1, "bestaande_lijf_pot": bestaande_lijf_pot,
        "bestaande_lijf_uitkering": bestaande_lijf_uitkering, "effectief_pensioen": effectief_pensioen,
        "target_uitkering": target_uitkering,
    }


@dataclass
class VermogensadviesResultaat:
    jaar: int
    nieuwe_inleg: float
    jaren: int
    rendement: float
    containers: list           # gerangschikt op netto_eind
    allocatie: dict            # {lijfrente, box3, bv} aanbevolen bedragen
    bestaand_box3_last: float
    bestaand_bv: dict | None
    liquiditeit_advies: str
    projectie: dict | None = None   # opgebouwde potten + jaarlijkse uitkering bij pensioen
    lijfrente_optimaal: dict | None = None  # pensioen-bewuste cap-uitleg
    herverdeling: dict | None = None  # herverdeling van bestaand spaargeld-overschot
    waarschuwingen: list = field(default_factory=list)


def vermogensadvies(
    jaar: int,
    *,
    nieuwe_inleg: float = 0.0,
    bestaand_box3: float = 0.0,
    bestaand_spaargeld: float = 0.0,
    bestaand_bv_spaargeld: float = 0.0,
    bestaand_bv_beleggingen: float = 0.0,
    rendement: float = 0.06,
    jaren: int = 15,
    marginaal_nu: float = 0.3756,
    tarief_uit: float = 0.1785,
    jaarruimte: float = 0.0,
    vrij_opneembaar: float = 0.0,
    verwacht_pensioen: float = 0.0,
    bestaande_lijfrente: float = 0.0,
    is_ondernemer: bool = False,
    partner: bool = False,
    uitkeringsjaren: int = 20,
    inflatie: float = 0.02,
    partner_marginaal: float = 0.3756,
    partner_jaarruimte: float = 0.0,
    partner_verwacht_pensioen: float = 0.0,
    partner_bestaande_lijfrente: float = 0.0,
    partner_bestaand_box3: float = 0.0,
) -> VermogensadviesResultaat:
    p = laad_params(jaar)
    vpb = p["vpb"]["schijven"][0]["tarief"]
    forfait = p.box3["forfait"]["overige_bezittingen"]
    tarief3 = p.box3["tarief"]
    inleg = max(nieuwe_inleg, 0.0)
    eenheid = max(inleg, 1.0)  # om per-euro te kunnen rekenen zonder /0

    # Netto-eindwaarde per container voor de volledige nieuwe inleg (pre-tax).
    lj = vergelijk_lijfrente(eenheid, rendement, jaren, jaar,
                             marginaal_nu=marginaal_nu, tarief_uit=tarief_uit, partner=partner)
    lijf_net = lj.lijfrente_eindnetto if inleg > 0 else 0.0
    box3_net = lj.prive_eindnetto if inleg > 0 else 0.0
    # Sparen = box 3 maar tegen de lage banktegoeden-rente — het "niets doen"-scenario.
    spaarrente0 = p.box3["forfait"]["banktegoeden"]
    lj_spaar = vergelijk_lijfrente(eenheid, spaarrente0, jaren, jaar,
                                   marginaal_nu=marginaal_nu, tarief_uit=tarief_uit, partner=partner)
    sparen_net = lj_spaar.prive_eindnetto if inleg > 0 else 0.0
    bv_net = 0.0
    containers = [
        Container("sparen", "Sparen (box 3 banktegoeden, ~1,3%)", round(sparen_net, 2),
                  "Volledig flexibel, maar laag rendement — het 'niets doen'-scenario.", None),
        Container("lijfrente", "Lijfrente / pensioensparen", round(lijf_net, 2),
                  "Vastzetten tot pensioen; aftrek nu, belastingvrije groei, box 1 bij opname.",
                  round(jaarruimte, 2)),
        Container("box3", "Privé beleggen (box 3)", round(box3_net, 2),
                  "Volledig flexibel; heffingvrij vermogen + tegenbewijs.", None),
    ]
    if is_ondernemer:
        u = vergelijk_uitstel(eenheid * (1 - vpb), rendement, jaren, jaar, partner=partner)
        bv_net = u.bv_eindnetto if inleg > 0 else 0.0
        containers.append(Container(
            "bv", "In de BV laten groeien", round(bv_net, 2),
            "Alleen bij groot, niet-geconsumeerd vermogen; box 2 bij opname.", None,
            soort="zakelijk"))
    containers.sort(key=lambda c: -c.netto_eind)

    # Pensioen-bewuste lijfrente-cap PER PERSOON (jij + evt. partner). Vul lijfrente daar waar het
    # marginale tarief NU het hoogst is (grootste uitstelvoordeel), tot de schijfgrens onder dat tarief.
    uj = max(1, int(uitkeringsjaren))
    jij_cap = _lijf_cap_persoon(p, marginaal=marginaal_nu, jaarruimte=jaarruimte,
                                verwacht_pensioen=verwacht_pensioen, bestaande_lijfrente=bestaande_lijfrente,
                                rendement=rendement, jaren=jaren, uj=uj)
    slots = [dict(jij_cap, wie="jij")]
    partner_cap = None
    if partner and partner_jaarruimte > 0:
        partner_cap = _lijf_cap_persoon(p, marginaal=partner_marginaal, jaarruimte=partner_jaarruimte,
                                        verwacht_pensioen=partner_verwacht_pensioen,
                                        bestaande_lijfrente=partner_bestaande_lijfrente,
                                        rendement=rendement, jaren=jaren, uj=uj)
        slots.append(dict(partner_cap, wie="partner"))
    slots.sort(key=lambda s: -s["marginaal"])  # hoogste marginaal eerst = grootste uitstelvoordeel
    totale_cap = sum(s["cap"] for s in slots)
    totale_jaarruimte = jaarruimte + (partner_jaarruimte if partner_cap else 0.0)
    lijf_gecapt = totale_cap < min(totale_jaarruimte, inleg) - 1 if totale_jaarruimte > 0 else False
    # Bestaande lijfrente-pot van de partner telt óók mee zónder jaarruimte (bestaand vermogen).
    partner_bestaande_lijf_pot = (partner_bestaande_lijfrente * (1 + rendement) ** jaren) if partner else 0.0
    bestaande_lijf_pot_tot = jij_cap["bestaande_lijf_pot"] + partner_bestaande_lijf_pot

    # Watervalallocatie van de JAARLIJKSE inleg: lijfrente-slots (hoogste marginaal eerst), rest → box 3/BV.
    resterend = inleg
    lijf = {"jij": 0.0, "partner": 0.0}
    for s in slots:
        neem = max(0.0, min(s["cap"], resterend))
        lijf[s["wie"]] = neem
        resterend -= neem
    lijf_deel = lijf["jij"] + lijf["partner"]
    overschot = resterend
    overschot_naar = "box3"
    if is_ondernemer and inleg > 0 and (bv_net / eenheid) > (box3_net / eenheid):
        overschot_naar = "bv"
    allocatie = {
        "lijfrente": round(lijf["jij"], 2),
        "lijfrente_partner": round(lijf["partner"], 2),
        "box3": round(overschot if overschot_naar == "box3" else 0.0, 2),
        "bv": round(overschot if overschot_naar == "bv" else 0.0, 2),
    }

    # Herverdeling van BESTAAND spaargeld: buffer liquide, overschot → resterende lijfrente-ruimte
    # (hoogste marginaal eerst, over beide personen), rest → box 3-beleggen.
    liquide = min(max(0.0, vrij_opneembaar), bestaand_spaargeld)
    surplus = round(bestaand_spaargeld - liquide, 2)
    herv = {"jij": 0.0, "partner": 0.0}
    rest_surplus = surplus
    for s in slots:
        ruimte = max(0.0, s["cap"] - lijf[s["wie"]])
        neem = min(ruimte, rest_surplus)
        herv[s["wie"]] = neem
        rest_surplus -= neem
    herv_lijfrente = herv["jij"] + herv["partner"]
    herv_box3 = round(surplus - herv_lijfrente, 2)
    herverdeling = {
        "spaargeld": round(bestaand_spaargeld, 2), "liquide": round(liquide, 2),
        "surplus": surplus, "naar_lijfrente": round(herv["jij"], 2),
        "naar_lijfrente_partner": round(herv["partner"], 2),
        "naar_box3": herv_box3,
        # rest kan de komende jaren alsnog in lijfrente (tot de jaarruimte) i.p.v. in box 3
        "gefaseerd": bool(herv_box3 > 1 and not lijf_gecapt),
    } if surplus > 0 else None

    # Bestaand vermogen.
    bestaand_box3_last = round(
        box3_last(p, beleggingen=bestaand_box3, partner=partner, werkelijk_rendement=rendement), 2
    ) if bestaand_box3 > 0 else 0.0
    bestaand_bv_res = None
    if bestaand_bv_spaargeld + bestaand_bv_beleggingen > 0:
        spaarrente = p.box3["forfait"]["banktegoeden"]
        bv_eind = prive_eind = 0.0
        if bestaand_bv_beleggingen > 0:  # binnen BV: Vpb op rendement; uitkeren → box 3 overige (6%)
            ub = vergelijk_uitstel(bestaand_bv_beleggingen, rendement, jaren, jaar, partner=partner)
            bv_eind += ub.bv_eindnetto
            prive_eind += ub.prive_eindnetto
        if bestaand_bv_spaargeld > 0:  # spaargeld groeit traag; uitkeren → box 3 banktegoeden (~1,28%)
            us = vergelijk_uitstel(bestaand_bv_spaargeld, spaarrente, jaren, jaar, partner=partner,
                                   forfait_cat="banktegoeden", pas_heffingvrij=False)
            bv_eind += us.bv_eindnetto
            prive_eind += us.prive_eindnetto
        bestaand_bv_res = {
            "spaargeld": bestaand_bv_spaargeld, "beleggingen": bestaand_bv_beleggingen,
            "bedrag": round(bestaand_bv_spaargeld + bestaand_bv_beleggingen, 2),
            "beste": "bv" if bv_eind >= prive_eind else "prive",
            "bv_eindnetto": round(bv_eind, 2), "prive_eindnetto": round(prive_eind, 2),
        }

    # Projectie: jaarlijkse inleg per container → pot bij pensioen → jaarlijkse uitkering.
    pct3 = min(forfait, rendement)  # tegenbewijs-benadering voor de box 3-drag
    net_box3 = rendement - pct3 * tarief3
    # Jaarlijkse inleg (annuïteit) + bestaande lijfrente-pot + herverdeeld spaargeld (lump), PER PERSOON.
    groei_lump = (1 + rendement) ** jaren
    lijf_pot_jij = (_fv_annuity(allocatie["lijfrente"], rendement, jaren)
                    + jij_cap["bestaande_lijf_pot"] + herv["jij"] * groei_lump)
    lijf_pot_partner = (_fv_annuity(allocatie["lijfrente_partner"], rendement, jaren)
                        + partner_bestaande_lijf_pot + herv["partner"] * groei_lump)
    lijf_pot = lijf_pot_jij + lijf_pot_partner
    box3_pot = _fv_annuity(allocatie["box3"], net_box3, jaren) + herv_box3 * (1 + net_box3) ** jaren
    bv_pot = _fv_annuity(allocatie["bv"], rendement * (1 - vpb), jaren)
    # Bestaand box 3-vermogen doorgegroeid tot pensioen + de nieuwe box 3-inleg.
    bestaand_box3_straks = bestaand_box3 * (1 + net_box3) ** jaren
    box3_straks_totaal = box3_pot + bestaand_box3_straks
    # Beleggingen van de partner groeien mee (worden niet herverdeeld) → aandeel voor de Straks-split.
    box3_straks_partner = partner_bestaand_box3 * (1 + net_box3) ** jaren
    # Alleen de liquide buffer blijft sparen (de rest is herverdeeld).
    spaarrente = p.box3["forfait"]["banktegoeden"]
    spaargeld_straks = liquide * (1 + spaarrente) ** jaren
    uj = max(1, int(uitkeringsjaren))
    defl = (1 + inflatie) ** jaren  # deflator naar euro's van nu (waarde bij pensioen)
    projectie = {
        "jaren_opbouw": jaren, "uitkeringsjaren": uj, "inflatie": inflatie,
        "lijfrente_pot": round(lijf_pot, 2), "box3_pot": round(box3_pot, 2),
        "bv_pot": round(bv_pot, 2),
        "lijfrente_uitkering": round(lijf_pot / uj, 2), "bv_dividend": round(bv_pot / uj, 2),
        # Lijfrente per persoon (voor Straks: jij en partner worden apart belast in box 1).
        "lijfrente_pot_jij": round(lijf_pot_jij, 2), "lijfrente_pot_partner": round(lijf_pot_partner, 2),
        "lijfrente_uitkering_jij": round(lijf_pot_jij / uj, 2),
        "lijfrente_uitkering_partner": round(lijf_pot_partner / uj, 2),
        "box3_straks": round(box3_pot, 2),
        "box3_straks_totaal": round(box3_straks_totaal, 2),  # incl. bestaand box 3 doorgegroeid
        "box3_straks_partner": round(box3_straks_partner, 2),  # aandeel partner (voor Straks-split)
        "spaargeld_straks": round(spaargeld_straks, 2),
        # Reëel (in euro's van nu) — inflatie deflateert alle containers ~evenredig, dus
        # dit verandert de keuze nauwelijks maar laat de echte koopkracht zien.
        "lijfrente_pot_reeel": round(lijf_pot / defl, 2),
        "lijfrente_uitkering_reeel": round(lijf_pot / uj / defl, 2),
        "bv_dividend_reeel": round(bv_pot / uj / defl, 2),
        "box3_straks_reeel": round(box3_pot / defl, 2),
    }

    liquiditeit_advies = (
        "Bepaal je liquide deel zo: noodbuffer (± 3–6 maanden vaste lasten) + uitgaven die je "
        "vóór je pensioen verwacht (verbouwing, studie kinderen). Dat deel hoort in box 3 "
        "(flexibel). Geld dat je écht tot je pensioen kunt missen, zet je vast in lijfrente "
        "(tot je jaarruimte); een eventueel overschot daarboven gaat naar de gunstigste "
        "resterende container."
    )
    waarschuwingen = [
        "Netto-eindwaarden zijn per container berekend voor de volledige inleg; het heffingvrij "
        "vermogen wordt per onderdeel toegepast (licht conservatief bij combinaties).",
        "Opnametarief lijfrente is een aanname (AOW-schijf 1); bij een grote pot hoger.",
        "BV-retentie is alleen relevant voor ondernemers die winst kunnen oppotten — privé "
        "al-belast vermogen verplaats je niet naar een BV.",
        f"Reële bedragen zijn naar euro's van nu teruggerekend met {inflatie*100:.1f}% inflatie. "
        "Inflatie deflateert alle containers ~evenredig, dus ze beïnvloedt vooral de koopkracht "
        "van je eindpot, nauwelijks de keuze tussen lijfrente/box 3/BV.",
    ]
    if jaren > 45:
        waarschuwingen.insert(0,
            f"⚠ Lange horizon ({jaren} jaar): de projectie veronderstelt {jaren} jaar lang "
            "dezelfde inleg én een constant rendement. Nominale bedragen lopen dan extreem op en "
            "zijn vooral illustratief — controleer of je leeftijd klopt.")
    lijfrente_optimaal = {
        "cap": round(jij_cap["cap"], 2), "target_box1": round(jij_cap["target_box1"], 2),
        "verwacht_pensioen": round(max(0.0, verwacht_pensioen), 2),
        "bestaande_lijfrente_uitkering": round(jij_cap["bestaande_lijf_uitkering"], 2),
        "effectief_pensioen": round(jij_cap["effectief_pensioen"], 2),
        "target_uitkering": round(jij_cap["target_uitkering"], 2), "marginaal_nu": marginaal_nu,
        "gecapt": bool(lijf_gecapt),
        "toegewezen": round(lijf["jij"] + herv["jij"], 2),
        "partner": ({
            "cap": round(partner_cap["cap"], 2), "target_box1": round(partner_cap["target_box1"], 2),
            "marginaal": partner_marginaal, "jaarruimte": round(partner_jaarruimte, 2),
            "verwacht_pensioen": round(max(0.0, partner_verwacht_pensioen), 2),
            "toegewezen": round(lijf["partner"] + herv["partner"], 2),
            "prioriteit": partner_marginaal > marginaal_nu,  # partner heeft het hoogste tarief
        } if partner_cap else None),
    }
    if lijf_gecapt:
        waarschuwingen.insert(0,
            f"Lijfrente begrensd op ± € {lijf_deel:,.0f}/jaar (huishouden): meer zou de pensioenuitkering "
            "boven de schijfgrens duwen, waar het opnametarief het tarief van nu raakt → het tariefvoordeel "
            "is dan weg. Doorvullen groeit nog wel belastingvrij (op rendement wint het), maar zit vast tot "
            "pensioen; de rest naar box 3 is een flexibiliteitskeuze. Box 3 wint pas óók op rendement als je "
            "daar meer dan ~2,16%/jaar méér haalt dan in de lijfrente.".replace(",", "."))
    return VermogensadviesResultaat(
        jaar=jaar, nieuwe_inleg=round(inleg, 2), jaren=jaren, rendement=rendement,
        containers=containers, allocatie=allocatie,
        bestaand_box3_last=bestaand_box3_last, bestaand_bv=bestaand_bv_res,
        liquiditeit_advies=liquiditeit_advies, projectie=projectie,
        lijfrente_optimaal=lijfrente_optimaal, herverdeling=herverdeling,
        waarschuwingen=waarschuwingen,
    )
