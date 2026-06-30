"""Optimalisatiemotor: gegeven één situatie, bepaal de fiscaal gunstigste route.

Twee dimensies:
1. **Inkomen** — werknemer / ZZP / DGA, inclusief Zvw, WW/WIA en toeslagen
   (hergebruikt `vergelijking.vergelijk`).
2. **Vermogen** — privévermogen wordt jaarlijks in **box 3** belast (forfaitair),
   maar vermogen dat in de **BV** blijft ontsnapt aan box 3: alleen het werkelijke
   rendement wordt belast (Vpb + later box 2). Voor de DGA telt daarom de BV-route,
   voor werknemer/ZZP de box 3-route.

De motor levert een gerangschikt advies met netto-besteedbaar per route + concrete
knoppen. Bedoeld als rekenlaag onder het dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .params import Params, laad_params
from .pensioen import jaarruimte
from .toeslagen import Huishoudprofiel
from .vergelijking import vergelijk


@dataclass
class Situatie:
    """Volledige invoer (wordt het invoermodel van het dashboard)."""

    economische_waarde: float            # V: winst/loon-equivalent per jaar
    profiel: Huishoudprofiel | None = None
    prive_vermogen: float = 0.0          # box 3 BELEGGINGEN (overige bezittingen, forfait ~6%)
    spaargeld: float = 0.0               # box 3 SPAARGELD (banktegoeden, forfait ~1,3%)
    verwacht_rendement: float = 0.06     # verwacht WERKELIJK rendement op dat vermogen
    urencriterium: bool = True
    tegenbewijs_box3: bool = True        # box 3 op werkelijk rendement indien lager dan forfait
    vaste_kosten: dict | None = None     # override administratie-/boekhoudkosten per rechtsvorm
    oprichtingskosten: dict | None = None  # override eenmalige oprichtingskosten per rechtsvorm
    horizon_jaren: int | None = None     # amortisatiehorizon oprichtingskosten (lang: niet terugswitchen)
    gebruikelijk_loon: float | None = None  # DGA-loon; bv. = V als de arbeid het loon bepaalt ("eigen gebruik")


@dataclass
class VormUitkomst:
    naam: str
    inkomen_netto: float       # netto besteedbaar + toeslagen
    vermogen_last: float       # box 3 (privé) of BV-route op het vermogen
    toelichting: str = ""

    @property
    def totaal_netto(self) -> float:
        return round(self.inkomen_netto - self.vermogen_last, 2)


@dataclass
class Advies:
    jaar: int
    situatie: Situatie
    uitkomsten: list[VormUitkomst]
    break_even_rendement: float | None
    jaarruimte_lijfrente: float = 0.0
    tips: list[str] = field(default_factory=list)

    @property
    def beste(self) -> VormUitkomst:
        return max(self.uitkomsten, key=lambda u: u.totaal_netto)

    @property
    def besparing_vs_slechtste(self) -> float:
        netto = [u.totaal_netto for u in self.uitkomsten]
        return round(max(netto) - min(netto), 2)

    def rapport(self) -> str:
        regels = [
            f"=== Optimalisatieadvies — belastingjaar {self.jaar} ===",
            f"Economische waarde V: € {self.situatie.economische_waarde:,.0f}".replace(",", "."),
        ]
        if self.situatie.prive_vermogen:
            regels.append(
                f"Vermogen: € {self.situatie.prive_vermogen:,.0f} "
                f"(verwacht rendement {self.situatie.verwacht_rendement:.1%})".replace(",", ".")
            )
        regels.append("")
        regels.append(f"{'route':>10} | {'inkomen netto':>14} | {'vermogenslast':>14} | {'TOTAAL netto':>14}")
        regels.append(f"{'-'*10}-+-{'-'*14}-+-{'-'*14}-+-{'-'*14}")
        for u in sorted(self.uitkomsten, key=lambda x: -x.totaal_netto):
            ster = "  <= beste" if u.naam == self.beste.naam else ""
            regels.append(
                f"{u.naam:>10} | € {u.inkomen_netto:>11,.0f} | € {u.vermogen_last:>11,.0f} | "
                f"€ {u.totaal_netto:>11,.0f}{ster}".replace(",", ".")
            )
        regels.append("")
        regels.append(
            f"Beste route: {self.beste.naam.upper()} — "
            f"€ {self.besparing_vs_slechtste:,.0f} per jaar voordeliger dan de duurste.".replace(",", ".")
        )
        for t in self.tips:
            regels.append(f"  • {t}")
        return "\n".join(regels)


def box3_last(
    p: Params,
    *,
    spaargeld: float = 0.0,
    beleggingen: float = 0.0,
    schulden: float = 0.0,
    partner: bool = False,
    werkelijk_rendement: float | None = None,
) -> float:
    """Jaarlijkse box 3-heffing over de drie categorieën: spaargeld (banktegoeden-forfait
    ~1,3%), beleggingen (overige-bezittingen-forfait ~6%) en schulden (forfait ~2,7%,
    boven de drempel). Met `werkelijk_rendement` (tegenbewijs): heft over het laagste van
    forfait/werkelijk."""
    b3 = p.box3
    f = b3["forfait"]
    drempel = b3["schuldendrempel_pp"] * (2 if partner else 1)
    schulden_mee = max(0.0, schulden - drempel)
    grondslag = spaargeld + beleggingen - schulden_mee
    if grondslag <= 0:
        return 0.0
    rendement = (
        spaargeld * f["banktegoeden"]
        + beleggingen * f["overige_bezittingen"]
        - schulden_mee * f["schulden"]
    )
    forfait_pct = rendement / grondslag if grondslag else 0.0
    pct = forfait_pct
    if werkelijk_rendement is not None and werkelijk_rendement < forfait_pct:
        pct = max(0.0, werkelijk_rendement)
    heffingvrij = b3["heffingvrij_vermogen_pp"] * (2 if partner else 1)
    na_vrij = max(0.0, grondslag - heffingvrij)
    return round(na_vrij * pct * b3["tarief"], 2)


def bv_vermogen_last(vermogen: float, verwacht_rendement: float, p: Params) -> float:
    """Jaarlijkse last als hetzelfde vermogen in de BV blijft: Vpb + box 2 over het
    WERKELIJKE rendement (lage tarieven; uitkering verondersteld)."""
    rendement = vermogen * verwacht_rendement
    vpb = rendement * p["vpb"]["schijven"][0]["tarief"]
    dividend = rendement - vpb
    box2 = dividend * p["box2"]["schijven"][0]["tarief"]
    return round(vpb + box2, 2)


def break_even_rendement(p: Params, *, partner: bool = False) -> float:
    """Werkelijk rendement waarbij box 3 (forfait) en de BV-route even duur zijn.
    Eronder is de BV goedkoper voor vermogen; erboven is box 3 (door het forfait) goedkoper."""
    b3 = p.box3
    forfait_tarief = b3["forfait"]["overige_bezittingen"] * b3["tarief"]
    vpb = p["vpb"]["schijven"][0]["tarief"]
    box2 = p["box2"]["schijven"][0]["tarief"]
    bv_tarief = vpb + (1 - vpb) * box2
    return round(forfait_tarief / bv_tarief, 4) if bv_tarief else 0.0


def optimaliseer(situatie: Situatie, jaar: int) -> Advies:
    p = laad_params(jaar)
    partner = situatie.profiel.heeft_toeslagpartner if situatie.profiel else False

    v = vergelijk(
        situatie.economische_waarde,
        jaar,
        urencriterium=situatie.urencriterium,
        profiel=situatie.profiel,
        vaste_kosten=situatie.vaste_kosten,
        oprichtingskosten=situatie.oprichtingskosten,
        horizon_jaren=situatie.horizon_jaren,
        gebruikelijk_loon=situatie.gebruikelijk_loon,
    )

    werkelijk = situatie.verwacht_rendement if situatie.tegenbewijs_box3 else None
    totaal_vermogen = situatie.prive_vermogen + situatie.spaargeld
    box3 = box3_last(
        p, spaargeld=situatie.spaargeld, beleggingen=situatie.prive_vermogen,
        partner=partner, werkelijk_rendement=werkelijk,
    )
    bv = bv_vermogen_last(totaal_vermogen, situatie.verwacht_rendement, p)

    uitkomsten: list[VormUitkomst] = []
    for vorm in v.vormen:
        if vorm.naam == "dga":
            # De DGA kan kiezen: vermogen in de BV laten, óf uitkeren en privé in box 3.
            if bv <= box3:
                last, toel = bv, "vermogen in BV (werkelijk rendement < forfait)"
            else:
                last, toel = box3, "vermogen privé in box 3 (forfait < werkelijk rendement)"
        else:
            # Box 3 heft het FICTIEVE rendement, niet de werkelijke winst.
            last = box3
            toel = "vermogen privé: box 3 (fictief rendement)"
        uitkomsten.append(
            VormUitkomst(vorm.naam, vorm.netto_inclusief_toeslagen, last, toel)
        )

    be = break_even_rendement(p, partner=partner) if totaal_vermogen else None

    tips: list[str] = []
    if totaal_vermogen:
        if situatie.tegenbewijs_box3:
            tips.append(
                "Met de tegenbewijsregeling heft box 3 maximaal over het WERKELIJKE rendement "
                "(36%), wat doorgaans goedkoper is dan de BV (Vpb + box 2 ≈ 38,8%). Het BV-voordeel "
                "voor vermogen zit dan vooral in uitstel (timing), niet in het tarief."
            )
        elif be is not None and situatie.verwacht_rendement < be:
            tips.append(
                f"Zonder tegenbewijs: vermogen met rendement < {be:.1%} in de BV houden bespaart "
                "box 3 (spaar-/beleggings-BV)."
            )
        elif be is not None:
            tips.append(
                f"Zonder tegenbewijs: bij rendement ≥ {be:.1%} is het box 3-forfait juist gunstiger "
                "dan de BV (het forfait ondertaxeert hoog werkelijk rendement)."
            )
    tips.append(
        "Eigenwoning-/hypotheekrenteaftrek tussen partners verdelen levert door de "
        "tariefaanpassing (37,56%) weinig op, behalve weg bij een lage-inkomenspartner (verdamping)."
    )

    kosten = situatie.vaste_kosten if situatie.vaste_kosten is not None else p["vaste_kosten_indicatief"]
    if kosten.get("dga", 0) > kosten.get("zzp", 0):
        k_dga_s = f"{kosten.get('dga', 0):,.0f}".replace(",", ".")
        k_zzp_s = f"{kosten.get('zzp', 0):,.0f}".replace(",", ".")
        tips.append(
            f"BV-overhead (boekhouding/jaarrekening/Vpb ~€ {k_dga_s}/jr vs ZZP ~€ {k_zzp_s}) "
            "is meegerekend en verschuift het omslagpunt naar de DGA omhoog; eenmalige "
            "oprichtingskosten zijn nog niet meegenomen."
        )

    if situatie.gebruikelijk_loon is None:
        tips.append(
            "DGA-voordeel berust op gebruikelijk loon = normbedrag. Voor inkomen dat je "
            "consumeert ('eigen gebruik') eist de Belastingdienst loon op het niveau van een "
            "vergelijkbare dienstbetrekking — dan verdampt het dividendvoordeel grotendeels. "
            "Het echte BV-voordeel is uitstel voor vermogen dat je NIET consumeert; de "
            "afzondering van privévermogen is bovendien beperkt (banken eisen vaak een "
            "persoonlijke borgstelling, en bestuurdersaansprakelijkheid kan privé doorwerken)."
        )

    # Jaarruimte lijfrente (factor A = 0: ZZP/DGA zonder werkgeverspensioen).
    jr = jaarruimte(situatie.economische_waarde, p)
    if jr > 0:
        jr_s = f"{jr:,.0f}".replace(",", ".")
        tips.append(
            f"Lijfrente-aftrek (jaarruimte, art. 3.127): tot € {jr_s} aftrekbaar in box 1 "
            "tegen je marginale tarief (niet afgetopt); het verlaagt het toetsingsinkomen "
            "(meer toeslagen) en het kapitaal valt buiten box 3."
        )

    return Advies(
        jaar=jaar,
        situatie=situatie,
        uitkomsten=uitkomsten,
        break_even_rendement=be,
        jaarruimte_lijfrente=jr,
        tips=tips,
    )
