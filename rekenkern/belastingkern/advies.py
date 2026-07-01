"""Bredere optimalisatiemotor: gegeven de volledige situatie, loop de wettelijke
optimalisaties langs en kwantificeer elk de jaarlijkse besparing.

Knoppen (naast de rechtsvormkeuze die in de vergelijking/mix zit):
1. Lijfrente-inleg (jaarruimte, art. 3.127) — aftrek + lager toetsingsinkomen (meer toeslagen).
2. Partnertoerekening eigen woning (art. 2.17) — optimale verdeling.
3. Box 3 verdelen over partners (2× heffingvrij vermogen, art. 5.5).
4. Rechtsvorm van een extra activiteit (loon/ZZP/BV) — via de mix.

Elke suggestie wordt concreet doorgerekend (Δ huishoudbelasting + Δ toeslagen).
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from .box1 import _heffing_over
from .dga import bepaal_gebruikelijk_loon
from .engine import bereken_persoon
from .mix import bereken_mix, _persoon_detail
from .model import Box3Vermogen, EigenWoning, Onderneming, Persoon
from .onderneming import kia_aftrek
from .optimalisatiemotor import box3_last
from .params import laad_params
from .pensioen import jaarruimte
from .toerekening import optimale_eigenwoning_verdeling
from .toeslagen import Huishoudprofiel, bereken_toeslagen
from .uitstel import vergelijk_uitstel
from .lijfrente import vergelijk_lijfrente


@dataclass
class Suggestie:
    titel: str
    besparing: float          # € per jaar
    toelichting: str
    wetsartikel: str


@dataclass
class AdviesResultaat:
    jaar: int
    baseline_belasting: float
    baseline_toeslagen: float
    baseline_netto: float
    suggesties: list[Suggestie] = field(default_factory=list)
    rechtsvorm: dict | None = None   # ZZP vs BV vs loon voor het ondernemersinkomen
    vermogen: dict | None = None     # box 3-last nu + BV-uitstel-vergelijking voor de beleggingen
    lijfrente: dict | None = None    # meerjarige lijfrente vs. privé, gekoppeld aan de jaarruimte
    detail: dict | None = None       # uitsplitsing huidige situatie (persoon + partner)

    @property
    def totaal_potentieel(self) -> float:
        return round(sum(s.besparing for s in self.suggesties), 2)


def _ond(winst, uren, starter=False, overige=0.0):
    return Onderneming(winst=winst, voldoet_urencriterium=uren, starter=starter,
                       overige_ondernemersaftrek=overige) if winst else None


def _meewerkaftrek(uren, winst, p):
    """Meewerkaftrek (art. 3.78): % van de winst o.b.v. de meewerk-uren van de partner."""
    if uren < 525 or winst <= 0:
        return 0.0
    pct = 0.0
    for s in p["onderneming"]["meewerkaftrek_schijven"]:
        if uren >= s["vanaf_uren"]:
            pct = s["pct"]
    return round(pct * winst, 2)


def _huishouden(persoon, partner, profiel, p, inkomen, box2=0.0, extra_heffing=0.0,
                minst=True, partner_minst=True):
    rp = bereken_persoon(persoon, p, box2_inkomen=box2, is_minstverdienende=minst)
    rpp = bereken_persoon(partner, p, is_minstverdienende=partner_minst) if partner else None
    vi = rp.verzamelinkomen + (rpp.verzamelinkomen if rpp else 0.0)
    toeslagen = bereken_toeslagen(vi, p, profiel=profiel).totaal if profiel else 0.0
    tax = rp.te_betalen + extra_heffing + (rpp.te_betalen if rpp else 0.0)
    return round(tax, 2), round(toeslagen, 2), round(inkomen - tax + toeslagen, 2)


def optimalisatie_advies(
    jaar: int,
    *,
    loon: float = 0.0,
    ondernemer_inkomen: float = 0.0,
    urencriterium: bool = False,
    gebruikelijk_loon: float | None = None,
    partner_inkomen: float = 0.0,
    heeft_fiscaal_partner: bool = False,
    eigen_woning: EigenWoning | None = None,
    box3: Box3Vermogen | None = None,
    profiel: Huishoudprofiel | None = None,
    rendement: float = 0.06,
    horizon: int = 15,
    huidige_vorm: str = "zzp",
    dividend_box2: float = 0.0,
    jongste_kind_leeftijd: int | None = None,
    starter: bool = False,
    meewerk_uren: int = 0,
    investering: float = 0.0,
) -> AdviesResultaat:
    """Het ondernemersinkomen ís de te optimaliseren variabele (ZZP vs BV vs loon).
    `huidige_vorm` ("zzp" of "bv") bepaalt de baseline: wat de gebruiker NU betaalt."""
    p = laad_params(jaar)
    ew = eigen_woning or EigenWoning()
    b3 = box3 or Box3Vermogen()
    heeft_fp = bool(partner_inkomen or heeft_fiscaal_partner)
    pk = dict(jongste_kind_leeftijd=jongste_kind_leeftijd, heeft_fiscale_partner=heeft_fp)  # IACK
    partner = Persoon(loon=partner_inkomen, **pk) if heeft_fp else None
    inkomen = loon + ondernemer_inkomen + partner_inkomen
    # IACK gaat naar de minstverdienende (of de alleenstaande ouder).
    user_arbeids = loon + ondernemer_inkomen
    minst = (not heeft_fp) or (user_arbeids <= partner_inkomen)
    partner_minst = heeft_fp and (partner_inkomen < user_arbeids)
    meewerk = _meewerkaftrek(meewerk_uren, ondernemer_inkomen, p)  # partner werkt mee in de zaak
    kia = kia_aftrek(investering, p) if ondernemer_inkomen > 0 else 0.0  # investeringsaftrek
    zzp_persoon = Persoon(loon=loon, onderneming=_ond(ondernemer_inkomen, urencriterium, starter, meewerk + kia),
                          eigen_woning=ew, box3=b3, **pk)

    # Bouw de "operationele" persoon voor een gekozen vorm: (persoon, box2, Vpb+overhead, box1-arbeidsinkomen).
    def _operationeel(naam):
        if naam == "bv":
            gl = bepaal_gebruikelijk_loon(ondernemer_inkomen, p, hoger_loon=gebruikelijk_loon or 0.0)
            winst_voor_vpb = max(0.0, ondernemer_inkomen - gl)
            vpb = _heffing_over(winst_voor_vpb, p["vpb"]["schijven"])
            ok = p["oprichtingskosten_indicatief"]
            overhead = p["vaste_kosten_indicatief"]["dga"] + ok["dga"] / ok["standaard_horizon_jaren"]
            return (Persoon(loon=loon + gl, eigen_woning=ew, box3=b3, **pk),
                    winst_voor_vpb - vpb, vpb + overhead, loon + gl)
        if naam == "meer_loon":
            return Persoon(loon=loon + ondernemer_inkomen, eigen_woning=ew, box3=b3, **pk), 0.0, 0.0, loon + ondernemer_inkomen
        return (zzp_persoon, 0.0, 0.0, loon + ondernemer_inkomen)

    # Huidige situatie = ondernemersinkomen in de opgegeven vorm (ZZP of bestaande BV).
    cur_naam = huidige_vorm if (ondernemer_inkomen > 0 and huidige_vorm in ("zzp", "bv")) else "zzp"
    cur_persoon, cur_box2, cur_extra, _cur_arb = _operationeel(cur_naam)
    # Uitgekeerd dividend uit eerder opgepot BV-vermogen: extra box 2-inkomen dit jaar.
    cur_box2 += dividend_box2
    base_tax, base_toeslagen, base_netto = _huishouden(
        cur_persoon, partner, profiel, p, inkomen, cur_box2, cur_extra, minst, partner_minst)
    rp = bereken_persoon(cur_persoon, p, box2_inkomen=cur_box2, is_minstverdienende=minst)
    rpp = bereken_persoon(partner, p, is_minstverdienende=partner_minst) if partner else None
    detail = {
        "persoon": _persoon_detail(rp, loon + ondernemer_inkomen, cur_extra),
        "partner": _persoon_detail(rpp, partner_inkomen, 0.0) if rpp else None,
        "toeslagen": base_toeslagen,
        "huishouden": {"te_betalen": base_tax, "netto": base_netto},
    }

    sugg: list[Suggestie] = []

    # 1. Rechtsvorm EERST — bepaalt de route waarop de rest wordt doorgerekend.
    rechtsvorm = None
    beste_naam = "zzp"
    if ondernemer_inkomen > 0:
        mix = bereken_mix(loon, ondernemer_inkomen, jaar, vast_winst=0.0,
                          urencriterium=urencriterium, gebruikelijk_loon=gebruikelijk_loon,
                          eigen_woning=ew, box3=b3, partner_inkomen=partner_inkomen, profiel=profiel)
        beste_naam = mix.beste.naam

        def _bv_wint(oi):
            m = bereken_mix(loon, oi, jaar, vast_winst=0.0, urencriterium=urencriterium,
                            gebruikelijk_loon=gebruikelijk_loon, eigen_woning=ew, box3=b3,
                            partner_inkomen=partner_inkomen, profiel=profiel)
            bv = next(o for o in m.opties if o.naam == "bv")
            zzp = next(o for o in m.opties if o.naam == "zzp")
            return bv.huishouden_netto >= zzp.huishouden_netto

        bv_omslag = None
        for oi in range(30000, 500001, 10000):
            if _bv_wint(oi):
                bv_omslag = oi
                break

        cur_o = next(o for o in mix.opties if o.naam == cur_naam)
        rechtsvorm = {
            "beste": mix.beste.naam, "beste_label": mix.beste.label, "bv_omslag": bv_omslag,
            "huidige_vorm": cur_naam, "huidige_label": cur_o.label,
            "bv_kosten_jaar": p["vaste_kosten_indicatief"]["dga"],
            "bv_oprichting": p["oprichtingskosten_indicatief"]["dga"],
            "gebruikelijk_loon_norm": p["dga"]["gebruikelijk_loon_normbedrag"],
            "opties": [
                {"naam": o.naam, "label": o.label, "huishouden_netto": o.huishouden_netto,
                 "marginaal_tarief": o.marginaal_tarief, "componenten": o.componenten}
                for o in mix.opties
            ],
        }
        voordeel = round(mix.beste.huishouden_netto - cur_o.huishouden_netto, 2)
        if beste_naam != cur_naam and voordeel > 1:
            sugg.append(Suggestie(
                f"Overstappen naar {mix.beste.label} (i.p.v. {cur_o.label})", voordeel,
                f"Bij € {ondernemer_inkomen:,.0f} ondernemersinkomen levert deze vorm netto meer "
                "op (let op eenmalige/jaarlijkse BV-kosten en het 'eigen gebruik'-punt).".replace(",", "."),
                "afd. 3.2 Wet IB 2001 / Wet Vpb 1969"))

    # Operationele situatie = de aanbevolen vorm. De rest wordt HIEROP doorgerekend (consistent).
    op_persoon, op_box2, op_extra, op_arbeidsinkomen = _operationeel(beste_naam)
    op_box2 += dividend_box2  # zelfde uitgekeerde dividend telt ook op de aanbevolen vorm
    op_tax, op_toeslagen, op_netto = _huishouden(
        op_persoon, partner, profiel, p, inkomen, op_box2, op_extra, minst, partner_minst)
    op_label = rechtsvorm["beste_label"] if (rechtsvorm and beste_naam != "zzp") else "je huidige vorm"

    # 1b. KIA — kwantificeer het investeringsaftrek-voordeel (of tip om tot boven de drempel te bundelen).
    if investering > 0 and huidige_vorm != "bv":
        kcfg = p["onderneming"].get("kia", {})
        if kia > 0:
            persoon_zk = dataclasses.replace(
                zzp_persoon, onderneming=_ond(ondernemer_inkomen, urencriterium, starter, meewerk))
            t_zk, _, _ = _huishouden(persoon_zk, partner, profiel, p, inkomen, cur_box2, cur_extra, minst, partner_minst)
            besp_kia = round(t_zk - base_tax, 2)
            if besp_kia > 1:
                in_afbouw = investering > kcfg.get("vast_tot", 1e12)
                sugg.append(Suggestie(
                    f"Investeringsaftrek (KIA) — € {kia:,.0f} extra aftrek".replace(",", "."), besp_kia,
                    f"Over € {investering:,.0f} zakelijke investeringen: € {kia:,.0f} extra aftrek op je winst".replace(",", ".")
                    + (" — je zit in de afbouwzone; investeringen over twee jaar spreiden kan meer opleveren."
                       if in_afbouw else "."),
                    "art. 3.41 Wet IB 2001"))
        elif kcfg and investering <= kcfg["drempel"]:
            drem = kcfg["drempel"]
            sugg.append(Suggestie(
                "Investeringen bundelen tot boven de KIA-drempel",
                round(0.28 * (drem + 1) * 0.33, 2),  # grove schatting: 28% aftrek × ~marginaal na MKB
                f"Je investeert € {investering:,.0f}; onder € {drem + 1:,.0f} krijg je géén KIA. Bundel je net "
                f"boven de drempel, dan is 28% aftrekbaar (± € {round(0.28 * (drem + 1)):,.0f} aftrek).".replace(",", "."),
                "art. 3.41 Wet IB 2001"))

    # 2. Lijfrente-inleg (jaarruimte op de gekozen route) + meerjarige doorrekening.
    jr = jaarruimte(op_arbeidsinkomen, p)
    lijfrente = None
    if jr > 0:
        op_persoon2 = dataclasses.replace(op_persoon, aftrekposten_box1=op_persoon.aftrekposten_box1 + jr)
        t2, ts2, _ = _huishouden(op_persoon2, partner, profiel, p, inkomen, op_box2, op_extra, minst, partner_minst)
        tax_saving = op_tax - t2
        besp = round(tax_saving + (ts2 - op_toeslagen), 2)
        if besp > 1:
            sugg.append(Suggestie(
                f"Lijfrente-inleg tot € {jr:,.0f}".replace(",", "."), besp,
                f"Op de route via {op_label}: aftrekbaar tegen je marginale tarief + lager "
                "toetsingsinkomen (meer toeslagen); kapitaal buiten box 3. Het ingelegde bedrag is "
                "uitgesteld inkomen (belast bij uitkering).",
                "art. 3.127 Wet IB 2001"))
        marg = round(tax_saving / jr, 4) if jr else 0.0
        lj = vergelijk_lijfrente(jr, rendement, horizon, jaar, marginaal_nu=marg,
                                 tarief_uit=0.1785, tegenbewijs=True, partner=(partner is not None))
        lijfrente = {
            "inleg": round(jr, 2), "rendement": rendement, "jaren": horizon,
            "marginaal_nu": marg, "tarief_uit": 0.1785,
            "lijfrente_eindnetto": lj.lijfrente_eindnetto, "prive_eindnetto": lj.prive_eindnetto,
            "voordeel": lj.voordeel, "breakeven_tarief_uit": lj.breakeven_tarief_uit,
        }

    # 2b. Lijfrente-inleg van de PARTNER (eigen, vaak nog onbenutte jaarruimte) — extra optimalisatie.
    if partner and partner_inkomen > 0:
        partner_jr = jaarruimte(partner_inkomen, p)
        if partner_jr > 0:
            partner2 = dataclasses.replace(partner, aftrekposten_box1=partner.aftrekposten_box1 + partner_jr)
            t3, ts3, _ = _huishouden(op_persoon, partner2, profiel, p, inkomen, op_box2, op_extra, minst, partner_minst)
            besp_p = round((op_tax - t3) + (ts3 - op_toeslagen), 2)
            if besp_p > 1:
                sugg.append(Suggestie(
                    f"Lijfrente-inleg partner tot € {partner_jr:,.0f}".replace(",", "."), besp_p,
                    "Je partner heeft eigen, nog onbenutte jaarruimte: aftrekbaar tegen het marginale "
                    "tarief van je partner, kapitaal buiten box 3. Zo benut je huishouden béíde "
                    "jaarruimtes. Wél op naam van je partner (weeg de 'op wiens naam'-vraag mee bij scheiding).",
                    "art. 3.127 Wet IB 2001"))

    # 3. Partnertoerekening eigen woning (op het box 1-inkomen van de gekozen route).
    if partner and (ew.woz_waarde or ew.betaalde_hypotheekrente):
        r = optimale_eigenwoning_verdeling(
            op_arbeidsinkomen, partner_inkomen, ew.woz_waarde, ew.betaalde_hypotheekrente, jaar)
        if r.besparing_vs_5050 > 1:
            sugg.append(Suggestie(
                f"Eigen woning toerekenen ({r.optimale_fractie_partner_a:.0%} bij hoofdverdiener)",
                r.besparing_vs_5050, r.toelichting, "art. 2.17 Wet IB 2001"))

    # 4. Box 3 verdelen over partners (2× heffingvrij) — onafhankelijk van de rechtsvorm.
    if partner and (b3.banktegoeden + b3.overige_bezittingen) > p.box3["heffingvrij_vermogen_pp"]:
        enkel = box3_last(p, spaargeld=b3.banktegoeden, beleggingen=b3.overige_bezittingen,
                          schulden=b3.schulden, partner=False)
        dubbel = box3_last(p, spaargeld=b3.banktegoeden, beleggingen=b3.overige_bezittingen,
                           schulden=b3.schulden, partner=True)
        if enkel - dubbel > 1:
            sugg.append(Suggestie(
                "Box 3 verdelen over beide partners (2× heffingvrij vermogen)",
                round(enkel - dubbel, 2),
                "Fiscale partners benutten samen 2× het heffingvrij vermogen (€ "
                f"{p.box3['heffingvrij_vermogen_pp']:,.0f} p.p.).".replace(",", "."),
                "art. 2.17 / 5.5 Wet IB 2001"))

    # 4b. Partner meewerken in de IB-zaak: meewerkaftrek vs. reële arbeidsbeloning (inkomen verschuiven).
    #     We kennen het partnerinkomen, dus we rekenen de optimale route uit.
    if partner and ondernemer_inkomen > 5000 and huidige_vorm != "bv" and meewerk_uren < 525:
        # Route 1 — meewerkaftrek ~2% (part-time): een aftrek voor jou, geen betaling.
        p_mw = dataclasses.replace(
            zzp_persoon, onderneming=_ond(ondernemer_inkomen, urencriterium, starter, meewerk + round(0.02 * ondernemer_inkomen, 2)))
        besp_mw = round(base_tax - _huishouden(p_mw, partner, profiel, p, inkomen, 0.0, 0.0, minst, partner_minst)[0], 2)
        # Route 2 — reële arbeidsbeloning: zoek het bedrag X (winst − X bij jou, +X box 1 bij partner) dat het meest bespaart.
        best_x, besp_ab = 0, 0.0
        for x in range(5000, min(int(ondernemer_inkomen), 40000) + 1, 2500):
            p_ond = dataclasses.replace(zzp_persoon, onderneming=_ond(ondernemer_inkomen - x, urencriterium, starter, meewerk))
            p_par = dataclasses.replace(partner, loon=partner_inkomen + x)
            s = base_tax - _huishouden(p_ond, p_par, profiel, p, inkomen, 0.0, 0.0, minst, partner_minst)[0]
            if s > besp_ab:
                besp_ab, best_x = s, x
        if max(besp_mw, besp_ab) > 1:
            if besp_ab >= besp_mw:
                sugg.append(Suggestie(
                    f"Partner een arbeidsbeloning geven (± € {best_x:,.0f})".replace(",", "."),
                    round(besp_ab, 2),
                    f"Je partner verdient nu € {partner_inkomen:,.0f}. Een reële arbeidsbeloning van ± € {best_x:,.0f} "
                    f"verschuift inkomen van jouw toptarief naar de lagere schijven van je partner → ≈ € {besp_ab:,.0f} "
                    "besparing. Voorwaarde: je partner werkt daadwerkelijk voor dat bedrag mee (≥ € 5.000, reëel — anders "
                    f"niet aftrekbaar). Simpeler alternatief zonder betaling: meewerkaftrek (≈ € {besp_mw:,.0f}).".replace(",", "."),
                    "art. 3.16 Wet IB 2001"))
            else:
                sugg.append(Suggestie(
                    "Partner laten meewerken in je zaak (meewerkaftrek)",
                    besp_mw,
                    "Werkt je fiscale partner ≥ 525 u/jaar mee (zonder loon ≥ € 5.000)? Dan is 1,25–4% van je "
                    f"winst aftrekbaar — bij ~part-time (2%) ≈ € {besp_mw:,.0f}. Vul de meewerk-uren in voor je eigen "
                    "situatie. Een reële arbeidsbeloning levert hier minder op (je partner heeft al inkomen).".replace(",", "."),
                    "art. 3.78 Wet IB 2001"))

    # 5. Vermogen: box 3-last nu (op het TOTALE box 3-vermogen) + BV-uitstel voor de beleggingen.
    vermogen = None
    beleggingen = b3.overige_bezittingen
    spaargeld = b3.banktegoeden
    if beleggingen + spaargeld > 0:
        box3_nu = box3_last(p, spaargeld=spaargeld, beleggingen=beleggingen,
                            schulden=b3.schulden, partner=(partner is not None),
                            werkelijk_rendement=rendement)
        u = vergelijk_uitstel(beleggingen, rendement, horizon, jaar,
                              tegenbewijs=True, partner=(partner is not None)) if beleggingen > 0 else None
        vermogen = {
            "spaargeld": spaargeld, "beleggingen": beleggingen, "schulden": b3.schulden,
            "totaal": round(spaargeld + beleggingen - b3.schulden, 2), "box3_belasting_nu": round(box3_nu, 2),
            "rendement": rendement, "horizon": horizon,
            "heffingvrij": p.box3["heffingvrij_vermogen_pp"] * (2 if partner is not None else 1),
            "bv_eindnetto": u.bv_eindnetto if u else None,
            "prive_eindnetto": u.prive_eindnetto if u else None,
            "beste": u.beste if u else None, "omslag_rendement": u.omslag_rendement if u else None,
        }

    sugg.sort(key=lambda s: -s.besparing)
    return AdviesResultaat(jaar, base_tax, base_toeslagen, base_netto, sugg,
                           rechtsvorm=rechtsvorm, vermogen=vermogen, lijfrente=lijfrente,
                           detail=detail)
