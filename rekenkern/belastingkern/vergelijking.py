"""Rechtsvormvergelijking: dezelfde economische waarde (V) belast als
a) werknemer (loon), b) IB-ondernemer/ZZP (winst), c) DGA (bv: Vpb + loon + box 2),
inclusief Zvw en een optionele pensioen-equivalent.

Doel: toetsen of de wetgever de totale druk over de rechtsvormen gelijk heeft getrokken.

INVARIANT (belangrijk): **V = totale economische kosten / waarde op activiteitsniveau**,
INCLUSIEF werkgeverslasten. Daardoor is de werknemer eerlijk vergelijkbaar:
- Werknemer: van V gaat eerst de werkgeversheffing Zvw af; de rest is brutoloon.
- ZZP: V = fiscale winst; de persoon betaalt zelf de lage Zvw-bijdrage + IB.
- DGA: V = bv-winst; gebruikelijk loon (box 1 + lage Zvw) + restwinst (Vpb) → dividend (box 2).
  Over dividend is GEEN Zvw verschuldigd.

Pensioen-equivalent (optioneel, `pensioen_pct`): een fiscaal aftrekbare oudedags-
reservering van `pensioen_pct × V`, voor elke vorm uit dezelfde V. Werknemer: werkgevers-
pensioen (omkeerregel, onbelast nu). ZZP/DGA: aftrekbare lijfrente / pensioen in bv.
Het is GEEN belasting (blijft vermogen van de persoon), maar verlaagt de actuele heffing
(uitstel). Vereenvoudiging: Zvw-grondslag wordt niet voor de pensioenpremie verlaagd.

NIET meegenomen: werknemersverzekeringen (WW/WIA-waarde voor de werknemer),
box 2-uitstel, en toeslagen (afbouw op toetsingsinkomen) — apart te koppelen.
"""

from __future__ import annotations

from dataclasses import dataclass

from .dga import bereken_dga
from .engine import bereken_persoon
from .model import Onderneming, Persoon
from .onderneming import bereken_onderneming
from .params import laad_params
from .socialezekerheid import (
    lage_bijdrage_zvw,
    werkgeversheffing_zvw,
    werknemersverzekeringen,
    werknemersverzekeringen_pct,
)
from .toeslagen import Huishoudprofiel, ToeslagenResultaat, bereken_toeslagen


@dataclass
class Vorm:
    naam: str
    bruto: float              # economische waarde V (totale kosten)
    inkomstenheffing: float   # IB/PVV (box 1) + box 2 + (DGA) Vpb, na heffingskortingen
    zvw: float
    werknemersverzekeringen: float = 0.0  # WW/WIA-premie (werkgeverslast); 'met aanspraak'
    pensioen: float = 0.0     # aftrekbare oudedagsreservering (geen belasting)
    vaste_kosten: float = 0.0             # administratie/boekhouding (aftrekbaar, cash-out)
    oprichtingskosten_jaar: float = 0.0   # eenmalig, geamortiseerd (niet-aftrekbaar, cash-out)
    verzamelinkomen: float = 0.0          # = toetsingsinkomen voor toeslagen
    toeslagen: ToeslagenResultaat | None = None

    @property
    def totale_belasting(self) -> float:
        """Zuivere belastingdruk: IB/PVV/Vpb/box 2 + Zvw (WW/WIA telt hier NIET mee,
        want dat is een premie met individuele aanspraak/verzekering)."""
        return round(self.inkomstenheffing + self.zvw, 2)

    @property
    def totale_wig(self) -> float:
        """Totale wig: belastingdruk + werknemersverzekeringen (alle afdrachten)."""
        return round(self.totale_belasting + self.werknemersverzekeringen, 2)

    @property
    def effectief_tarief(self) -> float:
        return round(self.totale_belasting / self.bruto, 4) if self.bruto else 0.0

    @property
    def effectief_wig(self) -> float:
        return round(self.totale_wig / self.bruto, 4) if self.bruto else 0.0

    @property
    def netto_besteedbaar(self) -> float:
        # Vaste kosten = aftrekbare cash-out; oprichtingskosten = niet-aftrekbare cash-out.
        return round(
            self.bruto - self.totale_wig - self.pensioen
            - self.vaste_kosten - self.oprichtingskosten_jaar, 2
        )

    @property
    def toeslagen_totaal(self) -> float:
        return self.toeslagen.totaal if self.toeslagen else 0.0

    @property
    def netto_inclusief_toeslagen(self) -> float:
        return round(self.netto_besteedbaar + self.toeslagen_totaal, 2)


@dataclass
class Vergelijking:
    jaar: int
    bruto: float
    werknemer: Vorm
    zzp: Vorm
    dga: Vorm
    inclusief_zvw: bool
    inclusief_wnv: bool
    pensioen_pct: float

    @property
    def vormen(self) -> list[Vorm]:
        return [self.werknemer, self.zzp, self.dga]

    @property
    def goedkoopste(self) -> Vorm:
        return min(self.vormen, key=lambda v: v.totale_belasting)

    @property
    def spreiding(self) -> float:
        """Verschil in effectief tarief tussen duurste en goedkoopste vorm (procentpunt)."""
        t = [v.effectief_tarief for v in self.vormen]
        return round((max(t) - min(t)) * 100, 2)


def vergelijk(
    bruto: float,
    jaar: int,
    *,
    urencriterium: bool = True,
    inclusief_zvw: bool = True,
    inclusief_wnv: bool = True,
    pensioen_pct: float = 0.0,
    profiel: Huishoudprofiel | None = None,
    vaste_kosten: dict | None = None,
    oprichtingskosten: dict | None = None,
    horizon_jaren: int | None = None,
    gebruikelijk_loon: float | None = None,
) -> Vergelijking:
    p = laad_params(jaar)
    pensioen = round(pensioen_pct * bruto, 2)
    kosten = vaste_kosten if vaste_kosten is not None else p["vaste_kosten_indicatief"]
    k_wn = float(kosten.get("werknemer", 0))
    k_zzp = float(kosten.get("zzp", 0))
    k_dga = float(kosten.get("dga", 0))

    # Eenmalige oprichtingskosten, geamortiseerd over de horizon (niet-aftrekbaar).
    opr = oprichtingskosten if oprichtingskosten is not None else p["oprichtingskosten_indicatief"]
    horizon = horizon_jaren or int(opr.get("standaard_horizon_jaren", 10))
    o_wn = round(float(opr.get("werknemer", 0)) / horizon, 2)
    o_zzp = round(float(opr.get("zzp", 0)) / horizon, 2)
    o_dga = round(float(opr.get("dga", 0)) / horizon, 2)

    def toeslagen_voor(verzamelinkomen: float) -> ToeslagenResultaat | None:
        """Toeslagen op basis van het toetsingsinkomen (verzamelinkomen + partnerinkomen)."""
        if profiel is None:
            return None
        return bereken_toeslagen(
            verzamelinkomen + profiel.partner_inkomen, p, profiel=profiel
        )

    # ---------- a) Werknemer ----------
    # V = totale werkgeverskosten. Trek werkgeverslasten (Zvw-heffing + WW/WIA, beide
    # tot hetzelfde maximumpremieloon) eraf om bij het brutoloon te komen.
    beschikbaar = bruto - pensioen - k_wn  # werknemer: doorgaans geen eigen admin (k_wn=0)
    cap = p["zvw"]["max_bijdrage_inkomen"]
    r = 0.0
    if inclusief_zvw:
        r += p["zvw"]["werkgeversheffing_pct"]
    if inclusief_wnv:
        r += werknemersverzekeringen_pct(p)
    brutoloon = beschikbaar / (1 + r)
    if brutoloon > cap:  # boven het maximumpremieloon is de werkgeverslast een vast bedrag
        brutoloon = beschikbaar - r * cap
    wn_zvw = werkgeversheffing_zvw(brutoloon, p) if inclusief_zvw else 0.0
    wn_wnv = werknemersverzekeringen(brutoloon, p) if inclusief_wnv else 0.0
    wn_res = bereken_persoon(Persoon(naam="werknemer", loon=brutoloon), p)
    werknemer = Vorm(
        "werknemer", bruto, wn_res.te_betalen, wn_zvw,
        werknemersverzekeringen=wn_wnv, pensioen=pensioen, vaste_kosten=k_wn,
        oprichtingskosten_jaar=o_wn,
        verzamelinkomen=wn_res.verzamelinkomen,
        toeslagen=toeslagen_voor(wn_res.verzamelinkomen),
    )

    # ---------- b) ZZP (IB-ondernemer) ----------
    # Boekhoudkosten zijn aftrekbaar: verlagen de winst (en daarmee grondslag/toeslagen).
    winst_zzp = max(0.0, bruto - k_zzp)
    ond = bereken_onderneming(
        Onderneming(winst=winst_zzp, voldoet_urencriterium=urencriterium), p
    )
    zzp_res = bereken_persoon(
        Persoon(
            naam="zzp",
            onderneming=Onderneming(winst=winst_zzp, voldoet_urencriterium=urencriterium),
            aftrekposten_box1=pensioen,  # aftrekbare lijfrente
        ),
        p,
    )
    zzp_zvw = lage_bijdrage_zvw(ond.belastbare_winst, p) if inclusief_zvw else 0.0
    zzp = Vorm(
        "zzp", bruto, zzp_res.te_betalen, zzp_zvw, pensioen=pensioen, vaste_kosten=k_zzp,
        oprichtingskosten_jaar=o_zzp,
        verzamelinkomen=zzp_res.verzamelinkomen,
        toeslagen=toeslagen_voor(zzp_res.verzamelinkomen),
    )

    # ---------- c) DGA (bv) ----------
    # Pensioen + boekhoudkosten via de bv (aftrekbaar voor Vpb): verlagen de uit te keren winst.
    # gebruikelijk_loon override: zet het loon hoger (bv. arbeidsbeloning voor "eigen gebruik").
    dga_res = bereken_dga(
        bruto - pensioen - k_dga, p, hoger_gebruikelijk_loon=gebruikelijk_loon or 0.0
    )
    dga_zvw = lage_bijdrage_zvw(dga_res.gebruikelijk_loon, p) if inclusief_zvw else 0.0
    dga_vi = dga_res.box1_resultaat.verzamelinkomen
    dga = Vorm(
        "dga", bruto, dga_res.totale_belasting, dga_zvw, pensioen=pensioen, vaste_kosten=k_dga,
        oprichtingskosten_jaar=o_dga,
        verzamelinkomen=dga_vi,
        toeslagen=toeslagen_voor(dga_vi),
    )

    return Vergelijking(
        jaar=jaar,
        bruto=bruto,
        werknemer=werknemer,
        zzp=zzp,
        dga=dga,
        inclusief_zvw=inclusief_zvw,
        inclusief_wnv=inclusief_wnv,
        pensioen_pct=pensioen_pct,
    )


def tabel(
    brutos: list[float],
    jaar: int,
    *,
    urencriterium: bool = True,
    inclusief_zvw: bool = True,
    inclusief_wnv: bool = True,
    pensioen_pct: float = 0.0,
    metric: str = "belasting",
) -> str:
    """`metric`: 'belasting' = IB/Vpb/box2 + Zvw (WW/WIA telt niet mee, is verzekering);
    'wig' = inclusief WW/WIA-premie (totale afdracht)."""
    is_wig = metric == "wig"
    kop = f"Effectieve {'totale wig' if is_wig else 'belastingdruk'} per rechtsvorm — belastingjaar {jaar}"
    sub = "incl. Zvw" if inclusief_zvw else "ZONDER Zvw"
    sub += " + WW/WIA" if (inclusief_wnv and is_wig) else ""
    if pensioen_pct:
        sub += f", pensioen {pensioen_pct:.0%} van V"
    noemer = "(IB/Vpb/box2 + Zvw + WW/WIA)" if is_wig else "(IB/Vpb/box2 + Zvw; WW/WIA apart)"
    regels = [
        f"{kop}  [{sub}]",
        f"(V = totale economische waarde/kosten; effectief = {noemer} / V)",
        "",
        f"{'V (bruto)':>11} | {'werknemer':>18} | {'ZZP':>18} | {'DGA':>18} | {'spreiding':>9}",
        f"{'-'*11}-+-{'-'*18}-+-{'-'*18}-+-{'-'*18}-+-{'-'*9}",
    ]
    for bruto in brutos:
        v = vergelijk(
            bruto,
            jaar,
            urencriterium=urencriterium,
            inclusief_zvw=inclusief_zvw,
            inclusief_wnv=inclusief_wnv,
            pensioen_pct=pensioen_pct,
        )

        def cel(vorm: Vorm) -> str:
            bedrag = vorm.totale_wig if is_wig else vorm.totale_belasting
            tarief = vorm.effectief_wig if is_wig else vorm.effectief_tarief
            return f"€{bedrag:>7,.0f} ({tarief*100:>4.1f}%)"

        tarieven = [
            (x.effectief_wig if is_wig else x.effectief_tarief) for x in v.vormen
        ]
        spreiding = round((max(tarieven) - min(tarieven)) * 100, 2)
        regels.append(
            f"{bruto:>11,.0f} | {cel(v.werknemer):>18} | {cel(v.zzp):>18} | "
            f"{cel(v.dga):>18} | {spreiding:>6.1f}pp"
        )
    regels.append("")
    regels.append("Laagste = de 'optimale route'.")
    return "\n".join(regels)
